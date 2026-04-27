# SENAI ACE — Node-RED (Pipeline MQTT + InfluxDB)

## Sobre o Projeto

Este módulo representa o **pipeline de processamento de dados em tempo real** utilizando **Node-RED**.

Ele atua como um **consumidor de eventos MQTT**, responsável por:

- Receber dados do simulador industrial
- Processar e normalizar os eventos
- Estruturar dados para armazenamento
- Persistir informações no InfluxDB

Este componente faz parte de uma arquitetura orientada a eventos para simulação de ambiente industrial (IIoT).

---

## Objetivo

O Node-RED tem como função:

- Consumir eventos via MQTT
- Transformar dados de produção e logística
- Padronizar timestamps e payloads
- Inserir dados em banco de séries temporais (InfluxDB)
- Permitir integração com dashboards (Grafana ou similares)

---

## Arquitetura do Fluxo

```mermaid
flowchart LR

    A[MQTT Broker]

    subgraph Node-RED Pipeline
        B1[MQTT In - Produção]
        B2[MQTT In - Logística]
        C1[Function: Produção]
        C2[Function: Logística]
        D[InfluxDB Out]
        DB[(InfluxDB)]
    end

    A --> B1
    A --> B2

    B1 --> C1
    B2 --> C2

    C1 --> D
    C2 --> D

    D --> DB
````

---

## Tópicos MQTT Consumidos

### Produção

```
senai/producao/linha
```

### Logística

```
senai/logistica/entrega
```

---

## Processamento de Dados

### 🔧 Fluxo de Produção

Node responsável: `producao`

**Funções:**

* Define measurement: `producao`
* Extrai dados do payload:

  * chassi
  * etapa
  * status
* Normaliza timestamp para formato ISO
* Adiciona campo fixo:

  * `quantidade = 1`

**Estrutura final:**

```json
{
  "measurement": "producao",
  "payload": {
    "quantidade": 1,
    "chassi": "ABC123",
    "etapa": "montagem",
    "status": "ok"
  }
}
```

---

### Fluxo de Logística

Node responsável: `logistica`

**Funções:**

* Define measurement: `logistica`
* Extrai dados do payload:

  * id
  * tipo
  * destino
  * status
* Normaliza timestamp para ISO
* Adiciona campo fixo:

  * `quantidade = 1`

**Estrutura final:**

```json
{
  "measurement": "logistica",
  "payload": {
    "quantidade": 1,
    "id": "987",
    "tipo": "entrega",
    "destino": "Sorocaba",
    "status": "em_transito"
  }
}
```

---

## Banco de Dados (InfluxDB)

### Configuração

* URL: `http://influxdb:8086`
* Bucket: `ace`
* Organização: `senai`
* Protocolo: InfluxDB 2.x

---

### Measurements Geradas

* `producao`
* `logistica`

---

## Debug e Monitoramento

O fluxo inclui nós de debug para:

* Visualização de payloads em tempo real
* Verificação de transformação dos dados
* Auditoria de mensagens MQTT
* Validação de envio para InfluxDB

---

## Fluxo de Dados

```text
MQTT → Node-RED → Function (Transformação) → InfluxDB
```

---

## Requisitos

* Node-RED
* node-red-contrib-influxdb
* Broker MQTT (ex: Mosquitto)
* InfluxDB 2.x

---

## Execução

### Iniciar Node-RED

```bash
node-red
```

Acesso padrão:

```
http://localhost:1880
```

---

## Uso Educacional

Este projeto é utilizado para ensino de:

* Arquitetura orientada a eventos (Event-Driven Architecture)
* Integração MQTT em sistemas IoT
* Processamento de dados com Node-RED
* Armazenamento em banco de séries temporais (InfluxDB)
* Simulação de ambiente industrial digital (IIoT)

---

## Observações

* Este módulo depende do simulador para geração de eventos
* O broker MQTT deve estar ativo antes da execução
* O InfluxDB deve estar configurado corretamente para persistência
* Pode ser integrado com Grafana para dashboards analíticos

