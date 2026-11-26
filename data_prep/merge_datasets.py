import pandas as pd
import os

def unificar_bases():
    """
    Função principal para juntar (merge) os dados do IBGE com os dados de Satélite (GEE).
    Os arquivos devem estar dentro da pasta 'data'.
    """
    print("Iniciando a unificação das bases de dados para o TCC...")
    
    # ---------------------------------------------------------
    # PASSO 1: Carregar os arquivos CSV gerados pelos outros scripts
    # ---------------------------------------------------------
    path_ibge = os.path.join('data', 'ibge_pam_soja_mt.csv')
    path_gee = os.path.join('data', 'gee_ndvi_soja_mt.csv')
    
    # Verifica se os arquivos realmente existem antes de continuar
    if not os.path.exists(path_ibge):
        print(f"\n[ERRO] O arquivo {path_ibge} não foi encontrado. Execute o script 'extract_ibge.py' primeiro.")
        return
        
    if not os.path.exists(path_gee):
        print(f"\n[ERRO] O arquivo {path_gee} não foi encontrado. Execute o script 'extract_gee.py' primeiro.")
        return

    print("Carregando bases...")
    # Lendo o CSV do IBGE (separador ponto e vírgula e decimal vírgula, conforme o código de extração)
    df_ibge = pd.read_csv(path_ibge, sep=';', decimal=',')
    
    # Lendo o CSV do GEE (Satélite)
    df_gee = pd.read_csv(path_gee, sep=';', decimal=',')

    # ---------------------------------------------------------
    # PASSO 2: Tratamento de Tipos de Dados (Data Cleaning)
    # ---------------------------------------------------------
    print("Limpando e formatando os dados...")
    
    # Garantir que a coluna 'ano' e 'cod_municipio' são do tipo numérico inteiro em ambas as tabelas
    # Isso evita erros durante a junção (ex: "2010" em texto não junta com 2010 em número)
    df_ibge['ano'] = pd.to_numeric(df_ibge['ano'], errors='coerce').astype('Int64')
    df_ibge['cod_municipio'] = pd.to_numeric(df_ibge['cod_municipio'], errors='coerce').astype('Int64')
    
    df_gee['ano'] = pd.to_numeric(df_gee['ano'], errors='coerce').astype('Int64')
    df_gee['cod_municipio'] = pd.to_numeric(df_gee['cod_municipio'], errors='coerce').astype('Int64')
    
    # Padronizar nomes de colunas no df_ibge para evitar espaços ou acentos, o que facilita na Modelagem depois
    # 'Área colhida' vira 'area_colhida', etc.
    df_ibge = df_ibge.rename(columns={
        'Quantidade produzida': 'quantidade_produzida_toneladas',
        'Rendimento médio da produção': 'rendimento_medio_kg_ha',
        'Valor da produção': 'valor_producao_mil_reais',
        'Área colhida': 'area_colhida_hectares',
        'Área plantada': 'area_plantada_hectares'
    })

    # O df_gee já tem as colunas limpas: 'ano', 'cod_municipio', 'nome_municipio', ...
    # Vamos remover a coluna 'nome_municipio' do GEE para não ficar duplicada após a junção
    df_gee = df_gee.drop(columns=['nome_municipio'])

    # ---------------------------------------------------------
    # PASSO 3: Junção (Merge)
    # ---------------------------------------------------------
    print("Cruzando dados de Produção com dados de Satélite...")
    
    # O método 'merge' cruza as informações como no PROCV do Excel ou JOIN do SQL
    # "how='inner'" significa que só vai manter as linhas que existirem EM AMBAS as tabelas.
    # Ex: Se em 2008 um município tem dado de satélite, mas o IBGE diz que ele não produziu soja, ele fica de fora.
    df_final = pd.merge(
        left=df_ibge, 
        right=df_gee, 
        on=['ano', 'cod_municipio'], # Chaves de junção
        how='inner' 
    )

    # ---------------------------------------------------------
    # PASSO 4: Remoção de Nulos
    # ---------------------------------------------------------
    # Removemos municípios cujo rendimento foi nulo ou onde a imagem de satélite falhou (nulo)
    qtd_antes = len(df_final)
    variaveis = ['NDVI', 'EVI', 'LST_Day_1km', 'pr', 'def', 'tmean', 'soil']
    colunas_gee = [f"{var}_j1" for var in variaveis] + [f"{var}_j2" for var in variaveis]
    
    df_final = df_final.dropna(subset=['rendimento_medio_kg_ha'] + colunas_gee)
    qtd_depois = len(df_final)
    print(f"Linhas removidas por falta de dados (Satélite nulo ou não plantou soja no ano): {qtd_antes - qtd_depois}")

    # ---------------------------------------------------------
    # PASSO 5: Salvar o Arquivo Final
    # ---------------------------------------------------------
    output_path = os.path.join('data', 'dataset_final_soja_mt.csv')
    df_final.to_csv(output_path, index=False, sep=';', decimal=',')
    
    print(f"\n[SUCESSO] Unificação Concluída com Sucesso!")
    print(f"O dataset final foi salvo em: {output_path}")
    print("\nResumo dos Dados Finais:")
    print(f"- Total de registros (município/ano): {len(df_final)}")
    print(f"- Colunas disponíveis: {list(df_final.columns)}")
    
    print("\nPróximo Passo Recomendado: Abra ou execute o script 'train_model.py' para prever a produção com Machine Learning!")

if __name__ == '__main__':
    unificar_bases()
