# TP2B

Sistema de Vendas com RPC e Análise XML

Implementação completa de um sistema distribuído para análise de dados de vendas utilizando **Sockets**, **RPC** (gRPC e XML-RPC) e **Análise de XML** (XPath/XQuery).

## Índice
- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Uso](#uso)
- [Endpoints e APIs](#endpoints-e-apis)
- [Exemplos de Consultas](#exemplos-de-consultas)
- [Dashboard](#dashboard)
- [Docker](#docker)
- [Análise de Dados](#análise-de-dados)

---

## Visão Geral

Este projeto implementa um sistema completo para análise dos dados do arquivo **`retail_orders_full_dataset.csv`** contendo 9.994 registros de vendas.

### Fluxo de Dados
```
┌─────────────────────────┐
│ retail_orders_full_     │
│ dataset.csv (9.994)     │
└──────────┬──────────────┘
           │ Conversão + Validação
           ▼
┌─────────────────┐     ┌──────────────┐
│   output.xml    │────►│ schema.xsd   │
│ (validado)      │     │              │
└────────┬────────┘     └──────────────┘
         │
         ├─────────────┐
         │             │
         ▼             ▼
┌──────────────┐  ┌────────────────┐
│ gRPC Server  │  │ XML-RPC Server │
│  (port 50051)│  │   (port 8000)  │
└──────────────┘  └────────────────┘
         │             │
         └──────┬──────┘
                ▼
        ┌──────────────┐
        │  Dashboard   │
        │ (Streamlit)  │
        └──────────────┘
```

---

## Arquitetura

### Componentes Principais

#### 1. **Conversor CSV → XML** (`csv_to_xml_converter.py`)
```bash
python csv_to_xml_converter.py retail_orders_full_dataset.csv output.xml schema.xsd
```
- Converte 9.994 registros CSV para XML
- Valida estrutura com schema XSD
- Namespace: `http://sales.example.com`

#### 2. **Servidor gRPC** (`grpc_server.py`)
```bash
python grpc_server.py output.xml
```
- **Porta:** 50051
- **Protocol Buffers:** `sales.proto`
- **Arquivos gerados:** `sales_pb2.py`, `sales_pb2_grpc.py`

#### 3. **Servidor XML-RPC** (`xmlrpc_server.py`)
```bash
python xmlrpc_server.py output.xml
```
- **Porta:** 8000
- Endpoint: `http://localhost:8000/RPC2`

#### 4. **Dashboard** (`dashboard.py`)
```bash
streamlit run dashboard.py
```
- Visualização interativa em tempo real
- Métricas, gráficos e alertas

---

## Estrutura do Projeto

```
TP2B/
├── Dados/
│   ├── retail_orders_full_dataset.csv    # 9.994 registros originais
│   ├── output.xml                        # XML gerado
│   └── schema.xsd                        # Schema de validação
│
├── Servidores/
│   ├── csv_to_xml_converter.py           # Conversor CSV→XML
│   ├── grpc_server.py                    # Servidor gRPC
│   ├── xmlrpc_server.py                  # Servidor XML-RPC
│   ├── sales.proto                       # Definição gRPC
│   ├── sales_pb2.py                      # Código gerado gRPC
│   └── sales_pb2_grpc.py                 # Serviço gRPC
│
├── Testes/
│   └── test_clients.py                   # Teste dos serviços
│
├── Dashboard/
│   └── dashboard.py                      # Interface web
│
└── Docker/
    ├── docker-compose.yml
    ├── Dockerfile.grpc
    ├── Dockerfile.xmlrpc
    └── Dockerfile.converter
```

---

## Instalação

### 1. Pré-requisitos
```bash
# Verificar Python
python --version  # Python 3.11.9

# Instalar dependências
pip install grpcio==1.60.0 grpcio-tools==1.60.0 lxml==5.1.0 protobuf==4.25.1
pip install streamlit plotly pandas tabulate
```

### 2. Gerar Código gRPC
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sales.proto
```

### 3. Converter Dados
```bash
python csv_to_xml_converter.py retail_orders_full_dataset.csv output.xml schema.xsd
```

---

## Uso

### Opção 1: Execução Manual
```bash
# Terminal 1 - gRPC
python grpc_server.py output.xml

# Terminal 2 - XML-RPC  
python xmlrpc_server.py output.xml

# Terminal 3 - Dashboard
streamlit run dashboard.py

# Terminal 4 - Testes
python test_clients.py
```

### Opção 2: Docker
```bash
# Iniciar todos os serviços
docker compose up -d

# Verificar status
docker compose ps

# Testar
python test_clients.py

# Dashboard
streamlit run dashboard.py
```

---

## Endpoints e APIs

### gRPC (Porta 50051)
```python
import grpc
import sales_pb2
import sales_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = sales_pb2_grpc.SalesServiceStub(channel)

# Exemplo: Buscar registros do South
response = stub.GetRecordsByRegion(sales_pb2.RegionRequest(region='South'))
print(f"Registros: {response.total_count}")

# Exemplo: Estatísticas
stats = stub.GetSalesStats(sales_pb2.StatsRequest(field='region'))
```

### XML-RPC (Porta 8000)
```python
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy('http://localhost:8000/RPC2')

# Exemplo: Top produtos
products = proxy.get_top_products(10)
for prod in products:
    print(f"{prod['product']}: ${prod['total_sales']:,.2f}")

# Exemplo: Vendas por estado
states = proxy.get_sales_by_state()
```

---

## Exemplos de Consultas

### Via gRPC
```python
# Produtos com vendas > $1000
response = stub.ExecuteXPath(sales_pb2.XPathRequest(
    xpath_query="//ns:Record[ns:Sales > 1000]/ns:ProductName/text()"
))

# Total de vendas
response = stub.ExecuteXPath(sales_pb2.XPathRequest(
    xpath_query="sum(//ns:Record/ns:Sales)"
))
```

### Via XML-RPC
```python
# Consulta XPath personalizada
results = proxy.execute_xpath("//ns:Record[ns:Profit < 0]")

# Análise de clientes
results = proxy.execute_xpath("//ns:CustomerID/text()")
```

### Exemplos do Arquivo `xpath_xquery_examples.py`
```bash
python xpath_xquery_examples.py output.xml
```
- Seleção básica de Order IDs
- Filtro por vendas > $1000
- Agregação por região
- Análise de prejuízos
- Top produtos por quantidade

---

## Dashboard

### Execução
```bash
streamlit run dashboard.py
# Acesse: http://localhost:8501
```

### Funcionalidades
-  **Métricas em tempo real**
-  **Gráficos interativos** 
-  **Análise por região e estado**
-  **Identificação de prejuízos**
-  **Top produtos e categorias**

### Métricas Principais
- ** Total de Vendas:** $2.296.200,86
- ** Lucro Total:** $286.397,02
- ** Total de Pedidos:** 9.994
- ** Ticket Médio:** $229,76

---

## Docker

### Serviços Configurados
```yaml
services:
  grpc-server:      # Porta 50051
  xmlrpc-server:    # Porta 8000  
  converter:        # Processa CSV→XML
```

### Comandos Úteis
```bash
# Build e início
docker compose up -d

# Ver logs
docker compose logs -f grpc-server

# Health check
docker compose ps

# Parar serviços
docker compose down
```

---

## Análise de Dados

### Distribuição por Região
| Região | Vendas | Lucro | Pedidos |
|--------|---------|--------|----------|
| **West** | $725.457,82 | $108.418,45 | 3.203 |
| **East** | $678.781,24 | $91.522,78 | 2.848 |
| **Central** | $501.239,89 | $39.706,36 | 2.323 |
| **South** | $391.721,91 | $46.749,43 | 1.620 |

### Top 5 Produtos
1. **Canon imageCLASS 2200 Advanced Copier** - $61.599,82
2. **Fellowes PB500 Electric Punch** - $27.453,38
3. **Cisco TelePresence System EX90** - $22.638,48
4. **HON 5400 Series Task Chairs** - $21.870,58
5. **GBC DocuBind TL300** - $19.823,48

### Áreas de Atenção (Prejuízos)
- **Texas:** -$25.729,36 (985 pedidos)
- **Ohio:** -$16.971,38 (469 pedidos)
- **Pennsylvania:** -$15.559,96 (587 pedidos)
- **Illinois:** -$12.607,89 (492 pedidos)
- **Florida:** -$3.399,30 (383 pedidos)

---

## Testes

### Teste Completo dos Serviços
```bash
python test_clients.py
```
**Saída esperada:**
-  Testes gRPC: região, categoria, estatísticas, XPath
-  Testes XML-RPC: região, top produtos, vendas por estado
-  Métricas consistentes entre ambos os serviços

### Verificação de Saúde
```bash
# gRPC
python -c "import grpc; grpc.insecure_channel('localhost:50051')"

# XML-RPC  
python -c "import xmlrpc.client; xmlrpc.client.ServerProxy('http://localhost:8000/RPC2').system.listMethods()"
```

---

## Casos de Uso do Projeto

### Para Análise de Negócios
- Identificar produtos mais lucrativos
- Analisar performance por região/estado
- Detectar oportunidades e problemas

### Para Estudo de Tecnologias
- Arquitetura de microserviços
- Comunicação RPC (gRPC vs XML-RPC)
- Processamento de dados com XML/XPath
- Containerização com Docker

### Para Desenvolvimento
- Exemplo de sistema distribuído completo
- Integração entre tecnologias modernas e legadas
- Boas práticas de validação e documentação

---

## Características Técnicas

### Performance
- **gRPC:** ~10x mais rápido que XML-RPC
- **XML carregado em memória** para consultas rápidas
- **Health checks** automáticos nos containers

### Validação
- **Schema XSD** para estrutura de dados
- **Tipos específicos** (decimal, date, enum)
- **Validação em tempo** de conversão

### Escalabilidade
- **Arquitetura containerizada**
- **Serviços independentes**
- **APIs bem definidas**

---

## Desenvolvimento

### Adicionar Novos Endpoints
1. Atualizar `sales.proto`
2. Gerar código: `python -m grpc_tools.protoc ...`
3. Implementar no `grpc_server.py`
4. Adicionar correspondente no `xmlrpc_server.py`

### Extensões Possíveis
- Autenticação JWT
- Cache Redis para consultas
- Logs estruturados
- Métricas Prometheus
- API REST adicional

---

**Desenvolvido como trabalho académico - IPVC/IS 2025/2026 - Orientador: Professor Doutor Jorge Ribeiro** 
