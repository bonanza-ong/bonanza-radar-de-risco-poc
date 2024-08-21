# POC Área de Risco - Bonanza GIS
## Descrição

O projeto **POC Área de Risco** utiliza o AWS Serverless Application Model (SAM) para configurar e gerenciar uma aplicação serverless dedicada ao processamento e armazenamento de dados geoespaciais. A arquitetura inclui:

1. **Banco de Dados RDS PostgreSQL com PostGIS**: Armazena dados geoespaciais.
2. **Bucket S3**: Armazena arquivos geoespaciais que são processados.
3. **Funções AWS Lambda**: Processam dados de arquivos e interagem com o banco de dados e o S3.
4. **API Gateway**: Fornece uma interface para interagir com uma das funções Lambda via HTTP.

## Arquitetura

### Recursos

1. **RDS PostgreSQL Instance** (`RDSInstance`): 
   - Banco de dados PostgreSQL configurado com a extensão PostGIS.
   - Armazena dados geoespaciais.
   - Utiliza a variável de ambiente `DBSecretName` para obter a senha do banco.

2. **Secrets Manager Secret** (`RDSSecret`):
   - Armazena a senha do banco de dados de forma segura.
   - É referenciado pelo `RDSInstance` para autenticação.

3. **S3 Bucket** (`S3Bucket`):
   - Armazena arquivos geoespaciais a serem processados pelas funções Lambda.
   - Configurado com a política para permitir acesso às funções Lambda.

4. **Lambda Execution Role** (`LambdaExecutionRole`):
   - Permite que as funções Lambda acessem o RDS, Secrets Manager, S3 e CloudWatch Logs.

5. **Funções Lambda**:
   - **`ProcessShapefile`**:
     - Processa arquivos geoespaciais (KML, GeoJSON, SHP, ZIP) armazenados no bucket S3.
     - Converte e carrega dados para a tabela `zona_risco` no banco de dados PostGIS.
   - **`EnderecoPost`**:
     - Recebe dados de endereço via API e os insere na tabela `endereco` no banco de dados PostGIS.

6. **API Gateway** (`ApiGatewayApi`):
   - Fornece uma API REST para a função Lambda `EnderecoPost`.
   - Requer autenticação por chave de API.
   - Configurada com um modelo de solicitação para validação dos dados do endereço.

### Parâmetros

- **`DBSecretName`**: Nome do segredo no Secrets Manager que contém a senha do banco de dados.
- **`DBUsername`**: Nome do usuário do banco de dados.

### Configuração

1. **Banco de Dados RDS**: 
   - A instância do banco de dados é criada com as configurações especificadas, incluindo o grupo de sub-redes e o grupo de segurança.

2. **Secrets Manager**: 
   - O segredo para a senha do banco é gerado e armazenado no Secrets Manager.

3. **Bucket S3**: 
   - O bucket é configurado para armazenar arquivos e permitir o acesso necessário para a função Lambda.

4. **Funções Lambda**: 
   - A função `ProcessShapefile` é configurada para ser acionada por eventos de criação de objetos no bucket S3.
   - A função `EnderecoPost` é configurada para expor uma API via API Gateway.

5. **API Gateway**: 
   - Configurado para expor uma API REST com um modelo de solicitação para validação dos dados de entrada.

## Como Usar

### Passo a Passo

1. **Deploy da Aplicação**:
   - Use o AWS SAM CLI para implantar a stack.
     ```bash
     sam deploy --guided
     ```
   - Forneça os parâmetros necessários durante o processo de implantação, como o nome do segredo e o nome de usuário do banco de dados.

2. **Upload de Arquivos para o S3**:
   - Faça o upload dos arquivos geoespaciais para o bucket S3 (`bonanza-gis`).
   - A função `ProcessShapefile` será acionada automaticamente para processar esses arquivos.

3. **Interagindo com a API**:
   - Envie uma solicitação POST para a API Gateway para adicionar um endereço ao banco de dados.
   - A URL da API será fornecida após o deploy.

4. **Monitoramento e Logs**:
   - Acompanhe os logs das funções Lambda no CloudWatch para monitorar o processamento e depuração.

## Variáveis de Ambiente

- **`connection_bonanza_gis`**: String de conexão para o banco de dados PostGIS, usada pelas funções Lambda. Exemplo: `postgresql://user:password@host:port/dbname`.

## Erros Comuns

- **Erro ao Acessar o RDS**: Verifique as permissões do grupo de segurança e a string de conexão.
- **Erro ao Processar Arquivos**: Verifique os arquivos e formatos suportados.
- **Erro na API**: Verifique a configuração da API Gateway e as permissões da função Lambda.

## Considerações de Limitação

- **Limites de Tamanho do Arquivo**: A função Lambda possui um limite de tamanho de arquivo que pode processar no diretório `/tmp`.
- **Limites de Tempo de Execução**: Ajuste o tempo limite da função Lambda conforme necessário para processar arquivos grandes ou operações complexas.