import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import os
import warnings

warnings.filterwarnings('ignore')

def gerar_graficos():
    print("Gerando gráficos de análise...")
    
    # Configuração de estilo do Seaborn
    sns.set_theme(style="whitegrid")
    
    # ---------------------------------------------------------
    # 1. GRÁFICO REAL VS PREVISTO (Base de Teste Out-of-Time)
    # ---------------------------------------------------------
    dataset_path = os.path.join('data', 'dataset_com_previsoes.csv')
    
    if not os.path.exists(dataset_path):
        print(f"[ERRO] {dataset_path} não encontrado. Execute 'train_model.py' primeiro para gerar as previsões.")
        return
        
    df = pd.read_csv(dataset_path, sep=';', decimal=',')

    
    ano_corte = 2021
    df_train = df[df['ano'] <= ano_corte]
    df_test = df[df['ano'] > ano_corte]
    
    features_satelite = ['NDVI_j1', 'NDVI_j2', 'EVI_j1', 'EVI_j2', 'LST_Day_1km_j1', 'LST_Day_1km_j2', 
                         'pr_j1', 'pr_j2', 'def_j1', 'def_j2', 'tmean_j1', 'tmean_j2', 'soil_j1', 'soil_j2']
    features = ['ano', 'area_plantada_hectares'] + features_satelite
    target = 'rendimento_medio_kg_ha'
    
    X_test = df_test[features]
    y_test = df_test[target]
    
    # Utiliza as previsões do modelo Híbrido: Random Forest geradas previamente
    nome_modelo_escolhido = 'Híbrido: Random Forest'
    coluna_prev = f'prev_{nome_modelo_escolhido}'
    
    if coluna_prev not in df_test.columns:
        print(f"[ERRO] A coluna '{coluna_prev}' não foi encontrada no dataset. Execute o 'train_model.py'.")
        return
        
    previsoes = df_test[coluna_prev]
    

    plt.figure(figsize=(10, 8))
    plt.scatter(y_test, previsoes, alpha=0.6, color='#2ca02c', edgecolors='w', s=80)
    
    # Linha de perfeição (y=x)
    min_val = min(y_test.min(), previsoes.min())
    max_val = max(y_test.max(), previsoes.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Previsão Perfeita')
    
    plt.title('Real vs Previsto: Rendimento de Soja (Teste OOT: 2022-2023)', fontsize=16, fontweight='bold')
    plt.xlabel('Rendimento Real (kg/ha)', fontsize=14)
    plt.ylabel('Rendimento Previsto pelo Modelo (kg/ha)', fontsize=14)
    plt.legend(fontsize=12)
    plt.tight_layout()
    
    path_real_previsto = os.path.abspath(os.path.join('outputs', 'real_vs_previsto.png'))
    plt.savefig(path_real_previsto, dpi=300)
    plt.close()
    print(f"Gráfico 'Real vs Previsto' salvo em: {path_real_previsto}")

    # ---------------------------------------------------------
    # 2. GRÁFICO FORECAST 2024 (Top Municípios)
    # ---------------------------------------------------------
    previsao_path = os.path.join('data', 'previsao_safra_2024_mt.csv')
    df_2024 = pd.read_csv(previsao_path, sep=';', decimal=',')
    
    # Pegar os top 15 municípios com maior previsão de rendimento
    top_15 = df_2024.sort_values('previsao_rendimento_kg_ha', ascending=False).head(15)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(
        x='previsao_rendimento_kg_ha', 
        y='nome_municipio', 
        data=top_15, 
        palette='viridis'
    )
    
    plt.title('Forecast 2024/2025: Top 15 Municípios (Rendimento Previsto kg/ha)', fontsize=16, fontweight='bold')
    plt.xlabel('Rendimento Previsto (kg/ha)', fontsize=14)
    plt.ylabel('Município', fontsize=14)
    
    # Adicionar os valores nas barras
    for index, value in enumerate(top_15['previsao_rendimento_kg_ha']):
        plt.text(value + 10, index, f'{value:.0f}', va='center', fontsize=11)
        
    plt.xlim(3000, 3900) # Ajustar limite para destacar as diferenças
    plt.tight_layout()
    
    path_forecast = os.path.abspath(os.path.join('outputs', 'forecast_2024.png'))
    plt.savefig(path_forecast, dpi=300)
    plt.close()
    print(f"Gráfico 'Forecast 2024' salvo em: {path_forecast}")

    # ---------------------------------------------------------
    # 3. GRÁFICO DE LINHA (Série Temporal: Real vs Previsto)
    # ---------------------------------------------------------
    print("Gerando gráfico de série temporal (Curva histórica)...")
    
    # Em vez de re-treinar com cross_val_predict, usamos a coluna de previsões salva
    # (Treinada via 'train_model.py')
    df['rendimento_previsto_kg_ha'] = df[coluna_prev]

    
    # Calcular a média ponderada do estado por ano
    df['producao_real'] = df['rendimento_medio_kg_ha'] * df['area_plantada_hectares']
    df['producao_prevista'] = df['rendimento_previsto_kg_ha'] * df['area_plantada_hectares']
    
    df_agrupado = df.groupby('ano').agg({
        'producao_real': 'sum',
        'producao_prevista': 'sum',
        'area_plantada_hectares': 'sum'
    }).reset_index()
    
    df_agrupado['rendimento_real_estado'] = df_agrupado['producao_real'] / df_agrupado['area_plantada_hectares']
    df_agrupado['rendimento_prev_estado'] = df_agrupado['producao_prevista'] / df_agrupado['area_plantada_hectares']
    
    # Calcular a média ponderada projetada para 2024
    df_2024['producao_prevista'] = df_2024['previsao_rendimento_kg_ha'] * df_2024['area_plantada_hectares']
    rend_2024 = df_2024['producao_prevista'].sum() / df_2024['area_plantada_hectares'].sum()
    
    # Preparar listas para o plot
    anos = list(df_agrupado['ano']) + [2024]
    rend_real = list(df_agrupado['rendimento_real_estado']) + [np.nan] # Não temos o real de 2024 ainda
    rend_prev = list(df_agrupado['rendimento_prev_estado']) + [rend_2024]
    
    plt.figure(figsize=(14, 7))
    
    # Plotar as linhas
    plt.plot(anos, rend_real, marker='o', linewidth=3, markersize=8, label='Real (Dados do IBGE)', color='#1f77b4')
    plt.plot(anos, rend_prev, marker='s', linewidth=2, linestyle='--', markersize=6, label='Previsto (Modelo Random Forest)', color='#ff7f0e')
    
    # Destacar o ano de forecast (2024)
    plt.scatter([2024], [rend_2024], color='red', s=150, zorder=5, label='Forecast 2024 (Safra Futura)')
    plt.annotate(f"{rend_2024:.0f} kg/ha", (2024, rend_2024), textcoords="offset points", xytext=(0,15), ha='center', fontsize=12, fontweight='bold', color='red')
    
    # Estilização
    plt.title('Curva Histórica de Rendimento de Soja (Mato Grosso) e Previsão Futura', fontsize=18, fontweight='bold')
    plt.xlabel('Ano da Safra', fontsize=14)
    plt.ylabel('Rendimento Médio Ponderado (kg/ha)', fontsize=14)
    plt.xticks(anos, rotation=45)
    
    # Para deixar o eixo Y focado nas variações reais
    plt.ylim(2600, 4000)
    
    plt.legend(fontsize=12, loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    path_serie = os.path.abspath(os.path.join('outputs', 'serie_temporal_safra.png'))
    plt.savefig(path_serie, dpi=300)
    plt.close()
    print(f"Gráfico 'Série Temporal' salvo em: {path_serie}")

if __name__ == '__main__':
    gerar_graficos()
