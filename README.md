# Projeto: Upload e Verificação de Endereços em Áreas de Risco

Este projeto tem como objetivo processar arquivos shapefile carregados em um bucket S3 da AWS, verificar se os endereços armazenados em um banco de dados PostgreSQL com extensão PostGIS estão em áreas de risco e salvar os resultados em uma nova tabela no RDS.

## Arquitetura do Projeto

1. **Upload do Shapefile:**
   - O usuário faz o upload de um shapefile para um bucket S3 da AWS.
   - Alternativamente, o usuário pode enviar o endereço diretamente via uma API REST.

2. **Disparo de Função Lambda:**
   - Um evento do Amazon CloudWatch é configurado para monitorar o bucket S3. Quando um shapefile é carregado, um evento é disparado, iniciando uma função Lambda escrita em Python.

3. **Processamento na Função Lambda:**
   - A Lambda realiza o download do shapefile do S3 e o carrega no banco de dados PostgreSQL, que possui a extensão PostGIS.
   - A Lambda, então, realiza uma varredura dos endereços armazenados no banco de dados para verificar se algum deles está localizado dentro das zonas de risco definidas no shapefile.

4. **Armazenamento dos Resultados:**
   - A informação de quais endereços estão em zonas de risco, contendo `zona_id` e `endereco_id`, é salva em uma nova tabela no RDS.

## Tecnologias Utilizadas

- **AWS S3**: Armazenamento dos shapefiles.
- **AWS Lambda**: Execução do código Python para processar o shapefile e verificar endereços.
- **AWS CloudWatch**: Monitoramento do bucket S3 e acionamento das Lambdas.
- **PostgreSQL com PostGIS**: Armazenamento dos endereços e zonas de risco, com suporte a consultas espaciais.
- **AWS SAM (Serverless Application Model)**: Utilizado para definir a infraestrutura como código e gerenciar o deploy das Lambdas.
