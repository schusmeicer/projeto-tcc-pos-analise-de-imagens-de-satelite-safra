import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_forecast():
    # Carregar dados com as previsões já consolidadas (sem precisar re-treinar)
    df = pd.read_csv('data/dataset_com_previsoes.csv', sep=';', decimal=',')
    
    # Filtrar apenas a safra de 2024
    df_2024 = df[df['ano'] == 2024].copy()

    # Encontrar dinamicamente a coluna do melhor modelo (Random Forest)
    col_previsao = [c for c in df.columns if 'Random Forest' in c][0]
    
    # Top 15 municípios (para o gráfico)
    top_15 = df_2024.sort_values(col_previsao, ascending=False).head(15)

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 8))
    sns.barplot(
        x=col_previsao, 
        y='nome_municipio', 
        data=top_15, 
        palette='magma'
    )
    
    plt.title('Forecast 2024/2025: Top 15 Municípios (Random Forest Híbrido)', fontsize=16, fontweight='bold')
    plt.xlabel('Rendimento Previsto (kg/ha)', fontsize=14)
    plt.ylabel('Município', fontsize=14)
    
    # Adicionar os valores nas barras
    for index, value in enumerate(top_15[col_previsao]):
        plt.text(value + 10, index, f'{value:.0f}', va='center', fontsize=11)
        
    plt.xlim(3000, 4200) # Ajustar limite para destacar as diferenças
    plt.tight_layout()
    
    os.makedirs('outputs', exist_ok=True)
    path_forecast = os.path.abspath(os.path.join('outputs', 'forecast_2024_rf_hibrido.png'))
    plt.savefig(path_forecast, dpi=300)
    plt.close()
    print(f"Gráfico salvo em: {path_forecast}")

if __name__ == '__main__':
    plot_forecast()
