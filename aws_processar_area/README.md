# AWS Lambda - Processamento de Arquivos Geoespaciais e Salvamento em Banco de Dados PostGIS

## Descrição

Esta função AWS Lambda processa arquivos geoespaciais e salva os dados em um banco de dados PostGIS. A função realiza as seguintes etapas:

1. **Recebe um evento S3** com um arquivo geoespacial (KML, GeoJSON, SHP ou ZIP contendo esses arquivos).
2. **Baixa o arquivo do S3** para o ambiente temporário da Lambda.
3. **Descompacta o arquivo** se for um ZIP e processa os arquivos extraídos.
4. **Geoprocessa o arquivo** para garantir que esteja no formato correto e adiciona informações adicionais.
5. **Carrega os dados** para uma tabela chamada `zona_risco` em um banco de dados PostGIS.

## Pré-requisitos

### Dependências

Certifique-se de que sua função Lambda tenha as seguintes dependências instaladas no ambiente:

- `geopandas`
- `shapely`
- `boto3`
- `sqlalchemy`
- `psycopg2-binary`

Essas bibliotecas podem ser incluídas ao criar um pacote de implantação customizado ou usando camadas Lambda.

### Configuração do Ambiente

A função Lambda espera que a string de conexão ao banco de dados PostGIS seja passada como uma variável de ambiente chamada `connection_bonanza_gis`.

## Como Funciona

1. **Entrada via Evento S3**: A função é acionada por um evento S3 que contém o nome do bucket e a chave do objeto (o arquivo a ser processado).
2. **Baixando o Arquivo**: O arquivo é baixado do bucket S3 para o diretório temporário `/tmp/`.
3. **Processamento de Arquivos**:
   - Se o arquivo for um ZIP, ele é descompactado e os arquivos extraídos são processados.
   - Os arquivos suportados (KML, GeoJSON, SHP) são carregados em um GeoDataFrame.
4. **Preparação dos Dados**: O GeoDataFrame é preparado e validado, e colunas adicionais são adicionadas.
5. **Upload para PostGIS**: Os dados são carregados na tabela `zona_risco` do banco de dados PostGIS.

## Entradas

O evento esperado pela função S3 deve seguir o formato padrão de notificação de eventos do S3. Exemplo:

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

## Saída

A função retorna um objeto JSON com o status da operação. Em caso de sucesso:

```json
{
  "statusCode": 200,
  "body": "Arquivo [nome-do-arquivo] processado e carregado para a tabela zona_risco."
}
```

Se ocorrer um erro durante o processamento, o status code será 500, com uma mensagem de erro:

```json
{
  "statusCode": 500,
  "body": "Erro ao processar o arquivo: [mensagem de erro]"
}
```

## Variáveis de Ambiente

- `connection_bonanza_gis`: String de conexão para o banco de dados PostGIS. Exemplo: `postgresql://user:password@host:port/dbname`.

## Erros Comuns

- **Erro ao Baixar o Arquivo do S3**: Verifique se a chave do objeto e o bucket estão corretos e se a função Lambda tem permissões apropriadas.
- **Erro ao Processar o Arquivo**: Verifique a extensão do arquivo e certifique-se de que ele está no formato suportado.
- **Erro de Conexão com o PostGIS**: Verifique se a string de conexão está correta e se o banco de dados está acessível.
- **Geometria Inválida**: Se o arquivo contém geometria inválida, a função tentará corrigir isso, mas erros podem ocorrer.

## Considerações de Limitação

- **Limites de Armazenamento Temporário**: A função Lambda tem um limite de armazenamento temporário (/tmp). Certifique-se de que os arquivos não excedam esse limite.
- **Limites de Tempo de Execução**: Se o processamento ou o upload para o banco de dados levar muito tempo, considere ajustar o tempo limite da função Lambda.