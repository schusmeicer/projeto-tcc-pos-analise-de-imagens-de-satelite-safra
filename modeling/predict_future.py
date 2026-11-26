import pandas as pd
import os
import numpy as np
import ee
import geemap
import geobr
from sklearn.ensemble import RandomForestRegressor
from hybrid_model import HybridDetrendingRegressor
import warnings

warnings.filterwarnings('ignore')

PROJECT_ID = 'gen-lang-client-0007396468'

def authenticate_gee():
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception as e:
        print("[!] Autenticação necessária.")
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)

def prever_safra_2024():
    print("="*80)
    print(f"{'PREVISÃO DE SAFRA INÉDITA - MATO GROSSO (2024/2025)':^80}")
    print("="*80 + "\n")

    dataset_path = os.path.join('data', 'dataset_final_soja_mt.csv')
    if not os.path.exists(dataset_path):
        print(f"[ERRO] {dataset_path} não encontrado.")
        return

    df = pd.read_csv(dataset_path, sep=';', decimal=',')
    
    print("1. Treinando o modelo Random Forest com o histórico completo (2008-2023)...")
    features_satelite = ['NDVI_j1', 'NDVI_j2', 'EVI_j1', 'EVI_j2', 'LST_Day_1km_j1', 'LST_Day_1km_j2', 
                         'pr_j1', 'pr_j2', 'def_j1', 'def_j2', 'tmean_j1', 'tmean_j2', 'soil_j1', 'soil_j2']
    features = ['ano', 'area_plantada_hectares'] + features_satelite
    target = 'rendimento_medio_kg_ha'
    
    X_train = df[features]
    y_train = df[target]
    
    # Parâmetros otimizados anteriormente
    base_rf = RandomForestRegressor(n_estimators=300, min_samples_split=2, max_depth=3, random_state=42, n_jobs=-1)
    modelo = HybridDetrendingRegressor(base_estimator=base_rf)
    modelo.fit(X_train, y_train)
    print("Modelo treinado com sucesso!\n")

    # Extrair dados de 2024 do GEE
    print("2. Conectando ao Earth Engine para extrair dados da safra 2024/2025...")
    authenticate_gee()
    
    print("Baixando malha do MT...")
    mt_mun = geobr.read_municipality(code_muni="MT", year=2020)
    fc = geemap.geopandas_to_ee(mt_mun)
    
    modis_veg = ee.ImageCollection("MODIS/061/MOD13Q1")
    modis_lst = ee.ImageCollection("MODIS/061/MOD11A2")
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
    era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
    
    ano = 2023
    
    def get_window_image(data_inicio, data_fim, sufixo):
        img_veg = modis_veg.filterDate(data_inicio, data_fim).select(['NDVI', 'EVI']).mean().multiply(0.0001)
        img_lst = modis_lst.filterDate(data_inicio, data_fim).select(['LST_Day_1km']).mean().multiply(0.02).subtract(273.15)
        
        img_pr = chirps.filterDate(data_inicio, data_fim).select(['precipitation']).sum().rename(['pr'])
        img_era5 = era5.filterDate(data_inicio, data_fim).select(['temperature_2m', 'volumetric_soil_water_layer_1', 'potential_evaporation_sum'])
        img_tmean = img_era5.select(['temperature_2m']).mean().subtract(273.15).rename(['tmean'])
        img_soil = img_era5.select(['volumetric_soil_water_layer_1']).mean().rename(['soil'])
        img_pet = img_era5.select(['potential_evaporation_sum']).sum().multiply(-1000)
        img_def = img_pr.subtract(img_pet).rename(['def'])
        
        img_window = img_veg.addBands(img_lst).addBands(img_pr).addBands(img_def).addBands(img_tmean).addBands(img_soil)
        band_names = img_window.bandNames()
        new_names = band_names.map(lambda name: ee.String(name).cat(sufixo))
        return img_window.rename(new_names)
        
    inicio_j1 = f'{ano}-10-01'
    fim_j1 = f'{ano}-12-31'
    inicio_j2 = f'{ano+1}-01-01'
    fim_j2 = f'{ano+1}-03-31'
    
    img_j1 = get_window_image(inicio_j1, fim_j1, '_j1')
    img_j2 = get_window_image(inicio_j2, fim_j2, '_j2')
    img_safra = img_j1.addBands(img_j2)
    
    stats = img_safra.reduceRegions(collection=fc, reducer=ee.Reducer.mean(), scale=1000)
    
    print("Baixando dados processados do servidor...")
    resultados_2024 = []
    features_gee = stats.getInfo()['features']
    for f in features_gee:
        props = f['properties']
        row = {
            'ano': ano,
            'cod_municipio': props.get('code_muni'),
            'nome_municipio': props.get('name_muni')
        }
        for var in ['NDVI', 'EVI', 'LST_Day_1km', 'pr', 'def', 'tmean', 'soil']:
            row[f'{var}_j1'] = props.get(f'{var}_j1', None)
            row[f'{var}_j2'] = props.get(f'{var}_j2', None)
        resultados_2024.append(row)
    
    df_2024 = pd.DataFrame(resultados_2024)
    df_2024['cod_municipio'] = pd.to_numeric(df_2024['cod_municipio'], errors='coerce').astype('Int64')
    
    # Mesclar com a área plantada de 2023
    print("3. Estimando área plantada (baseada em 2023)...")
    df_2023 = df[df['ano'] == 2023][['cod_municipio', 'area_plantada_hectares']]
    df_2024 = pd.merge(df_2024, df_2023, on='cod_municipio', how='inner')
    
    # Remover nulos caso alguma imagem tenha falhado
    df_2024 = df_2024.dropna(subset=features)
    
    print(f"Dados prontos para {len(df_2024)} municípios. Fazendo previsões...\n")
    
    X_pred = df_2024[features]
    df_2024['previsao_rendimento_kg_ha'] = modelo.predict(X_pred)
    df_2024['previsao_producao_total_toneladas'] = (df_2024['previsao_rendimento_kg_ha'] * df_2024['area_plantada_hectares']) / 1000
    
    # Salvar resultados
    output_path = os.path.join('data', 'previsao_safra_2024_mt.csv')
    df_2024.to_csv(output_path, index=False, sep=';', decimal=',')
    
    print("="*80)
    print("RESULTADOS: TOP 10 MUNICÍPIOS COM MAIOR RENDIMENTO PREVISTO (kg/ha) - 2024")
    print("="*80)
    
    top_10 = df_2024.sort_values('previsao_rendimento_kg_ha', ascending=False).head(10)
    header = f"{'Município':<30} | {'Área (ha)':>12} | {'Rend. Previsto (kg/ha)':>22} | {'Prod. Prevista (Ton)':>20}"
    print(header)
    print("-" * 89)
    for idx, row in top_10.iterrows():
        print(f"{row['nome_municipio']:<30} | {row['area_plantada_hectares']:>12,.0f} | {row['previsao_rendimento_kg_ha']:>22,.2f} | {row['previsao_producao_total_toneladas']:>20,.2f}")
    
    print("\n[!] Previsão salva em:", output_path)

if __name__ == '__main__':
    prever_safra_2024()
