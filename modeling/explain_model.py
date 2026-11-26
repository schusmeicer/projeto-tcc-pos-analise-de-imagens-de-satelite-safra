import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import os
from sklearn.ensemble import RandomForestRegressor
from hybrid_model import HybridDetrendingRegressor
import warnings

warnings.filterwarnings('ignore')

def gerar_explicabilidade():
    print("="*80)
    print(f"{'GERANDO ANÁLISE DE EXPLICABILIDADE COM SHAP':^80}")
    print("="*80 + "\n")
    
    dataset_path = os.path.join('data', 'dataset_final_soja_mt.csv')
    if not os.path.exists(dataset_path):
        print(f"[ERRO] {dataset_path} não encontrado.")
        return

    df = pd.read_csv(dataset_path, sep=';', decimal=',')
    
    features_satelite = ['NDVI_j1', 'NDVI_j2', 'EVI_j1', 'EVI_j2', 'LST_Day_1km_j1', 'LST_Day_1km_j2', 
                         'pr_j1', 'pr_j2', 'def_j1', 'def_j2', 'tmean_j1', 'tmean_j2', 'soil_j1', 'soil_j2']
    features = ['ano', 'area_plantada_hectares'] + features_satelite
    target = 'rendimento_medio_kg_ha'
    
    X = df[features]
    y = df[target]
    
    print("Treinando o modelo Random Forest Híbrido para extração do SHAP...")
    base_rf = RandomForestRegressor(n_estimators=150, max_depth=5, min_samples_split=4, random_state=42, n_jobs=-1)
    modelo = HybridDetrendingRegressor(base_estimator=base_rf)
    modelo.fit(X, y)
    
    print("Calculando os valores SHAP (isso pode demorar um pouco)...")
    # Usa um sample menor se o dataset for muito grande para agilizar o cálculo visual
    X_sample = X.sample(n=min(2000, len(X)), random_state=42)
    
    # Explicaremos a Árvore (base_estimator) que está prestando o serviço não-linear (clima)
    explainer = shap.TreeExplainer(modelo.base_estimator)
    shap_values = explainer.shap_values(X_sample)
    
    print("Gerando gráficos...")
    
    # 1. Gráfico de Resumo (Beeswarm)
    plt.figure(figsize=(12, 10))
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.title('Importância e Impacto das Variáveis (SHAP Beeswarm)', fontsize=16)
    plt.tight_layout()
    path_summary = os.path.join('outputs', 'shap_summary.png')
    plt.savefig(path_summary, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Gráfico Beeswarm salvo em: {path_summary}")
    
    # 2. Gráfico de Barras (Importância Média Absoluta)
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False, color='#1f77b4')
    plt.title('Importância das Variáveis (SHAP Feature Importance)', fontsize=16)
    plt.tight_layout()
    path_bar = os.path.join('outputs', 'shap_importance_bar.png')
    plt.savefig(path_bar, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Gráfico de Barras salvo em: {path_bar}")
    
    # 3. Gráficos de Dependência (Dependence Plots)
    # Mostram como a variação de uma feature específica impacta o modelo e sua interação com outra feature
    top_features = ['ano', 'tmean_j2', 'def_j2']
    print(f"Gerando gráficos de dependência para: {top_features}")
    
    for feature in top_features:
        if feature in X_sample.columns:
            plt.figure(figsize=(10, 6))
            shap.dependence_plot(feature, shap_values, X_sample, show=False)
            plt.title(f'SHAP Dependence Plot: {feature}', fontsize=14)
            plt.tight_layout()
            path_dep = os.path.join('outputs', f'shap_dependence_{feature}.png')
            plt.savefig(path_dep, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"-> Gráfico de Dependência para {feature} salvo em: {path_dep}")
    
    print("\n[SUCESSO] Análise de explicabilidade gerada!")
    print("DICA: Observe quais variáveis (e em quais janelas - J1 ou J2) tiveram maior impacto na mudança do rendimento.")

if __name__ == '__main__':
    gerar_explicabilidade()
