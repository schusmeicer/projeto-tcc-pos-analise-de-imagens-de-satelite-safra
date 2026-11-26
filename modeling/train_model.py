import pandas as pd
import os
import numpy as np
import mlflow
import mlflow.sklearn
import optuna
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from hybrid_model import HybridDetrendingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
import warnings

# Ignorar alguns avisos do pandas
warnings.filterwarnings('ignore')

def treinar_e_comparar_modelos():
    """
    Este script carrega o dataset unificado, separa os dados usando o método Out-of-Time
    (Passado vs Futuro) e compara múltiplos algoritmos para prever o Rendimento Médio (kg/ha).
    """
    print("\n" + "="*80)
    print(f"{'Iniciando Validação Out-of-Time e Comparação de Modelos':^80}")
    print("="*80 + "\n")
    
    # ---------------------------------------------------------
    # MLFLOW: CONFIGURAÇÃO DO EXPERIMENTO
    # ---------------------------------------------------------
    # Forçar o MLflow a salvar em pastas normais ao invés de banco de dados SQLite
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("Previsao_Soja_MT")
    
    # ---------------------------------------------------------
    # PASSO 1: Carregar o Dataset
    # ---------------------------------------------------------
    dataset_path = os.path.join('data', 'dataset_final_soja_mt.csv')
    
    if not os.path.exists(dataset_path):
        print(f"[ERRO] O arquivo {dataset_path} não existe. Execute o 'merge_datasets.py' primeiro.")
        return
        
    df = pd.read_csv(dataset_path, sep=';', decimal=',')
    print(f"Dataset carregado com {len(df)} registros válidos.")

    # ---------------------------------------------------------
    # PASSO 2: Separação Out-of-Time (OOT)
    # ---------------------------------------------------------
    # Ao invés de sortear dados aleatórios, vamos treinar com o PASSADO e testar com o FUTURO
    # Isso evita "Data Leakage" (Vazamento de Dados) e simula o mundo real
    ano_corte = 2021
    
    df_train = df[df['ano'] <= ano_corte]
    df_test = df[df['ano'] > ano_corte]
    
    print(f"Separação Temporal (Corte após a Safra {ano_corte}/{ano_corte+1}):")
    print(f"- Base de Treino ({df_train['ano'].min()} a {df_train['ano'].max()}): {len(df_train)} registros")
    print(f"- Base de Teste ({df_test['ano'].min()} a {df_test['ano'].max()}): {len(df_test)} registros\n")

    # Definir variáveis
    variaveis = ['NDVI', 'EVI', 'LST_Day_1km', 'pr', 'def', 'tmean', 'soil']
    features_satelite = [f"{var}_j1" for var in variaveis] + [f"{var}_j2" for var in variaveis]
    features = ['ano', 'area_plantada_hectares'] + features_satelite
    target = 'rendimento_medio_kg_ha'
    
    X_train = df_train[features]
    y_train = df_train[target]
    
    X_test = df_test[features]
    y_test = df_test[target]

    # ---------------------------------------------------------
    # PASSO 3: Otimização Bayesiana com Optuna
    # ---------------------------------------------------------
    optuna.logging.set_verbosity(optuna.logging.WARNING) # Evita spam no terminal

    resultados = []

    print("Treinando, otimizando hiperparâmetros via Optuna e extraindo métricas de erro...\n")

    # 1. Regressão Linear Múltipla (Baseline, sem hiperparâmetros)
    print("[Regressão Linear Múltipla] Iniciando treinamento...")
    with mlflow.start_run(run_name="Regressão Linear Múltipla"):
        modelo_lr = LinearRegression()
        modelo_lr.fit(X_train, y_train)
        print("  -> Treinamento padrão concluído.")
        
        previsoes_teste = modelo_lr.predict(X_test)
        mean_y_train = y_train.mean()
        ss_res = np.sum((y_test - previsoes_teste) ** 2)
        ss_tot_oos = np.sum((y_test - mean_y_train) ** 2)
        r2 = 1 - (ss_res / ss_tot_oos)
        rmse = np.sqrt(mean_squared_error(y_test, previsoes_teste))
        mae = mean_absolute_error(y_test, previsoes_teste)
        mape = mean_absolute_percentage_error(y_test, previsoes_teste) * 100
        wmape = (np.sum(np.abs(y_test - previsoes_teste)) / np.sum(np.abs(y_test))) * 100
        
        mlflow.log_metric("R2", r2)
        mlflow.log_metric("RMSE", rmse)
        mlflow.log_metric("MAE", mae)
        mlflow.log_metric("MAPE", mape)
        mlflow.log_metric("WMAPE", wmape)
        mlflow.sklearn.log_model(modelo_lr, "model")
        
        # Salva as previsões na base completa (treino + teste)
        df['prev_Regressão Linear Múltipla'] = modelo_lr.predict(df[features])
        
        resultados.append({
            'Modelo': "Regressão Linear Múltipla",
            'R²': r2, 'RMSE': rmse, 'MAE': mae, 'MAPE (%)': mape, 'WMAPE (%)': wmape
        })

    # Função Helper para processar e avaliar as Árvores com Optuna
    def otimizar_e_avaliar(nome_modelo, get_model_func, n_trials=20):
        print(f"[{nome_modelo}] Iniciando Otimização Optuna com {n_trials} trials...")
        with mlflow.start_run(run_name=nome_modelo):
            
            def objective(trial):
                modelo = get_model_func(trial)
                # Cross-validation no grupo de treino com 3 folds (evita vazamento do teste)
                score = cross_val_score(modelo, X_train, y_train, cv=3, scoring='neg_mean_absolute_error', n_jobs=-1)
                return score.mean() # Retorna o MAE negativo médio
            
            study = optuna.create_study(direction="maximize") # Queremos maximizar o neg_mean_absolute_error (que é negativo)
            study.optimize(objective, n_trials=n_trials)
            
            print(f"  -> Melhores parâmetros encontrados: {study.best_params}")
            mlflow.log_params(study.best_params)
            
            # Treinar o modelo final com os melhores parâmetros
            modelo_final = get_model_func(optuna.trial.FixedTrial(study.best_params))
            modelo_final.fit(X_train, y_train)
            
            # Avaliar no conjunto de teste Out-of-Time
            previsoes_teste = modelo_final.predict(X_test)
            mean_y_train = y_train.mean()
            ss_res = np.sum((y_test - previsoes_teste) ** 2)
            ss_tot_oos = np.sum((y_test - mean_y_train) ** 2)
            r2 = 1 - (ss_res / ss_tot_oos)
            rmse = np.sqrt(mean_squared_error(y_test, previsoes_teste))
            mae = mean_absolute_error(y_test, previsoes_teste)
            mape = mean_absolute_percentage_error(y_test, previsoes_teste) * 100
            wmape = (np.sum(np.abs(y_test - previsoes_teste)) / np.sum(np.abs(y_test))) * 100
            
            mlflow.log_metric("R2", r2)
            mlflow.log_metric("RMSE", rmse)
            mlflow.log_metric("MAE", mae)
            mlflow.log_metric("MAPE", mape)
            mlflow.log_metric("WMAPE", wmape)
            mlflow.sklearn.log_model(modelo_final, "model")
            
            # Salva as previsões na base completa (treino + teste)
            df[f'prev_{nome_modelo}'] = modelo_final.predict(df[features])
            
            resultados.append({
                'Modelo': nome_modelo,
                'R²': r2, 'RMSE': rmse, 'MAE': mae, 'MAPE (%)': mape, 'WMAPE (%)': wmape
            })

    # 2. Híbrido: Random Forest Regressor
    def get_rf(trial):
        base_rf = RandomForestRegressor(
            random_state=42,
            n_estimators=trial.suggest_int("n_estimators", 50, 300, step=50),
            max_depth=trial.suggest_int("max_depth", 3, 15),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 15)
        )
        return HybridDetrendingRegressor(base_estimator=base_rf)
    otimizar_e_avaliar("Híbrido: Random Forest", get_rf, n_trials=20)

    # 3. Híbrido: Gradient Boosting Regressor
    def get_gbm(trial):
        base_gbm = GradientBoostingRegressor(
            random_state=42,
            n_estimators=trial.suggest_int("n_estimators", 50, 200, step=50),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            max_depth=trial.suggest_int("max_depth", 3, 10)
        )
        return HybridDetrendingRegressor(base_estimator=base_gbm)
    otimizar_e_avaliar("Híbrido: Gradient Boosting", get_gbm, n_trials=20)

    # 4. Híbrido: XGBoost Regressor
    def get_xgb(trial):
        base_xgb = XGBRegressor(
            random_state=42,
            n_estimators=trial.suggest_int("n_estimators", 50, 200, step=50),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            max_depth=trial.suggest_int("max_depth", 3, 10)
        )
        return HybridDetrendingRegressor(base_estimator=base_xgb)
    otimizar_e_avaliar("Híbrido: XGBoost", get_xgb, n_trials=20)

    # ---------------------------------------------------------
    # PASSO 4: Salvar a base de dados com as previsões
    # ---------------------------------------------------------
    path_previsoes = os.path.join('data', 'dataset_com_previsoes.csv')
    df.to_csv(path_previsoes, sep=';', decimal=',', index=False)
    print(f"\n[SUCESSO] Base de dados salva com todas as previsões em: {path_previsoes}")

    # ---------------------------------------------------------
    # PASSO 5: Imprimir a Tabela Comparativa Final
    # ---------------------------------------------------------
    df_resultados = pd.DataFrame(resultados)
    
    print("="*95)
    print(f"{'Quadro Comparativo de Desempenho no Teste Out-of-Time':^95}")
    print("="*95)
    
    # Formatação de string para criar a tabela de forma limpa
    header = f"{'Modelo':<30} | {'R²':>8} | {'RMSE':>8} | {'MAE':>8} | {'MAPE':>8} | {'WMAPE':>8}"
    print(header)
    print("-" * 95)
    
    for idx, row in df_resultados.iterrows():
        print(f"{row['Modelo']:<30} | {row['R²']:>8.4f} | {row['RMSE']:>8.2f} | {row['MAE']:>8.2f} | {row['MAPE (%)']:>7.2f}% | {row['WMAPE (%)']:>7.2f}%")
        
    print("="*95)
    print("\n[!] Dica para o TCC: Compare o WMAPE (Erro Percentual Absoluto Ponderado) entre os modelos.")
    print("O modelo com o menor WMAPE e MAE é o mais recomendado para estimar a produtividade (kg/ha).")
    print("Se a Regressão Linear for pior que as árvores (RF/GBM), isso prova que a relação")
    print("entre NDVI/EVI e produtividade não é uma reta simples, justificando o uso de Machine Learning!")

if __name__ == '__main__':
    treinar_e_comparar_modelos()
