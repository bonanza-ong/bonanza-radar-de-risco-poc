# Lambda Function: Processamento de Arquivos Geoespaciais e Upload para PostGIS

## Descrição

Esta função Lambda é projetada para processar arquivos geoespaciais (como KML, GeoJSON e Shapefiles) carregados em um bucket S3, extrair informações geométricas, prepará-las em um `GeoDataFrame` e carregar os dados resultantes em uma tabela PostGIS.

### Funcionamento Geral

1. **Trigger pelo S3**: A função é disparada sempre que um arquivo é carregado no bucket S3.
2. **Download do Arquivo**: O arquivo é baixado da S3 para o ambiente temporário `/tmp` na Lambda.
3. **Processamento de Arquivo**:
   - Se o arquivo for um `.zip`, ele é descompactado.
   - Dependendo do tipo de arquivo (KML, GeoJSON, Shapefile), ele é carregado em um `GeoDataFrame` usando o `geopandas`.
4. **Preparação do GeoDataFrame**: A função `prepare_gdf` garante que o GeoDataFrame contenha as colunas necessárias, como `nome`, `descricao`, `em_risco`, `created_at`, `area_code` e `area_risco`.
5. **Upload para PostGIS**: Os dados preparados são enviados para uma tabela específica no banco de dados PostGIS.

## Estrutura do Projeto

```bash
├── lambda_function.py       # Código principal da Lambda
├── README.md                # Este arquivo
└── requirements.txt         # Dependências Python para a Lambda
```

## Dependências

A função Lambda depende das seguintes bibliotecas Python:

- `geopandas`
- `boto3`
- `sqlalchemy`
- `shapely`

Estas dependências devem ser incluídas no pacote de implantação ou especificadas no `requirements.txt`.

## Variáveis de Ambiente

A função Lambda requer as seguintes variáveis de ambiente:

- `connection_bonanza_gis`: String de conexão para o banco de dados PostGIS onde os dados serão armazenados.

## Eventos de Trigger

A função é disparada por eventos de `PUT` em um bucket S3. O evento fornece detalhes sobre o arquivo carregado, incluindo o nome do bucket e a chave do arquivo.

## Como a Função Funciona

### 1. Preparação do GeoDataFrame

A função `prepare_gdf` ajusta o GeoDataFrame carregado para garantir que ele tenha a estrutura esperada:

- Combina geometrias se necessário.
- Adiciona colunas padrão como `nome`, `descricao`, `em_risco`, `created_at`, e `area_code`.
- Define o CRS (Sistema de Referência de Coordenadas) para EPSG:4326.

### 2. Upload para PostGIS

A função `upload_to_postgis` utiliza `SQLAlchemy` para inserir o GeoDataFrame na tabela PostGIS especificada.

### 3. Tratamento de Erros

Se ocorrer algum erro durante o download, processamento ou upload, a função capturará a exceção, imprimirá uma mensagem de erro e retornará um código de status 500.

## Exemplo de Evento

Aqui está um exemplo de evento S3 que acionaria a função Lambda:

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "nome-do-bucket"
        },
        "object": {
          "key": "caminho/para/o/arquivo.zip"
        }
      }
    }
  ]
}
```

## Logs e Monitoramento

Os logs da função são gravados no Amazon CloudWatch, onde você pode visualizar mensagens de erro e status de upload.

## Notas Adicionais

- A função suporta os formatos de arquivo `.kml`, `.geojson`, e `.shp`. Outros formatos serão ignorados.
- O ambiente de execução da Lambda tem um limite de espaço de armazenamento de 512 MB no diretório `/tmp`, então arquivos maiores que este valor podem não ser processados corretamente.