# Lambda Function: Geocoding and Address Storage

## Descrição

Esta função Lambda recebe informações de endereço, geocodifica o endereço para obter coordenadas de latitude e longitude, e armazena os dados, incluindo as coordenadas, em uma tabela `endereco` em um banco de dados PostgreSQL com extensão PostGIS.

## Requisitos

- AWS Lambda
- Python 3.x
- PostGIS no PostgreSQL
- Biblioteca `geopy` para geocodificação
- `sqlalchemy` para manipulação do banco de dados

## Variáveis de Ambiente

Certifique-se de definir a variável de ambiente `connection_bonanza_gis` para a string de conexão do seu banco de dados PostgreSQL. A string de conexão deve estar no formato:

```
postgresql://username:password@hostname:port/dbname
```

## Estrutura da Tabela

A tabela `endereco` deve ter a seguinte estrutura:

```sql
CREATE TABLE endereco (
    endereco_id SERIAL PRIMARY KEY,
    rua VARCHAR(256),
    numero INTEGER,
    bairro VARCHAR(256),
    estado VARCHAR(128),
    cidade VARCHAR(128),
    complemento VARCHAR(256),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    localizacao GEOMETRY(POINT, 4326)
);
```

## Funcionamento

1. **Recebimento do Evento**: A função Lambda é acionada por um evento contendo os detalhes do endereço no corpo da solicitação (`event['body']`).

2. **Geocodificação**: Utiliza o serviço Nominatim do `geopy` para converter o endereço completo em coordenadas de latitude e longitude.

3. **Armazenamento**: Insere o endereço e as coordenadas geocodificadas na tabela `endereco` no banco de dados PostgreSQL. As coordenadas são armazenadas como um ponto no tipo `GEOMETRY` do PostGIS.

## Exemplo de Evento

Aqui está um exemplo de payload que você pode enviar para a função Lambda:

```json
{
  "body": "{\"rua\": \"Rua das Flores\", \"bairro\": \"Jardim das Américas\", \"numero\": 123, \"cidade\": \"Curitiba\", \"estado\": \"PR\", \"complemento\": \"Apto 45\"}"
}
```

## Observações

- **Segurança**: Certifique-se de que a string de conexão com o banco de dados não esteja exposta e use práticas seguras para armazenar e acessar informações sensíveis.

- **Limitações de API**: O serviço de geocodificação pode ter limitações de taxa ou uso. Verifique a documentação da API Nominatim para mais detalhes.

- **Manejo de Erros**: A função captura e retorna erros em caso de falhas na geocodificação ou no armazenamento dos dados.
