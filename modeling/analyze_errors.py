import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from hybrid_model import HybridDetrendingRegressor
import warnings

warnings.filterwarnings('ignore')

def analyze_worst_errors():
    dataset_path = os.path.join('data', 'dataset_final_soja_mt.csv')
    df = pd.read_csv(dataset_path, sep=';', decimal=',')
    
    # 1. Separação OOT
    ano_corte = 2021
    df_train = df[df['ano'] <= ano_corte]
    df_test = df[df['ano'] > ano_corte].copy()
    
    features_satelite = ['NDVI_j1', 'NDVI_j2', 'EVI_j1', 'EVI_j2', 'LST_Day_1km_j1', 'LST_Day_1km_j2', 
                         'pr_j1', 'pr_j2', 'def_j1', 'def_j2', 'tmean_j1', 'tmean_j2', 'soil_j1', 'soil_j2']
    features = ['ano', 'area_plantada_hectares'] + features_satelite
    target = 'rendimento_medio_kg_ha'
    
    X_train = df_train[features]
    y_train = df_train[target]
    X_test = df_test[features]
    y_test = df_test[target]
    
    # 2. Treinar o modelo campeão (Híbrido XGBoost)
    # Melhores parms do log: n_estimators=150, learning_rate=0.0635, max_depth=5
    base_xgb = XGBRegressor(n_estimators=150, learning_rate=0.0635, max_depth=5, random_state=42)
    modelo = HybridDetrendingRegressor(base_estimator=base_xgb)
    modelo.fit(X_train, y_train)
    
    # 3. Prever no Teste (2022 e 2023)
    df_test['Previsto'] = modelo.predict(X_test)
    df_test['Real'] = y_test
    
    # 4. Calcular Erros
    # O R2 odeia o erro quadrático, então vamos calcular exatamente ele
    df_test['Erro_Absoluto (kg/ha)'] = np.abs(df_test['Real'] - df_test['Previsto'])
    df_test['Erro_Quadratico'] = (df_test['Real'] - df_test['Previsto']) ** 2
    
    # Ordenar pelas piores previsões (maior erro quadrático)
    df_erros = df_test.sort_values(by='Erro_Quadratico', ascending=False)
    
    top_worst = df_erros[['ano', 'nome_municipio', 'Real', 'Previsto', 'Erro_Absoluto (kg/ha)', 'Erro_Quadratico']].head(15)
    
    print("\n" + "="*80)
    print(" TOP 15 MAIORES ERROS DO MODELO HÍBRIDO (XGBOOST) NO TESTE (2022-2023)")
    print(" (Estes são os 'vilões' que negativaram o R²!)")
    print("="*80)
    print(top_worst.to_string(index=False, float_format='%.2f'))
    print("="*80 + "\n")
    
    # 5. Gerar Gráfico dos Maiores Erros
    plt.figure(figsize=(14, 8))
    
    # Criar um label único para o eixo X
    top_worst['label'] = top_worst['nome_municipio'] + " (" + top_worst['ano'].astype(str) + ")"
    
    x = np.arange(len(top_worst))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    rects1 = ax.bar(x - width/2, top_worst['Real'], width, label='Produção Real', color='#2ca02c')
    rects2 = ax.bar(x + width/2, top_worst['Previsto'], width, label='Previsão do Modelo', color='#d62728')
    
    ax.set_ylabel('Rendimento (kg/ha)', fontsize=12)
    ax.set_title('Top 15 Maiores Erros de Previsão do Modelo Híbrido (Safra 22/23)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(top_worst['label'], rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    
    os.makedirs('outputs', exist_ok=True)
    path_plot = os.path.join('outputs', 'analise_erros_outliers.png')
    plt.savefig(path_plot, dpi=300)
    plt.close()
    
    print(f"[!] Gráfico salvo em: {path_plot}")

if __name__ == '__main__':
    analyze_worst_errors()
