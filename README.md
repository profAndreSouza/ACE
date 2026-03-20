# Sistema de Acompanhamento de Produção com IoT e Recomendação

## 1. Visão Geral

Este projeto tem como objetivo desenvolver um sistema completo de acompanhamento de produção de veículos, integrando:

- Backend (API REST)
- Frontend Web e Mobile
- Pipeline de dados IoT
- Banco de dados relacional e temporal
- Sistema de recomendação baseado em perfil

O sistema permite que clientes acompanhem o status de produção de seus veículos em tempo quase real e recebam recomendações personalizadas.


## 2. Arquitetura do Sistema

O sistema é dividido em três grandes blocos:

### 2.1 Camada IoT (Stack MING)

Responsável pela coleta e armazenamento de dados brutos de produção:

- Dispositivo (ESP32 simulado)
- MQTT (mensageria)
- Node-RED (processamento)
- InfluxDB (dados temporais)
- Grafana (visualização)

Os dados armazenados no InfluxDB representam eventos de produção, como:

- Entrada em etapa
- Saída de etapa


### 2.2 Backend (API)

Responsável por:

- Autenticação de usuários
- Regras de negócio
- Consolidação de dados de produção
- Integração com sistema de recomendação
- Exposição de APIs REST

Tecnologias:

- .NET / Java (dependendo da versão do grupo)
- PostgreSQL (dados estruturados)
- InfluxDB (dados de eventos)
- JWT (autenticação)


### 2.3 Frontend

Aplicações cliente responsáveis pela interação com o usuário:

- Web: React
- Mobile: React Native (Expo)


### 2.4 Sistema de Recomendação

Serviço em Python responsável por:

- Analisar perfil do cliente
- Gerar sugestões de produtos/serviços

A comunicação ocorre via API com o backend.


## 3. Fluxo de Dados

1. Dispositivos enviam eventos para o MQTT
2. Node-RED processa e grava no InfluxDB
3. Backend consome periodicamente os dados do InfluxDB
4. Backend consolida os dados no PostgreSQL
5. Frontend consome o backend
6. Backend consulta o sistema de recomendação
7. Sistema de recomendação retorna sugestões


## 4. Escopo do MVP

O MVP contempla as seguintes funcionalidades:

### 4.1 Autenticação

- Cadastro de usuário
- Login com geração de token

### 4.2 Gestão de Cliente

- Visualização de perfil

### 4.3 Pedido

- Criação de pedido
- Consulta de pedido

### 4.4 Veículo

- Consulta de veículo

### 4.5 Produção

- Visualização do status atual
- Histórico de etapas (timeline)

### 4.6 Recomendação

- Sugestões personalizadas com base no perfil do cliente


## 5. Endpoints Principais

### Autenticação

- POST /api/auth/register
- POST /api/auth/login

### Cliente

- GET /api/client/me

### Pedido

- POST /api/orders
- GET /api/orders/{id}
- GET /api/orders/my

### Veículo

- GET /api/vehicles/{id}

### Produção

- GET /api/production/{orderId}

### Recomendação

- GET /api/recommendations/{clientId}


## 6. Integração com IoT

Os dados de produção são armazenados no InfluxDB no formato de eventos:

Exemplo:

```

carro=1 etapa=montagem evento=entrada
carro=1 etapa=montagem evento=saida

```

O backend executa um processo periódico que:

- Lê os eventos do InfluxDB
- Consolida as informações
- Atualiza o banco relacional


## 7. Modelo de Comunicação

- Frontend não acessa banco diretamente
- Sistema de recomendação não acessa banco diretamente
- Toda comunicação passa pelo backend


## 8. Estrutura Esperada do Backend

- Controller: endpoints REST
- Service: regras de negócio
- Repository: acesso a dados
- DTO: objetos de transferência
- Entity/Model: entidades do domínio


## 9. Telas do MVP

### Usuário

- Login
- Cadastro
- Home
- Perfil

### Funcionalidades

- Visualização de pedido
- Acompanhamento de produção (timeline)
- Visualização de veículo
- Recomendações


## 10. Requisitos Não Funcionais

- API REST stateless
- Autenticação baseada em token
- Separação de responsabilidades
- Escalabilidade básica
- Código organizado por camadas


## 11. Roadmap do Projeto

1. Implementação de autenticação
2. Cadastro de clientes
3. Cadastro e consulta de pedidos
4. Integração com dados de produção
5. Desenvolvimento do frontend
6. Implementação do sistema de recomendação
7. Integração final


## 12. Objetivo Acadêmico

Este projeto tem como finalidade:

- Aplicar conceitos de arquitetura de software
- Trabalhar com integração de sistemas
- Utilizar tecnologias modernas de mercado
- Simular um cenário real de indústria 4.0
- Desenvolver soluções fullstack com IoT e IA
