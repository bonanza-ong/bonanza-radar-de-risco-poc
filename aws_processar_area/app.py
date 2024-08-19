import geopandas as gpd
import zipfile
import boto3
import uuid
import os
from botocore.exceptions import ClientError
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union
from urllib.parse import unquote_plus
from sqlalchemy import create_engine
from datetime import datetime

# Obtém a string de conexão do ambiente
connection_bonanza_gis = os.environ.get("connection_bonanza_gis", "")

def prepare_gdf(gdf, area_code, file_key):
    # Renomeia a geometria se necessário
    if gdf.geometry.name != 'area_risco':
        gdf = gdf.rename_geometry('area_risco')

    # Define as colunas padrão
    nome = file_key
    em_risco = True
    descricao = file_key
    created_at = datetime.utcnow()

    # Verifica e adiciona a coluna 'nome' se não existir
    if 'nome' in gdf.columns:
        nome = gdf.iloc[0]['nome']

    # Verifica e adiciona a coluna 'descricao' se não existir
    if 'descricao' in gdf.columns:
        descricao = gdf.iloc[0]['descricao']

    gdf['nome'] = nome
    gdf['em_risco'] = em_risco
    gdf['descricao'] = descricao
    gdf['created_at'] = created_at
    gdf['area_code'] = area_code

    # Define o CRS se não estiver definido
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    elif gdf.crs.to_string() != 'EPSG:4326':
        gdf = gdf.to_crs(epsg=4326)

    # Corrige geometrias inválidas
    gdf['area_risco'] = gdf['area_risco'].buffer(0)
    if not gdf.is_valid.all():
        gdf['area_risco'] = gdf['area_risco'].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))

    # Mantém apenas as colunas desejadas
    gdf = gdf[['nome', 'em_risco', 'descricao', 'created_at', 'area_code', 'area_risco']]

    return gdf


def upload_to_postgis(gdf, table_name, db_connection_string):
    engine = create_engine(db_connection_string, pool_size=10, max_overflow=20, pool_timeout=300, pool_recycle=3600)
    gdf.to_postgis(table_name, engine, if_exists='append', index=False)
    print(f"Upload para a tabela '{table_name}' realizado com sucesso.")

def process_file(file_path, area_code, connection_string):
    # Carrega o arquivo em um GeoDataFrame usando geopandas
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.kml':
        gdf = gpd.read_file(file_path, driver='KML')
    elif file_extension in ('.geojson', '.shp'):
        gdf = gpd.read_file(file_path)
    else:
        print(f"Extensão de arquivo {file_extension} não suportada. Ignorando {file_path}.")
        return

    # Prepara o GeoDataFrame
    gdf = prepare_gdf(gdf, area_code, file_path.replace('/tmp/', ''))

    # Faz o upload para o PostGIS
    upload_to_postgis(gdf, "zona_risco", connection_string)

def lambda_handler(event, context):
    s3 = boto3.client('s3', region_name="us-east-1")

    # Extrai informações do evento
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    file_extension = os.path.splitext(file_key)[1].lower()

    # Define o caminho de download
    download_path = f'/tmp/{os.path.basename(file_key)}'

    try:
        # Baixa o arquivo do S3
        s3.download_file(bucket_name, file_key, download_path)
    except ClientError as e:
        print(f"Erro ao baixar o arquivo do S3: {e}")
        return {
            'statusCode': 500,
            'body': f"Erro ao baixar o arquivo: {str(e)}"
        }

    try:
        # Se o arquivo for um zip, descompacta-o
        if file_extension == '.zip':
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall('/tmp/')
            # A partir daqui, iteramos sobre os arquivos extraídos
            extracted_files = [os.path.join('/tmp/', f) for f in zip_ref.namelist()]
        else:
            extracted_files = [download_path]

        area_code = str(uuid.uuid4())

        # Processa cada arquivo extraído
        for file_path in extracted_files:
            process_file(file_path, area_code, connection_bonanza_gis)

        return {
            'statusCode': 200,
            'body': f'Arquivo {file_key} processado e carregado para a tabela zona_risco.'
        }

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return {
            'statusCode': 500,
            'body': f"Erro ao processar o arquivo: {str(e)}"
        }
