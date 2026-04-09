# Backend — API REST

API REST do sistema de acompanhamento de produção, desenvolvida em **.NET 8 (C#)**.

Responsável por autenticação, regras de negócio, leitura dos dados de produção do InfluxDB, persistência no PostgreSQL e integração com o serviço de recomendação.

---

## Tecnologias

- [.NET 8](https://dotnet.microsoft.com/) — framework principal
- [ASP.NET Core](https://learn.microsoft.com/aspnet/core) — camada web / API REST
- [Entity Framework Core](https://learn.microsoft.com/ef/core) — ORM para PostgreSQL
- [Npgsql](https://www.npgsql.org/) — driver PostgreSQL
- [InfluxDB.Client](https://github.com/influxdata/influxdb-client-csharp) — leitura dos dados IoT
- [JWT Bearer](https://learn.microsoft.com/aspnet/core/security/authentication/jwt-authn) — autenticação stateless

---

## Estrutura de Pastas

```
backend/
├── Controllers/            # Endpoints REST (recebem e respondem requisições)
│   ├── AuthController.cs
│   ├── ClientController.cs
│   ├── OrderController.cs
│   ├── VehicleController.cs
│   ├── ProductionController.cs
│   └── RecommendationController.cs
│
├── Services/               # Regras de negócio
│   ├── AuthService.cs
│   ├── OrderService.cs
│   ├── ProductionService.cs
│   └── RecommendationService.cs
│
├── Repositories/           # Acesso a dados (PostgreSQL e InfluxDB)
│   ├── UserRepository.cs
│   ├── OrderRepository.cs
│   ├── VehicleRepository.cs
│   └── ProductionRepository.cs
│
├── Models/                 # Entidades do domínio (tabelas do banco)
│   ├── User.cs
│   ├── Client.cs
│   ├── Order.cs
│   ├── Vehicle.cs
│   └── ProductionEvent.cs
│
├── DTOs/                   # Objetos de transferência (request e response)
│   ├── Auth/
│   ├── Order/
│   ├── Production/
│   └── Recommendation/
│
├── Data/
│   └── AppDbContext.cs     # Contexto do Entity Framework
│
├── Jobs/                   # Processos periódicos (leitura do InfluxDB)
│   └── InfluxSyncJob.cs
│
├── appsettings.json        # Configurações gerais
├── appsettings.Development.json
└── Program.cs              # Ponto de entrada e configuração de serviços
```

---

## Configuração

### Variáveis de ambiente / appsettings

Configure o arquivo `appsettings.Development.json` (nunca suba dados sensíveis no repositório):

```json
{
  "ConnectionStrings": {
    "Postgres": "Host=localhost;Port=5432;Database=dbace;Username=admin;Password=admin123"
  },
  "InfluxDB": {
    "Url": "http://localhost:8086",
    "Token": "<token-gerado-no-setup-do-influxdb>",
    "Org": "senai",
    "Bucket": "linha_producao"
  },
  "JwtSettings": {
    "Secret": "<chave-secreta-minimo-32-chars>",
    "ExpiresInHours": 8
  },
  "RecommendationService": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

> **Token do InfluxDB:** após subir os containers com `docker compose up -d`, acesse `http://localhost:8086`, faça login com `admin / admin123` e gere um token em **Data → API Tokens**.

---

## Como Rodar

### Opção 1 — dentro do Docker (recomendado durante o desenvolvimento integrado)

```bash
docker compose up -d postgres influxdb

docker exec -it backend-dev bash

# Dentro do container:
dotnet restore
dotnet run --urls "http://0.0.0.0:5000"
```

### Opção 2 — localmente (requer .NET 8 SDK instalado)

```bash
cd backend
dotnet restore
dotnet run
```

A API estará disponível em `http://localhost:5000`.

---

## Migrations (Entity Framework)

```bash
# Criar uma nova migration
dotnet ef migrations add <NomeDaMigration>

# Aplicar ao banco
dotnet ef database update
```

> Certifique-se de que o container do PostgreSQL está rodando antes de aplicar as migrations.

---

## Endpoints

Todos os endpoints autenticados exigem o header:

```
Authorization: Bearer <token>
```

### Autenticação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/api/auth/register` | Não | Cadastro de novo usuário |
| POST | `/api/auth/login` | Não | Login — retorna JWT |

**Body — register:**
```json
{
  "name": "João Silva",
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Body — login:**
```json
{
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Response — login:**
```json
{
  "token": "eyJhbGci...",
  "expiresAt": "2025-04-10T12:00:00Z"
}
```

---

### Cliente

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/client/me` | Sim | Retorna perfil do cliente autenticado |

---

### Pedidos

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/api/orders` | Sim | Cria novo pedido |
| GET | `/api/orders/{id}` | Sim | Busca pedido por ID |
| GET | `/api/orders/my` | Sim | Lista pedidos do cliente autenticado |

**Body — criar pedido:**
```json
{
  "vehicleId": "uuid-do-veiculo",
  "observations": "Cor azul metálico"
}
```

---

### Veículo

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/vehicles/{id}` | Sim | Retorna dados do veículo |

---

### Produção

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/production/{orderId}` | Sim | Retorna status atual e histórico de etapas |

**Response:**
```json
{
  "orderId": "uuid",
  "currentStage": "pintura",
  "status": "em_andamento",
  "timeline": [
    { "stage": "montagem", "enteredAt": "2025-04-09T08:00:00Z", "exitedAt": "2025-04-09T10:30:00Z" },
    { "stage": "pintura",  "enteredAt": "2025-04-09T11:00:00Z", "exitedAt": null }
  ]
}
```

---

### Recomendação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/recommendations/{clientId}` | Sim | Retorna sugestões personalizadas |

---

## Job de Sincronização (InfluxDB → PostgreSQL)

O arquivo `Jobs/InfluxSyncJob.cs` implementa um processo periódico (background service) que:

1. Consulta eventos novos no InfluxDB desde o último registro processado.
2. Consolida os pares `entrada / saída` por etapa.
3. Atualiza a tabela de produção no PostgreSQL.

Registre o job em `Program.cs`:

```csharp
builder.Services.AddHostedService<InfluxSyncJob>();
```

---

## Arquitetura em Camadas

```
HTTP Request
     │
     ▼
 Controller       ← valida input, chama Service, retorna DTO de resposta
     │
     ▼
  Service         ← orquestra regras de negócio, não conhece HTTP nem banco
     │
     ▼
Repository        ← acessa PostgreSQL (via EF Core) ou InfluxDB diretamente
     │
     ▼
  Database
```

Regras importantes:
- Controllers **não** acessam repositórios diretamente.
- Services **não** conhecem `HttpContext` nem retornam `IActionResult`.
- Repositórios **não** contêm regras de negócio.

---

## Padrões Adotados

- **DTOs** separados por operação (`CreateOrderDto`, `OrderResponseDto`) — nunca exponha a entidade diretamente.
- **Injeção de dependência** para todos os serviços e repositórios.
- **Async/await** em todas as operações de I/O.
- **Validação** via Data Annotations ou FluentValidation nos DTOs de entrada.

---

## Checklist de Implementação

- [ ] Configurar `AppDbContext` e connection string
- [ ] Criar entidades e primeira migration
- [ ] Implementar autenticação (register + login + JWT)
- [ ] Implementar CRUD de pedidos
- [ ] Implementar consulta de veículo
- [ ] Implementar `InfluxSyncJob`
- [ ] Implementar endpoint de produção (lê do PostgreSQL)
- [ ] Integrar com serviço de IA (HTTP client)
- [ ] Implementar endpoint de recomendação