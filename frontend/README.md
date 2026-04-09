# Frontend — Aplicação Web

Interface web do sistema de acompanhamento de produção, desenvolvida em **React**.

Consome exclusivamente a API REST do backend — sem acesso direto a banco de dados.

---

## Tecnologias

- [React 18](https://react.dev/) — biblioteca de UI
- [React Router v6](https://reactrouter.com/) — roteamento
- [Axios](https://axios-http.com/) — cliente HTTP
- [Context API](https://react.dev/reference/react/createContext) — estado global (autenticação)

---

## Estrutura de Pastas

```
frontend/
├── public/
│   └── index.html
│
├── src/
│   ├── api/                    # Configuração do Axios e chamadas à API
│   │   ├── axios.js            # Instância base com interceptors de token
│   │   ├── authApi.js
│   │   ├── orderApi.js
│   │   ├── productionApi.js
│   │   └── recommendationApi.js
│   │
│   ├── components/             # Componentes reutilizáveis
│   │   ├── Header.jsx
│   │   ├── PrivateRoute.jsx    # Redireciona para login se não autenticado
│   │   ├── ProductionTimeline.jsx
│   │   └── RecommendationCard.jsx
│   │
│   ├── contexts/
│   │   └── AuthContext.jsx     # Token JWT, usuário logado, login/logout
│   │
│   ├── pages/                  # Uma pasta por tela
│   │   ├── Login/
│   │   │   ├── index.jsx
│   │   │   └── Login.module.css
│   │   ├── Register/
│   │   ├── Home/
│   │   ├── Profile/
│   │   ├── Orders/
│   │   │   ├── OrderList.jsx
│   │   │   └── OrderDetail.jsx
│   │   ├── Production/
│   │   │   └── ProductionDetail.jsx
│   │   └── Vehicle/
│   │       └── VehicleDetail.jsx
│   │
│   ├── routes/
│   │   └── AppRoutes.jsx       # Definição central de todas as rotas
│   │
│   ├── App.jsx
│   └── main.jsx
│
├── .env.example
├── .env                        # NÃO subir no repositório
├── package.json
└── vite.config.js
```

---

## Configuração

Copie o arquivo de exemplo e preencha a URL da API:

```bash
cp .env.example .env
```

Conteúdo do `.env`:

```env
VITE_API_URL=http://localhost:5000
```

> Em produção, substitua pelo endereço real do backend.

---

## Como Rodar

### Opção 1 — dentro do Docker

```bash
docker exec -it frontend-dev bash

# Dentro do container:
npm install
npm run dev -- --host 0.0.0.0 --port 19006
```

Acesse em `http://localhost:19006`.

### Opção 2 — localmente (requer Node 20+)

```bash
cd frontend
npm install
npm run dev
```

---

## Telas

| Rota | Componente | Auth | Descrição |
|------|-----------|------|-----------|
| `/login` | `Login` | Não | Formulário de login |
| `/register` | `Register` | Não | Cadastro de novo usuário |
| `/` | `Home` | Sim | Resumo dos pedidos ativos |
| `/profile` | `Profile` | Sim | Perfil do cliente |
| `/orders` | `OrderList` | Sim | Lista de pedidos |
| `/orders/:id` | `OrderDetail` | Sim | Detalhe do pedido + link para produção |
| `/production/:orderId` | `ProductionDetail` | Sim | Timeline de etapas de produção |
| `/vehicles/:id` | `VehicleDetail` | Sim | Dados do veículo |

---

## Autenticação

O token JWT retornado pelo backend é armazenado no `localStorage` e injetado automaticamente em todas as requisições via interceptor do Axios.

### `src/api/axios.js`

```js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

### `src/contexts/AuthContext.jsx`

Expõe:

- `user` — dados do usuário autenticado
- `login(email, password)` — chama a API, salva o token e redireciona
- `logout()` — limpa o token e redireciona para `/login`
- `isAuthenticated` — booleano para uso nas rotas protegidas

---

## Rotas Protegidas

Rotas que exigem autenticação usam o componente `PrivateRoute`:

```jsx
// src/routes/AppRoutes.jsx
<Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
```

```jsx
// src/components/PrivateRoute.jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}
```

---

## Chamadas à API

Centralize todas as chamadas em `/src/api/`. Nunca use `fetch` ou `axios` diretamente dentro de componentes ou páginas.

**Exemplo — `src/api/productionApi.js`:**

```js
import api from './axios';

export const getProduction = (orderId) =>
  api.get(`/api/production/${orderId}`).then((res) => res.data);
```

**Uso na página:**

```jsx
import { useEffect, useState } from 'react';
import { getProduction } from '../../api/productionApi';

export default function ProductionDetail({ orderId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    getProduction(orderId).then(setData);
  }, [orderId]);

  if (!data) return <p>Carregando...</p>;

  return <ProductionTimeline timeline={data.timeline} />;
}
```

---

## Componente de Timeline

O componente `ProductionTimeline` recebe o array de etapas e renderiza o progresso da produção:

```jsx
// src/components/ProductionTimeline.jsx
export default function ProductionTimeline({ timeline }) {
  return (
    <ul>
      {timeline.map((item) => (
        <li key={item.stage}>
          <strong>{item.stage}</strong>
          <span> — entrada: {new Date(item.enteredAt).toLocaleString('pt-BR')}</span>
          {item.exitedAt && (
            <span> — saída: {new Date(item.exitedAt).toLocaleString('pt-BR')}</span>
          )}
          {!item.exitedAt && <span> ← em andamento</span>}
        </li>
      ))}
    </ul>
  );
}
```

---

## Padrões Adotados

- **Páginas** contêm lógica de estado e chamadas à API; **componentes** são apresentacionais.
- **Todas as chamadas HTTP** passam pelos módulos em `/api/` — nunca diretamente nos componentes.
- **Variáveis de ambiente** sempre prefixadas com `VITE_` para serem expostas pelo Vite.
- **CSS Modules** para escopo local de estilos (`.module.css`).
- **Sem estado global além de autenticação** — use estado local com `useState`/`useReducer` nas páginas.

---

## Checklist de Implementação

- [ ] Configurar Vite + React
- [ ] Instalar dependências (`react-router-dom`, `axios`)
- [ ] Criar instância do Axios com interceptor de token
- [ ] Implementar `AuthContext` (login, logout, token)
- [ ] Implementar `PrivateRoute`
- [ ] Definir rotas em `AppRoutes.jsx`
- [ ] Tela de Login
- [ ] Tela de Cadastro
- [ ] Tela Home (lista de pedidos ativos)
- [ ] Tela de Perfil
- [ ] Tela de Detalhe do Pedido
- [ ] Tela de Acompanhamento de Produção (timeline)
- [ ] Tela de Detalhe do Veículo
- [ ] Componente de Recomendações