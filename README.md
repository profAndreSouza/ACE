# Sistema de Acompanhamento de Produção — ACE

Sistema completo para acompanhamento em tempo real da produção de veículos, integrando IoT, backend REST, frontend web/mobile e recomendação por IA.

---

## Visão Geral

O projeto é um **monorepo** com cinco aplicações independentes que se comunicam via rede Docker:

| Aplicação | Tecnologia | Porta |
|-----------|-----------|-------|
| `simulador` | Python | — |
| `backend` | .NET 8 | 5000 |
| `frontend` | React / Expo | 19006 |
| `ai` | Python | 8000 |
| InfluxDB | — | 8086 |
| PostgreSQL | — | 5432 |
| Node-RED | — | 1880 |
| Grafana | — | 3000 |
| MQTT (Mosquitto) | — | 1883 |

---

## Estrutura do Repositório

```
.
├── docker-compose.yml
├── mosquitto/
│   └── mosquitto.conf
├── simulador/          # Dispositivo IoT simulado (Python)
├── backend/            # API REST (.NET 8)
├── frontend/           # Web + Mobile (React / Expo)
└── ai/                 # Serviço de recomendação (Python)
```

---

## Arquitetura

```
[ Simulador Python ]
        |  MQTT (1883)
        v
  [ Mosquitto ]
        |
        v
   [ Node-RED ]  ──────────────> [ Grafana ]
        |                              ^
        v                              |
   [ InfluxDB ]  <─────────────────────┘
        ^
        | leitura periódica
        |
   [ Backend .NET ] ──> [ PostgreSQL ]
        |
        |──> [ AI Python ] (recomendações)
        |
        v
   [ Frontend React/Expo ]
```

### Fluxo de dados

1. O **simulador** publica eventos de produção via MQTT (tópico configurado no broker Mosquitto).
2. O **Node-RED** consome as mensagens MQTT e as grava no **InfluxDB** como séries temporais.
3. O **backend** lê periodicamente o InfluxDB, consolida os dados de produção e os persiste no **PostgreSQL**.
4. O **frontend** consome exclusivamente o backend via API REST.
5. O **serviço de IA** é consultado pelo backend para gerar recomendações personalizadas por cliente.
6. O **Grafana** se conecta ao InfluxDB para visualização dos dados brutos de produção.

---

## Stack IoT (MING)

| Componente | Função |
|-----------|--------|
| **M**osquitto (MQTT) | Broker de mensageria entre o simulador e o Node-RED |
| **I**nfluxDB 2 | Armazenamento de séries temporais dos eventos de produção |
| **N**ode-RED | Processamento e roteamento das mensagens MQTT → InfluxDB |
| **G**rafana | Dashboard de visualização dos dados brutos |

### Formato dos eventos no InfluxDB

```
measurement: producao
tags:   carro=<id>   etapa=<nome>
fields: evento=<entrada|saida>
```

Exemplo de mensagem MQTT publicada pelo simulador:

```json
{
  "carro": "1",
  "etapa": "montagem",
  "evento": "entrada"
}
```

---

## Aplicações

### Simulador (`/simulador`)

Aplicação Python que simula um dispositivo IoT publicando eventos de produção via MQTT.

- Construída com `Dockerfile` próprio.
- Aguarda o broker MQTT estar disponível antes de publicar.
- Publica mensagens no formato JSON no tópico configurado.

### Backend (`/backend`)

API REST em .NET 8 responsável por:

- Autenticação de usuários (JWT)
- Regras de negócio e consolidação dos dados
- Leitura periódica do InfluxDB e persistência no PostgreSQL
- Integração com o serviço de recomendação (IA)
- Exposição dos endpoints para o frontend

**Organização interna:**

```
backend/
├── Controllers/    # Endpoints REST
├── Services/       # Regras de negócio
├── Repositories/   # Acesso a dados
├── DTOs/           # Objetos de transferência
└── Models/         # Entidades do domínio
```

**Variáveis de ambiente relevantes:**

```
ConnectionStrings__Postgres=Host=postgres;Database=dbace;Username=admin;Password=admin123
InfluxDB__Url=http://influxdb:8086
InfluxDB__Token=<token gerado no setup>
InfluxDB__Org=senai
InfluxDB__Bucket=linha_producao
JwtSettings__Secret=<secret>
```

### Frontend (`/frontend`)

Aplicação React (web) e React Native com Expo (mobile).

- Porta `19006` exposta para acesso web via Expo.
- Consome exclusivamente a API do backend.
- Não acessa banco de dados diretamente.

### Serviço de IA (`/ai`)

Serviço Python que expõe uma API REST na porta `8000` com endpoints de recomendação.

- Recebe dados do perfil do cliente enviados pelo backend.
- Retorna sugestões personalizadas de produtos e serviços.

---

## Endpoints da API (Backend)

### Autenticação

```
POST /api/auth/register
POST /api/auth/login
```

### Cliente

```
GET /api/client/me
```

### Pedidos

```
POST /api/orders
GET  /api/orders/{id}
GET  /api/orders/my
```

### Veículo

```
GET /api/vehicles/{id}
```

### Produção

```
GET /api/production/{orderId}
```

### Recomendação

```
GET /api/recommendations/{clientId}
```

---

## Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados.

### Subir todos os serviços

```bash
docker compose up -d
```

### Acessar os serviços

| Serviço | URL |
|---------|-----|
| Backend API | http://localhost:5000 |
| Frontend (Expo Web) | http://localhost:19006 |
| Serviço de IA | http://localhost:8000 |
| Node-RED | http://localhost:1880 |
| InfluxDB | http://localhost:8086 |
| Grafana | http://localhost:3000 |
| MQTT | mqtt://localhost:1883 |

### Credenciais padrão

| Serviço | Usuário | Senha |
|---------|---------|-------|
| InfluxDB | `admin` | `admin123` |
| PostgreSQL | `admin` | `admin123` |
| Grafana | `admin` | `admin` (padrão da imagem) |

> **InfluxDB:** na primeira inicialização, acesse `http://localhost:8086` para obter o token de API. Configure esse token nas variáveis de ambiente do backend.

### Desenvolvimento individual

Os containers de `backend`, `frontend` e `ai` montam os diretórios locais como volumes — as alterações em código refletem sem precisar reconstruir a imagem.

Para iniciar o servidor de desenvolvimento dentro de cada container:

```bash
# Backend (.NET)
docker exec -it backend-dev bash
dotnet run

# Frontend (Expo)
docker exec -it frontend-dev bash
npm install
npx expo start --web

# IA (Python)
docker exec -it ai-dev bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Configuração do Node-RED

Após subir os containers, acesse `http://localhost:1880` e configure o fluxo:

1. **MQTT In** → conectar ao broker `mqtt` (porta `1883`) no tópico de produção.
2. **Function** → transformar o payload para o formato de medição do InfluxDB.
3. **InfluxDB Out** → gravar na organização `senai`, bucket `linha_producao`.

---

## MVP — Funcionalidades

- Cadastro e login de usuários (JWT)
- Visualização de perfil do cliente
- Criação e consulta de pedidos
- Consulta de veículo
- Acompanhamento de produção com timeline de etapas
- Recomendações personalizadas por perfil

---

## Requisitos Não Funcionais

- API REST stateless com autenticação baseada em token
- Frontend desacoplado do banco de dados (tudo via backend)
- Serviço de IA desacoplado do banco (comunicação somente via backend)
- Separação de responsabilidades por camadas
- Containerização completa com Docker Compose

---

## Roadmap

1. Autenticação (register + login)
2. Gestão de clientes e perfil
3. Cadastro e consulta de pedidos
4. Pipeline IoT: simulador → MQTT → Node-RED → InfluxDB
5. Integração backend ↔ InfluxDB → PostgreSQL
6. Desenvolvimento do frontend
7. Serviço de recomendação (IA)
8. Integração final e testes

---

## Contexto Acadêmico

Projeto desenvolvido como exercício prático de:

- Arquitetura de software em camadas
- Integração de sistemas heterogêneos
- Tecnologias de mercado (IoT, REST, containers, séries temporais)
- Simulação de cenário real de Indústria 4.0
- Desenvolvimento fullstack com IoT e IA