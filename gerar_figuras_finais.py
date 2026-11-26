import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from scipy.stats import spearmanr
from modeling.hybrid_model import HybridDetrendingRegressor

def generate_tcc_figures():
    print("Iniciando a geracao das figuras para o TCC...")
    
    # 1. Setup paths
    out_dir = os.path.join(os.getcwd(), 'figuras_tcc')
    os.makedirs(out_dir, exist_ok=True)
    
    dataset_path = os.path.join('data', 'dataset_final_soja_mt.csv')
    df = pd.read_csv(dataset_path, sep=';', decimal=',')
    
    # 2. Features and Target
    features_satelite = ['NDVI_j1', 'NDVI_j2', 'EVI_j1', 'EVI_j2', 'LST_Day_1km_j1', 'LST_Day_1km_j2', 
                         'pr_j1', 'pr_j2', 'def_j1', 'def_j2', 'tmean_j1', 'tmean_j2', 'soil_j1', 'soil_j2']
    features = ['ano', 'area_plantada_hectares'] + features_satelite
    target = 'rendimento_medio_kg_ha'
    
    # Train / Test Split OOT
    df_train = df[df['ano'] <= 2021]
    df_test = df[df['ano'] > 2021]
    
    X_train = df_train[features]
    y_train = df_train[target]
    X_test = df_test[features]
    y_test = df_test[target]
    
    # 3. Models
    modelos = {
        "Regressao Linear": LinearRegression(),
        "Random Forest Hibrido": HybridDetrendingRegressor(RandomForestRegressor(n_estimators=300, max_depth=15, min_samples_split=2, random_state=42, n_jobs=-1)),
        "GBM Hibrido": HybridDetrendingRegressor(GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=5, random_state=42)),
        "XGBoost Hibrido": HybridDetrendingRegressor(XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42, n_jobs=-1))
    }
    
    preds_test = {}
    preds_all = {}
    
    for name, model in modelos.items():
        model.fit(X_train, y_train)
        preds_test[name] = model.predict(X_test)
        preds_all[name] = model.predict(df[features])

    # 4. FIGURA 1: Comparacao temporal do rendimento real vs previsto pelos 4 modelos
    print("Gerando Figura 1...")
    plt.figure(figsize=(14, 7))
    
    df_agg = df.groupby('ano').agg({'rendimento_medio_kg_ha': 'mean'}).reset_index()
    anos = df_agg['ano']
    y_real = df_agg['rendimento_medio_kg_ha']
    
    plt.plot(anos, y_real, marker='o', linewidth=3, color='black', label='Real (IBGE)')
    
    colors = ['blue', 'green', 'orange', 'red']
    for (name, _), color in zip(modelos.items(), colors):
        df_temp = df.copy()
        df_temp['pred'] = preds_all[name]
        y_pred = df_temp.groupby('ano')['pred'].mean()
        plt.plot(anos, y_pred, linestyle='--', linewidth=2, color=color, label=f'Previsto ({name})')
        
    plt.axvline(x=2021.5, color='red', linestyle=':', linewidth=2, label='Fronteira Treino/Teste OOT')
    
    plt.title('Figura 1 - Rendimento Real vs. Previsto por todos os modelos (2008-2024)', fontsize=14)
    plt.xlabel('Ano')
    plt.ylabel('Rendimento Médio (kg/ha)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'comparativo_temporal_modelos.png'), dpi=300)
    plt.close()
    
    # 5. FIGURA 2: Serie temporal ponderada (apenas XGBoost Hibrido)
    print("Gerando Figura 2...")
    df_temp = df.copy()
    df_temp['pred'] = preds_all['XGBoost Hibrido']
    df_temp['prod_real'] = df_temp['rendimento_medio_kg_ha'] * df_temp['area_plantada_hectares']
    df_temp['prod_pred'] = df_temp['pred'] * df_temp['area_plantada_hectares']
    
    df_agg2 = df_temp.groupby('ano').agg({
        'prod_real': 'sum',
        'prod_pred': 'sum',
        'area_plantada_hectares': 'sum'
    }).reset_index()
    
    df_agg2['rend_real'] = df_agg2['prod_real'] / df_agg2['area_plantada_hectares']
    df_agg2['rend_pred'] = df_agg2['prod_pred'] / df_agg2['area_plantada_hectares']
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_agg2['ano'], df_agg2['rend_real'], marker='o', linewidth=3, label='Real (IBGE)')
    plt.plot(df_agg2['ano'], df_agg2['rend_pred'], marker='s', linestyle='--', linewidth=2, label='Previsto (XGBoost Híbrido)')
    plt.axvline(x=2021.5, color='red', linestyle=':')
    plt.title('Figura 2 - Série Temporal de Rendimento da Soja no MT (Real vs XGBoost Híbrido)', fontsize=14)
    plt.xlabel('Ano da Safra')
    plt.ylabel('Rendimento Médio Ponderado (kg/ha)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'serie_temporal_safra.png'), dpi=300)
    plt.close()
    
    # 6. FIGURA 3: Real vs Previsto Scatter Plot (Teste)
    print("Gerando Figura 3...")
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, preds_test['XGBoost Hibrido'], alpha=0.6, color='purple', edgecolors='w')
    
    min_val = min(y_test.min(), preds_test['XGBoost Hibrido'].min())
    max_val = max(y_test.max(), preds_test['XGBoost Hibrido'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Y = X')
    
    plt.title('Figura 3 - Real vs Previsto (Validação OOT 2022-2024)', fontsize=14)
    plt.xlabel('Rendimento Real (kg/ha)')
    plt.ylabel('Rendimento Previsto (XGBoost Híbrido)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'real_vs_previsto.png'), dpi=300)
    plt.close()
    
    # 7. FIGURA 4: Heterocedasticidade
    print("Gerando Figura 4...")
    residuals = y_test - preds_test['XGBoost Hibrido']
    
    plt.figure(figsize=(8, 6))
    plt.scatter(preds_test['XGBoost Hibrido'], residuals, alpha=0.6, color='steelblue', edgecolors='w')
    plt.axhline(y=0, color='r', linestyle='--', lw=2)
    plt.title('Figura 4 - Resíduos vs Previstos (Teste de Heterocedasticidade)', fontsize=14)
    plt.xlabel('Rendimento Previsto (kg/ha)')
    plt.ylabel('Resíduos (kg/ha)')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'heterocedasticity_scatter_plot.png'), dpi=300)
    plt.close()
    
    # Spearman test print
    rho, pval = spearmanr(preds_test['XGBoost Hibrido'], np.abs(residuals))
    print(f"Spearman correlation: rho={rho:.4f}, pval={pval:.4f}")
    
    # 8. SHAP Integrado (Painel 2x2 em Português)
    print("Gerando Painel Integrado SHAP (Figura 5)...")
    feature_names_pt = {
        'ano': 'Ano da Safra',
        'area_plantada_hectares': 'Área Plantada (ha)',
        'NDVI_j1': 'NDVI (J1 - Vegetativo)',
        'NDVI_j2': 'NDVI (J2 - Reprodutivo)',
        'EVI_j1': 'EVI (J1 - Vegetativo)',
        'EVI_j2': 'EVI (J2 - Reprodutivo)',
        'LST_Day_1km_j1': 'Temp. Superfície J1 (°C)',
        'LST_Day_1km_j2': 'Temp. Superfície J2 (°C)',
        'pr_j1': 'Precipitação J1 (mm)',
        'pr_j2': 'Precipitação J2 (mm)',
        'def_j1': 'Déficit Hídrico J1 (mm)',
        'def_j2': 'Déficit Hídrico J2 (mm)',
        'tmean_j1': 'Temp. Média Ar J1 (°C)',
        'tmean_j2': 'Temp. Média Ar J2 (°C)',
        'soil_j1': 'Umidade Solo J1 (mm)',
        'soil_j2': 'Umidade Solo J2 (mm)'
    }
    
    X_train_pt = X_train.rename(columns=feature_names_pt)
    shap_model = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=4, random_state=42, n_jobs=-1)
    shap_model.fit(X_train_pt, y_train)
    
    X_sample = X_train_pt.sample(n=min(1500, len(X_train_pt)), random_state=42)
    explainer = shap.TreeExplainer(shap_model)
    shap_values = explainer.shap_values(X_sample)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    plt.subplots_adjust(wspace=0.35, hspace=0.35)
    
    # Subplot (A): Beeswarm
    plt.sca(axes[0, 0])
    shap.summary_plot(shap_values, X_sample, max_display=8, show=False, plot_size=None)
    axes[0, 0].set_title('(A) Importância Global das Variáveis (Beeswarm)', fontsize=12, fontweight='bold', pad=10)
    axes[0, 0].set_xlabel('Valor SHAP (Impacto na Produtividade em kg/ha)', fontsize=10)
    
    for ax in fig.axes:
        if 'Feature value' in ax.get_ylabel():
            ax.set_ylabel('Valor da Variável', fontsize=10)
            ticks = ax.get_yticks()
            if len(ticks) >= 2:
                ax.set_yticks([ticks[0], ticks[-1]])
                ax.set_yticklabels(['Baixo', 'Alto'], fontsize=9)
                
    # Subplot (B): def_j2
    plt.sca(axes[0, 1])
    shap.dependence_plot('Déficit Hídrico J2 (mm)', shap_values, X_sample, ax=axes[0, 1], show=False, interaction_index=None)
    axes[0, 1].set_title('(B) Dependência: Déficit Hídrico na J2', fontsize=12, fontweight='bold', pad=10)
    axes[0, 1].set_xlabel('Déficit Hídrico J2 (mm)', fontsize=10)
    axes[0, 1].set_ylabel('Valor SHAP (kg/ha)', fontsize=10)
    axes[0, 1].axhline(0, color='gray', linestyle='--', alpha=0.6)
    axes[0, 1].grid(alpha=0.25)
    
    # Subplot (C): tmean_j2
    plt.sca(axes[1, 0])
    shap.dependence_plot('Temp. Média Ar J2 (°C)', shap_values, X_sample, ax=axes[1, 0], show=False, interaction_index=None)
    axes[1, 0].set_title('(C) Dependência: Temperatura Média na J2', fontsize=12, fontweight='bold', pad=10)
    axes[1, 0].set_xlabel('Temperatura Média J2 (°C)', fontsize=10)
    axes[1, 0].set_ylabel('Valor SHAP (kg/ha)', fontsize=10)
    axes[1, 0].axhline(0, color='gray', linestyle='--', alpha=0.6)
    axes[1, 0].grid(alpha=0.25)
    
    # Subplot (D): ano
    plt.sca(axes[1, 1])
    shap.dependence_plot('Ano da Safra', shap_values, X_sample, ax=axes[1, 1], show=False, interaction_index=None)
    axes[1, 1].set_title('(D) Dependência: Tendência Temporal (Ano)', fontsize=12, fontweight='bold', pad=10)
    axes[1, 1].set_xlabel('Ano da Safra', fontsize=10)
    axes[1, 1].set_ylabel('Valor SHAP (kg/ha)', fontsize=10)
    axes[1, 1].axhline(0, color='gray', linestyle='--', alpha=0.6)
    axes[1, 1].grid(alpha=0.25)
    
    plt.tight_layout()
    out_path = os.path.join(out_dir, 'painel_shap_integrado.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Painel integrado salvo com sucesso em: {out_path}")

if __name__ == "__main__":
    generate_tcc_figures()
