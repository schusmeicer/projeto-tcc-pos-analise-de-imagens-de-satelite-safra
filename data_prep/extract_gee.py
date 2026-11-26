import ee
import geemap
import geobr
import pandas as pd
import os

# Insira aqui o ID do seu projeto do Google Cloud vinculado ao Earth Engine
PROJECT_ID = 'gen-lang-client-0007396468'

def authenticate_gee():
    try:
        print("Tentando inicializar o Google Earth Engine...")
        ee.Initialize(project=PROJECT_ID)
        print("Earth Engine inicializado com sucesso!")
    except Exception as e:
        print("\n[!] Autenticação necessária.")
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)

def get_window_image(modis_veg, modis_lst, chirps, era5, data_inicio, data_fim, sufixo, mask=None):
    """
    Função auxiliar para processar as coleções de imagens para uma janela temporal específica
    e renomear as bandas adicionando um sufixo (ex: '_j1' ou '_j2'). Aplica máscara espacial (MapBiomas) se fornecida.
    """
    # 1. Vegetação (MODIS 250m)
    img_veg = modis_veg.filterDate(data_inicio, data_fim) \
                       .select(['NDVI', 'EVI']) \
                       .mean() \
                       .multiply(0.0001)
                       
    # 2. LST (Land Surface Temperature MODIS 1km) - Convertendo para Celsius
    img_lst = modis_lst.filterDate(data_inicio, data_fim) \
                       .select(['LST_Day_1km']) \
                       .mean() \
                       .multiply(0.02).subtract(273.15)
                       
    # 3. Clima - Precipitação (CHIRPS)
    img_pr = chirps.filterDate(data_inicio, data_fim) \
                   .select(['precipitation']) \
                   .sum() \
                   .rename(['pr'])
                   
    # 4. Clima - ERA5-Land (Temperatura, Umidade do Solo, Evapotranspiração)
    # Convertendo temperatura de Kelvin para Celsius e PET de metros para mm (inverte o sinal pois ERA5 é negativo)
    img_era5 = era5.filterDate(data_inicio, data_fim) \
                   .select(['temperature_2m', 'volumetric_soil_water_layer_1', 'potential_evaporation_sum'])
                   
    img_tmean = img_era5.select(['temperature_2m']).mean().subtract(273.15).rename(['tmean'])
    img_soil = img_era5.select(['volumetric_soil_water_layer_1']).mean().rename(['soil'])
    img_pet = img_era5.select(['potential_evaporation_sum']).sum().multiply(-1000)
    
    # 5. Déficit Hídrico = Chuva - Evapotranspiração Potencial
    img_def = img_pr.subtract(img_pet).rename(['def'])
                                
    # Junta todas as bandas da janela
    img_window = img_veg.addBands(img_lst).addBands(img_pr).addBands(img_def).addBands(img_tmean).addBands(img_soil)
    
    # Renomeia as bandas com o sufixo da janela (ex: NDVI_j1, pr_j1)
    band_names = img_window.bandNames()
    new_names = band_names.map(lambda name: ee.String(name).cat(sufixo))
    
    img_window = img_window.rename(new_names)
    
    if mask is not None:
        img_window = img_window.updateMask(mask)
        
    return img_window

def extract_gee_data():
    authenticate_gee()
    
    print("\nBaixando limites geográficos dos municípios do MT (geobr)...")
    mt_mun = geobr.read_municipality(code_muni="MT", year=2020)
    
    print("Enviando geometrias para o Earth Engine...")
    fc = geemap.geopandas_to_ee(mt_mun)
    
    # Coleções
    modis_veg = ee.ImageCollection("MODIS/061/MOD13Q1")
    modis_lst = ee.ImageCollection("MODIS/061/MOD11A2")
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
    era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
    mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1')
    
    anos = range(2008, 2026)
    resultados = []
    
    print("\nIniciando cálculo com novas variáveis (CHIRPS, ERA5-Land, Déficit Hídrico, LST, Tmean) e Janelas Fenológicas...")
    
    for ano in anos:
        print(f" -> Processando a safra {ano}/{ano+1}...")
        
        # Definindo as duas janelas
        # Janela 1 (Crescimento Vegetativo): Outubro a Dezembro do ano de plantio
        inicio_j1 = f'{ano}-10-01'
        fim_j1 = f'{ano}-12-31'
        
        # Janela 2 (Floração e Enchimento): Janeiro a Março do ano seguinte
        inicio_j2 = f'{ano+1}-01-01'
        fim_j2 = f'{ano+1}-03-31'
        
        # Definir a máscara do MapBiomas (Coleção 9 possui dados até 2023)
        # Assumimos que para 2024 e 2025 o uso do solo se mantém próximo a 2023
        ano_mask = min(ano, 2023)
        # Classe 39 é a Soja
        mask = mapbiomas.select(f'classification_{ano_mask}').eq(39)
        
        # Obtém imagens combinadas por janela
        img_j1 = get_window_image(modis_veg, modis_lst, chirps, era5, inicio_j1, fim_j1, '_j1', mask)
        img_j2 = get_window_image(modis_veg, modis_lst, chirps, era5, inicio_j2, fim_j2, '_j2', mask)
        
        # Junta todas as bandas do ano em uma única imagem
        img_safra = img_j1.addBands(img_j2)
        
        # Redução (Zonal Statistics)
        stats = img_safra.reduceRegions(
            collection=fc,
            reducer=ee.Reducer.mean(),
            scale=1000 # Mudando a escala para 1km para agilizar o processamento pesado de 16 bandas
        )
        
        try:
            features = stats.getInfo()['features']
            for f in features:
                props = f['properties']
                
                # Coleta as propriedades calculadas
                row = {
                    'ano': ano,
                    'cod_municipio': props.get('code_muni'),
                    'nome_municipio': props.get('name_muni')
                }
                
                # Extraindo para J1 e J2
                for var in ['NDVI', 'EVI', 'LST_Day_1km', 'pr', 'def', 'tmean', 'soil']:
                    row[f'{var}_j1'] = props.get(f'{var}_j1', None)
                    row[f'{var}_j2'] = props.get(f'{var}_j2', None)
                
                resultados.append(row)
                
        except Exception as e:
            print(f"Erro ao baixar dados da safra {ano}: {e}")
            
    print("\nProcessamento concluído. Salvando base de dados...")
    df_dados = pd.DataFrame(resultados)
    
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    output_path = os.path.join(data_dir, 'gee_ndvi_soja_mt.csv')
    df_dados.to_csv(output_path, index=False, sep=';', decimal=',')
    
    print(f"\nVariáveis de Satélite salvas com sucesso em: {output_path}")

if __name__ == '__main__':
    extract_gee_data()
