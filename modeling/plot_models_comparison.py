import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
import warnings

warnings.filterwarnings('ignore')

def gerar_grafico_comparativo():
    print("Carregando dados para o gráfico comparativo...")
    dataset_path = os.path.join('data', 'dataset_com_previsoes.csv')
    
    if not os.path.exists(dataset_path):
        print(f"[ERRO] {dataset_path} não encontrado. Execute 'train_model.py' primeiro para gerar as previsões.")
        return
        
    df = pd.read_csv(dataset_path, sep=';', decimal=',')
    
    ano_corte = 2021
    
    # Modelos com os nomes exatamente como foram salvos pelo train_model.py
    modelos = [
        "Regressão Linear Múltipla",
        "Híbrido: Random Forest",
        "Híbrido: Gradient Boosting",
        "Híbrido: XGBoost"
    ]
    
    # Preparar a figura com 4 subplots (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    axes = axes.flatten()
    
    sns.set_theme(style="whitegrid")
    
    for i, nome in enumerate(modelos):
        print(f"Gerando gráfico para {nome}...")
        
        # Verificar se a coluna de previsão existe
        col_prev = f'prev_{nome}'
        if col_prev not in df.columns:
            print(f"[AVISO] Coluna {col_prev} não encontrada no dataset. Pulando...")
            continue
        
        # Calcular médias ponderadas pelo estado inteiro
        df['producao_real'] = df['rendimento_medio_kg_ha'] * df['area_plantada_hectares']
        df[f'producao_prev_{nome}'] = df[col_prev] * df['area_plantada_hectares']
        
        agrupado = df.groupby('ano').agg({
            'producao_real': 'sum',
            f'producao_prev_{nome}': 'sum',
            'area_plantada_hectares': 'sum'
        }).reset_index()
        
        agrupado['rendimento_real'] = agrupado['producao_real'] / agrupado['area_plantada_hectares']
        agrupado['rendimento_prev'] = agrupado[f'producao_prev_{nome}'] / agrupado['area_plantada_hectares']
        
        ax = axes[i]
        
        # Plotar as linhas Real x Previsto
        ax.plot(agrupado['ano'], agrupado['rendimento_real'], marker='o', linewidth=3, label='Real (IBGE)', color='#1f77b4')
        ax.plot(agrupado['ano'], agrupado['rendimento_prev'], marker='s', linewidth=2, linestyle='--', label='Previsto', color='#ff7f0e')
        
        # Adicionar a linha vermelha de corte separando Treino e Teste
        y_max = max(agrupado['rendimento_real'].max(), agrupado['rendimento_prev'].max())
        y_min = min(agrupado['rendimento_real'].min(), agrupado['rendimento_prev'].min())
        
        ax.axvline(x=ano_corte + 0.5, color='red', linestyle=':', linewidth=2)
        
        # Adicionar anotações de texto (Treino e Teste)
        ax.text(ano_corte, y_max * 0.98, 'TREINO (Até 2021)', color='gray', fontsize=12, fontweight='bold', ha='right')
        ax.text(ano_corte + 1, y_max * 0.98, 'TESTE (OOT)', color='red', fontsize=12, fontweight='bold', ha='left')
        
        ax.set_title(nome, fontsize=16, fontweight='bold')
        ax.set_xlabel('Ano da Safra', fontsize=12)
        ax.set_ylabel('Rendimento Ponderado (kg/ha)', fontsize=12)
        ax.legend(loc='lower right')
        
    plt.tight_layout()
    os.makedirs('outputs', exist_ok=True)
    path_grafico = os.path.abspath(os.path.join('outputs', 'comparativo_temporal_modelos.png'))
    plt.savefig(path_grafico, dpi=300)
    plt.close()
    
    print(f"\n[SUCESSO] Gráfico salvo em: {path_grafico}")

if __name__ == '__main__':
    gerar_grafico_comparativo()
