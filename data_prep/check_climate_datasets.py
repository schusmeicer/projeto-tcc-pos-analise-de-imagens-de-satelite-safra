import ee

PROJECT_ID = 'gen-lang-client-0007396468'
try:
    ee.Initialize(project=PROJECT_ID)
except Exception as e:
    pass

def check_dataset(name, collection_id):
    try:
        col = ee.ImageCollection(collection_id)
        latest = col.sort('system:time_start', False).first()
        date = ee.Date(latest.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        bands = latest.bandNames().getInfo()
        print(f"--- {name} ---")
        print(f"ID: {collection_id}")
        print(f"Última data disponível: {date}")
        print(f"Bandas (Variáveis): {bands[:10]} ...\n")
    except Exception as e:
        print(f"Erro ao checar {name} ({collection_id}): {e}\n")

if __name__ == "__main__":
    check_dataset("TerraClimate", "IDAHO_EPSCOR/TERRACLIMATE")
    check_dataset("ERA5-Land Mensal", "ECMWF/ERA5_LAND/MONTHLY_AGGR")
    check_dataset("ERA5-Land Diário", "ECMWF/ERA5_LAND/HOURLY") # There's no daily_aggr, usually it's hourly, let's check hourly
    check_dataset("CHIRPS Diário", "UCSB-CHG/CHIRPS/DAILY")
