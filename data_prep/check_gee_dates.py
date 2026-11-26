import ee

PROJECT_ID = 'gen-lang-client-0007396468'

try:
    ee.Initialize(project=PROJECT_ID)
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project=PROJECT_ID)

def get_latest_date(collection_name):
    col = ee.ImageCollection(collection_name)
    latest = col.sort('system:time_start', False).first()
    date = ee.Date(latest.get('system:time_start')).format('YYYY-MM-dd').getInfo()
    return date

if __name__ == "__main__":
    print("Checando as últimas datas disponíveis no Google Earth Engine...")
    try:
        print(f"MODIS NDVI/EVI (MOD13Q1): {get_latest_date('MODIS/061/MOD13Q1')}")
        print(f"MODIS LST (MOD11A2): {get_latest_date('MODIS/061/MOD11A2')}")
        print(f"TerraClimate: {get_latest_date('IDAHO_EPSCOR/TERRACLIMATE')}")
    except Exception as e:
        print(f"Erro ao acessar GEE: {e}")
