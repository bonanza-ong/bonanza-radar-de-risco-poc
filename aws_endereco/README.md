
# AWS Lambda - Geocodificação de Endereços e Salvamento em Banco de Dados PostGIS

## Descrição

Esta função AWS Lambda realiza geocodificação de endereços e salva os resultados em um banco de dados PostGIS. A função:

1. Recebe um evento contendo detalhes do endereço.
2. Concatena o endereço e utiliza o serviço de geocodificação da Nominatim para obter as coordenadas geográficas (latitude e longitude).
3. Insere o endereço e as coordenadas obtidas em uma tabela PostGIS chamada `endereco`, utilizando a extensão espacial do PostgreSQL.

## Pré-requisitos

### Dependências

Certifique-se de que sua função Lambda tenha as seguintes dependências instaladas no ambiente:

- `sqlalchemy`
- `geopy`
- `psycopg2-binary`

Essas bibliotecas podem ser incluídas ao criar um pacote de implantação customizado ou usando camadas Lambda.

### Configuração do Ambiente

A função Lambda espera que a string de conexão ao banco de dados PostGIS seja passada como uma variável de ambiente chamada `connection_bonanza_gis`.

## Como Funciona

1. **Entrada via Evento**: A função é acionada por um evento que contém informações de endereço no formato JSON.
2. **Geocodificação**: A função utiliza a biblioteca `geopy` para geocodificar o endereço completo (concatenando rua, número, bairro, cidade, estado e país).
3. **Inserção no PostGIS**: Os dados de endereço, juntamente com as coordenadas obtidas, são inseridos na tabela `endereco` em um banco de dados PostGIS.

## Entradas

O evento esperado pela função deve conter o endereço no corpo, no seguinte formato:

```json
{
  "rua": "Nome da Rua",
  "bairro": "Nome do Bairro",
  "numero": "123",
  "cidade": "Nome da Cidade",
  "estado": "Nome do Estado",
  "zip": "12345-678",
  "pais": "Nome do País",
  "complemento": "Apartamento 456"
}
```

## Saída

A função retorna um objeto JSON com o status da operação. Em caso de sucesso:

```json
{
  "statusCode": 200,
  "body": "{\"action\": \"POST\", \"message\": \"Endereco salvo com sucesso\"}"
}
```

Se ocorrer um erro durante o processamento, o status code será 500, com uma mensagem de erro:

```json
{
  "statusCode": 500,
  "body": "{\"action\": \"POST\", \"message\": \"[mensagem de erro]\"}"
}
```

## Variáveis de Ambiente

- `connection_bonanza_gis`: String de conexão para o banco de dados PostGIS. Exemplo: `postgresql://user:password@host:port/dbname`.

## Erros Comuns

- **Erro de Geocodificação**: Se o endereço fornecido não puder ser geocodificado, a função ainda tentará inserir o endereço no banco de dados, mas com NULL para latitude e longitude.
- **Erro de Conexão com o PostGIS**: Verifique se a string de conexão está correta e se o banco de dados está acessível.
- **GeocoderTimedOut**: Ocorre quando a geocodificação falha devido a uma espera muito longa. A função tenta novamente até 5 vezes antes de falhar.

## Considerações de Limitação

- **Limites da API de Geocodificação**: O serviço Nominatim tem limites de taxa de requisições por segundo. Em caso de uso intensivo, considere implementar uma política de backoff ou usar uma API paga.
- **Timeout do Lambda**: Se o processo de geocodificação ou inserção no banco de dados demorar muito, considere ajustar o tempo limite da função Lambda.
