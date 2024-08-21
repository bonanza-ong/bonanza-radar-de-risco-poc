# AWS Bonanza SAM Project

## Descrição

Este projeto utiliza o AWS Serverless Application Model (SAM) para criar uma aplicação serverless que processa arquivos geoespaciais e realiza geocodificação de endereços. A aplicação inclui:

1. Uma função Lambda para processar arquivos geoespaciais enviados para um bucket S3 e salvar os dados processados em um banco de dados PostGIS.
2. Uma função Lambda para geocodificar endereços recebidos via API Gateway e salvar os resultados no banco de dados PostGIS.
3. Um banco de dados PostgreSQL com extensão PostGIS gerenciado pela AWS RDS.
4. Um bucket S3 para armazenamento dos arquivos geoespaciais.
5. Um Secrets Manager para armazenar credenciais sensíveis do banco de dados.
6. Um API Gateway configurado para gerenciar solicitações HTTP para a função de geocodificação de endereços.

## Estrutura do Projeto

O projeto está estruturado da seguinte forma:

.
├── aws_processar_area/ # Código da Lambda para processar arquivos geoespaciais
├── aws_endereco/ # Código da Lambda para geocodificação de endereços
├── template.yaml # Template AWS SAM
└── README.md # Este arquivo README

markdown
Copiar código

## Recursos

O projeto define os seguintes recursos usando o AWS CloudFormation:

### 1. Banco de Dados RDS (PostgreSQL com PostGIS)

- Um banco de dados PostgreSQL com extensão PostGIS gerenciado pelo AWS RDS.
- Configuração para autenticação IAM e armazenamento seguro da senha no AWS Secrets Manager.

### 2. Bucket S3

- Um bucket S3 chamado `bonanza-gis` para armazenar arquivos geoespaciais que serão processados pela função Lambda.

### 3. Funções Lambda

- **Processar Arquivos Geoespaciais**: Esta função é acionada quando um novo arquivo é enviado para o bucket S3, processa o arquivo geoespacial e armazena os dados em uma tabela PostGIS.
- **Geocodificação de Endereços**: Esta função recebe requisições POST através do API Gateway, realiza a geocodificação de endereços usando a biblioteca `geopy` e armazena o resultado no banco de dados PostGIS.

### 4. API Gateway

- Uma API REST configurada para gerenciar solicitações HTTP para a função de geocodificação de endereços.

### 5. Secrets Manager

- Um Secret no AWS Secrets Manager para armazenar as credenciais sensíveis (senha) do banco de dados PostgreSQL.

## Pré-requisitos

### Dependências Globais

Certifique-se de que você tenha o AWS CLI, SAM CLI e Docker instalados na sua máquina para testar e fazer o deploy da aplicação.

- [Instalação do AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [Instalação do AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Instalação do Docker](https://docs.docker.com/get-docker/)

### Dependências do Projeto

As funções Lambda deste projeto utilizam as seguintes dependências Python:

- **Lambda de Processamento de Arquivos Geoespaciais**:
  - `geopandas`
  - `boto3`
  - `shapely`
  - `sqlalchemy`
  - `psycopg2-binary`

- **Lambda de Geocodificação de Endereços**:
  - `sqlalchemy`
  - `geopy`
  - `psycopg2-binary`

Você pode instalar essas dependências no seu ambiente de desenvolvimento com o `pip` ou incluir as bibliotecas necessárias nas camadas Lambda.

## Como Executar

### 1. Clonar o Repositório

Clone o repositório para o seu ambiente de desenvolvimento local:

```bash
git clone https://github.com/seu-usuario/aws_bonanza_sam.git
cd aws_bonanza_sam
2. Instalar Dependências
Instale as dependências Python necessárias para as funções Lambda:

bash
Copiar código
pip install -r aws_processar_area/requirements.txt -t aws_processar_area/
pip install -r aws_endereco/requirements.txt -t aws_endereco/
3. Configuração de Variáveis de Ambiente
Certifique-se de configurar as seguintes variáveis de ambiente no AWS Lambda:

connection_bonanza_gis: String de conexão para o banco de dados PostGIS. Exemplo: postgresql://user:password@host:port/dbname.
4. Testar Localmente
Você pode testar a aplicação localmente usando o SAM CLI:

bash
Copiar código
sam local start-api
5. Deploy para AWS
Faça o deploy da aplicação para a AWS usando o SAM CLI:

bash
Copiar código
sam deploy --guided
Siga as instruções para configurar o deploy, incluindo a definição dos parâmetros como DBSecretName e DBUsername.

Considerações de Segurança
Segurança do Banco de Dados: Certifique-se de que a configuração de segurança do grupo de segurança do RDS esteja adequada, permitindo acesso apenas de IPs confiáveis.
Gerenciamento de Segredos: Use o AWS Secrets Manager para armazenar credenciais sensíveis, como a senha do banco de dados.
Permissões IAM: As permissões IAM para as funções Lambda estão configuradas para permitir acesso mínimo necessário aos recursos, incluindo RDS, S3 e Secrets Manager.