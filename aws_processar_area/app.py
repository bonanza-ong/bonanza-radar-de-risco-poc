import geopandas as gpd
import boto3
import os
import zipfile
import uuid
from sqlalchemy import create_engine
from botocore.exceptions import ClientError
from urllib.parse import unquote_plus
from datetime import datetime

connection_bonanza_gis = os.environ.get("connection_bonanza_gis", "")

def prepare_gdf(gdf):
    # Renomeia a coluna de geometria para 'area_risco' se necessário
    if gdf.geometry.name != 'area_risco':
        gdf = gdf.rename_geometry('area_risco')

    # Verifica e adiciona a coluna 'nome' se não existir
    if 'nome' not in gdf.columns:
        gdf['nome'] = 'Nome padrão'

    # Verifica e adiciona a coluna 'descricao' se não existir
    if 'descricao' not in gdf.columns:
        gdf['descricao'] = 'Descrição padrão'

    # Verifica e adiciona a coluna 'created_at' se não existir
    if 'created_at' not in gdf.columns:
        gdf['created_at'] = datetime.utcnow()

    return gdf

def upload_to_postgis(gdf, table_name, db_connection_string):
    engine = create_engine(db_connection_string, pool_size=10, max_overflow=20, pool_timeout=300, pool_recycle=3600)
    gdf.to_postgis(table_name, engine, if_exists='append', index=False)
    print(f"Upload para a tabela '{table_name}' realizado com sucesso.")

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

        # Processa cada arquivo extraído
        for file_path in extracted_files:
            file_extension = os.path.splitext(file_path)[1].lower()
            # Carrega o arquivo em um GeoDataFrame usando geopandas
            if file_extension == '.kml':
                gdf = gpd.read_file(file_path, driver='KML')
            elif file_extension in ('.geojson', '.shp'):
                gdf = gpd.read_file(file_path)
            else:
                print(f"Extensão de arquivo {file_extension} não suportada. Ignorando {file_path}.")
                continue  # Ignora arquivos com extensões não suportadas

            # Prepara o GeoDataFrame para garantir que as colunas necessárias estejam presentes
            gdf = prepare_gdf(gdf)

            # Faz o upload para o PostGIS
            upload_to_postgis(gdf, "zona_risco", connection_bonanza_gis)

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
