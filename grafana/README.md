# SENAI ACE — Grafana (Dashboards de Produção e Logística)

## Sobre o Projeto

Este módulo representa a camada de **visualização e análise de dados** do sistema SENAI ACE.

O Grafana é responsável por:

- Exibir métricas em tempo real
- Monitorar produção industrial simulada
- Acompanhar eventos logísticos
- Criar indicadores de desempenho (KPIs)
- Visualizar dados provenientes do InfluxDB

---

## Objetivo

O Grafana neste projeto tem como finalidade:

- Transformar dados IoT em painéis visuais
- Permitir análise operacional em tempo real
- Apoiar decisões baseadas em indicadores
- Demonstrar conceitos de BI aplicado a IIoT
- Visualizar dados gerados por MQTT → Node-RED → InfluxDB

---

## Arquitetura de Visualização


```mermaid
flowchart LR

    A[Simulador]

    subgraph Stack MING
      B[MQTT]
      C[Node-RED]
      D[InfluxDB]
      E[Grafana]
    end
    
    A --> B
    B --> C 
    C --> D
    D --> E

````

O Grafana atua como **camada final de observação do sistema**.

---

## Fonte de Dados

* Banco: InfluxDB 2.x
* Bucket: `ace`
* Organização: `senai`
* Tipo: Time Series Database

---

# Dashboard — Produção

## Visão Geral

O dashboard de produção monitora a linha de montagem industrial.

### Indicadores (KPIs)

#### Veículos Produzidos

* Baseado em chassi único
* Conta veículos distintos processados

#### Mensagens Processadas

* Soma total de eventos recebidos

---

## Inconsistências e Qualidade

### Eventos por Etapa

* Agrupa produção por fase do processo:

  * montagem
  * pintura
  * finalização
* Permite identificar gargalos na linha

### Status por Etapa

* Matriz de status operacional:

  * OK
  * erro
  * pendente
* Cruzamento entre etapa e estado do processo

---

## Uso do Dashboard Produção

Este painel é utilizado para:

* Monitoramento de linha de produção simulada
* Análise de fluxo produtivo
* Identificação de gargalos operacionais
* Visualização de KPIs industriais

---

# Dashboard — Logística

## Visão Geral

O dashboard de logística acompanha o fluxo de entrega de itens produzidos.

---

## Indicadores

### Total Despachado

* Soma total de eventos logísticos processados

### Por Tipo de Carga

* Classificação:

  * veículos
  * peças
* Permite análise de distribuição logística

### Destino

* Agrupamento por cidades/regiões
* Demonstra fluxo de distribuição

---

## Análise Temporal

### Envios por Minuto

* Gráfico temporal de eventos
* Permite identificar:

  * picos de envio
  * estabilidade do sistema
  * carga operacional

---

## Uso do Dashboard Logística

Este painel é utilizado para:

* Monitoramento de cadeia de suprimentos simulada
* Análise de fluxo de entrega
* Controle de distribuição de cargas
* Avaliação de performance logística

---

## Estrutura dos Dashboards

```mermaid
flowchart TB

A[InfluxDB] --> B[Grafana]

B --> C[Dashboard Produção]
B --> D[Dashboard Logística]

C --> C1[KPIs]
C --> C2[Etapas]

D --> D1[Fluxo]
D --> D2[Destinos]
```

---

## Tecnologias Utilizadas

* Grafana
* InfluxDB 2.x
* Flux Query Language
* Node-RED (origem dos dados)
* MQTT (entrada de eventos)

---

## Requisitos

* Grafana 9+
* InfluxDB configurado e conectado
* Datasource InfluxDB ativo no Grafana
* Bucket `ace` disponível

---

## Importação dos Dashboards

Os dashboards podem ser importados diretamente via JSON:

* Dashboard Produção
* Dashboard Logística

Basta utilizar:

```
Grafana → Import → Upload JSON
```

---

## Uso Educacional

Este módulo é utilizado para ensino de:

* Visualização de dados industriais (IIoT)
* Construção de KPIs em tempo real
* Integração Grafana + InfluxDB
* Análise de eventos MQTT em dashboards
* Business Intelligence aplicado a sistemas industriais

---

## Observações

* O Grafana não gera dados, apenas consome do InfluxDB
* Depende do pipeline ativo (Simulador + Node-RED)
* Pode ser expandido com alertas (Alerting)
* Pode integrar com dashboards executivos e OEE

