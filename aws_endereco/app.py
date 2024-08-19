import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from geopy.geocoders import Nominatim

# Obtém a string de conexão do ambiente
connection_bonanza_gis = os.environ.get("connection_bonanza_gis", "")

def lambda_handler(event, context):
    # Carrega o corpo do evento
    event_body = json.loads(event['body'])
    
    # Obtém os detalhes do endereço do corpo do evento
    rua = event_body.get("rua")
    bairro = event_body.get("bairro")
    numero = event_body.get("numero")
    cidade = event_body.get("cidade")
    estado = event_body.get("estado")
    zip = event_body.get("zip")
    pais = event_body.get("pais")
    complemento = event_body.get("complemento")
    
    # Cria o geocodificador
    geolocator = Nominatim(user_agent="bonanza-endereco-point")
    
    # Concatena o endereço completo
    full_address = f"{rua}, {numero}, {bairro}, {cidade}, {estado}, {pais}"

    # Geocodifica o endereço
    location = geolocator.geocode(full_address)
    if location:
        lat, lon = location.latitude, location.longitude
        print(f"Endereço '{full_address}' geocodificado para Latitude: {lat}, Longitude: {lon}")
    else:
        lat, lon = None, None
        print(f"Não foi possível geocodificar o endereço '{full_address}'")
    
    # Cria o engine e a sessão
    engine = create_engine(connection_bonanza_gis)
    db = scoped_session(sessionmaker(bind=engine))

    try:
        # Define a consulta SQL como texto
        sql_query = text("""
            INSERT INTO endereco (rua, bairro, numero, cidade, estado, complemento, created_at, lat, lon, localizacao, zip, pais)
            VALUES(:rua, :bairro, :numero, :cidade, :estado, :complemento, :created_at, :lat, :lon, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), :zip, :pais)
        """)

        # Define os parâmetros da consulta
        params = {
            "rua": rua,
            "bairro": bairro,
            "numero": numero,
            "cidade": cidade,
            "estado": estado,
            "complemento": complemento,
            "pais": pais,
            "zip": zip,
            "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "lat": lat,
            "lon": lon
        }

        # Executa a consulta com os parâmetros
        db.execute(sql_query, params)
        db.commit()

        # Define o resultado da resposta
        result = {"body": json.dumps({"action": "POST", "message": "Endereco salvo com sucesso"}), "statusCode": 200}
        
    except Exception as ex:
        # Define o resultado da resposta em caso de erro
        result = {"body": json.dumps({"action": "POST", "message": str(ex)}), "statusCode": 500}
        
    finally:
        # Fecha a sessão
        db.remove()

    return result
