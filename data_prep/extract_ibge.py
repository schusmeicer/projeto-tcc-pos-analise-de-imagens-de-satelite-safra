import sidrapy
import pandas as pd
import os
import time

def extract_soybean_data_mt():
    print("Iniciando a extração dos dados do IBGE (Tabela 1612) para Soja no Mato Grosso...")
    
    # Anos de interesse para a análise histórica (vamos pegar os últimos 18 anos)
    anos = [str(ano) for ano in range(2008, 2026)]
    df_list = []
    
    for ano in anos:
        print(f"Buscando dados para o ano {ano}...")
        try:
            # Fazemos a busca por ano e para "all" (todos os municípios do Brasil)
            # Dessa forma evitamos o limite de 50.000 valores por requisição da API
            df_raw = sidrapy.get_table(
                table_code="1612",
                territorial_level="6",
                ibge_territorial_code="all",
                variable="109,214,215,216,112",
                period=ano,
                classification="81/2713"
            )
            
            # Formata os dados
            df_raw.columns = df_raw.iloc[0]
            df = df_raw[1:].copy()
            
            # Filtra apenas os municípios do MT (código IBGE iniciando em 51)
            df = df[df['Município (Código)'].str.startswith('51', na=False)]
            
            df_list.append(df)
            
            # Pequena pausa para não sobrecarregar a API do IBGE
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro ao buscar o ano {ano}: {e}")
            
    if not df_list:
        print("Nenhum dado foi extraído. Verifique os erros acima.")
        return
        
    print("Concatenando todos os anos...")
    df_final = pd.concat(df_list, ignore_index=True)
    
    # Selecionando e renomeando colunas
    cols_to_keep = {
        'Ano': 'ano',
        'Município (Código)': 'cod_municipio',
        'Município': 'nome_municipio',
        'Variável': 'variavel',
        'Valor': 'valor'
    }
    df_final = df_final[list(cols_to_keep.keys())].rename(columns=cols_to_keep)
    
    # Limpeza dos valores
    df_final['valor'] = pd.to_numeric(df_final['valor'].replace('-', pd.NA).replace('...', pd.NA), errors='coerce')
    df_final['ano'] = df_final['ano'].astype(int)
    
    print("Pivotando a tabela...")
    df_pivot = df_final.pivot_table(
        index=['ano', 'cod_municipio', 'nome_municipio'],
        columns='variavel',
        values='valor',
        aggfunc='first'
    ).reset_index()
    
    df_pivot.columns.name = None
    
    # Salvar em CSV
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, 'ibge_pam_soja_mt.csv')
    df_pivot.to_csv(output_path, index=False, sep=';', decimal=',')
    
    print(f"\nExtração concluída com sucesso! Base salva em: {output_path}")
    print(f"Tamanho da base final: {df_pivot.shape}")
    print(df_pivot.head())

if __name__ == '__main__':
    extract_soybean_data_mt()
