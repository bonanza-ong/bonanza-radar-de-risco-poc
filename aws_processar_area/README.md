# AWS Lambda - Processamento de Arquivos Geoespaciais

## Descrição

Esta função AWS Lambda é responsável por processar arquivos geoespaciais (como arquivos KML, GeoJSON e Shapefiles) que são enviados para um bucket S3. A função realiza as seguintes etapas:

1. Baixa o arquivo do S3.
2. Descompacta o arquivo, caso ele esteja em formato ZIP.
3. Carrega o arquivo em um GeoDataFrame (via `geopandas`).
4. Prepara e padroniza os dados.
5. Carrega os dados geoespaciais processados em uma tabela PostGIS (`zona_risco`).

## Pré-requisitos

### Dependências

Certifique-se de que sua função Lambda tenha as seguintes dependências instaladas no ambiente:

- `geopandas`
- `boto3`
- `shapely`
- `sqlalchemy`
- `psycopg2-binary`

Essas bibliotecas podem ser incluídas ao criar um pacote de implantação customizado ou usando camadas Lambda.

### Configuração do Ambiente

A função Lambda espera que a string de conexão ao banco de dados PostGIS seja passada como uma variável de ambiente chamada `connection_bonanza_gis`.

## Como Funciona

1. **Evento S3**: A função é acionada por eventos do S3. Quando um arquivo é carregado no bucket S3 configurado, a função Lambda é executada.
2. **Processamento de Arquivos**: Dependendo do tipo de arquivo (KML, GeoJSON, Shapefile), a função carrega o arquivo em um `GeoDataFrame`, padroniza as colunas, e corrige possíveis problemas de geometria.
3. **Upload para o PostGIS**: Após o processamento, os dados geoespaciais são carregados na tabela `zona_risco` no banco de dados PostGIS.

## Entradas

O evento esperado pela função deve seguir o formato padrão de eventos do S3, com informações sobre o bucket e o arquivo carregado.

Exemplo de evento S3:

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "nome-do-bucket"
        },
        "object": {
          "key": "caminho/do/arquivo.zip"
        }
      }
    }
  ]
}

Saída
A função retorna um objeto JSON com o status da operação. Em caso de sucesso:

json
Copiar código
{
  "statusCode": 200,
  "body": "Arquivo processado e carregado para a tabela zona_risco."
}
Se ocorrer um erro durante o processamento, o status code será 500, com uma mensagem de erro:

json
Copiar código
{
  "statusCode": 500,
  "body": "Erro ao processar o arquivo: [mensagem de erro]"
}
Variáveis de Ambiente
connection_bonanza_gis: String de conexão para o banco de dados PostGIS. Exemplo: postgresql://user:password@host:port/dbname.
Erros Comuns
Erro ao Baixar Arquivo do S3: Verifique se o arquivo existe no bucket S3 e se a função Lambda possui as permissões corretas para acessar o bucket.
Formato de Arquivo Não Suportado: Atualmente, a função suporta apenas arquivos nos formatos .kml, .geojson, .shp, e .zip. Outros formatos serão ignorados.
Erro de Conexão com o PostGIS: Certifique-se de que a string de conexão esteja correta e que o banco de dados esteja acessível.
Considerações de Limitação
Espaço de Armazenamento: O ambiente Lambda oferece um armazenamento temporário de até 512MB no diretório /tmp/. Certifique-se de que o tamanho dos arquivos processados não exceda essa capacidade.
Timeout: Dependendo do tamanho dos arquivos, o tempo limite da função Lambda pode precisar ser ajustado. O padrão é 3 segundos, mas pode ser configurado para até 15 minutos.