# Microsserviço de Pedidos - FIAP SOAT Tech Challenge Fase 4

## Visão Geral

Este é o microsserviço de Pedidos desenvolvido como parte do Tech Challenge da FASE 4 do curso de Arquitetura de Software da FIAP. O microsserviço é responsável por gerenciar todo o ciclo de vida dos pedidos em um sistema de autoatendimento para lanchonetes.

## Arquitetura

### Responsabilidades do Microsserviço

- **Criação de Pedidos**: Registrar novos pedidos no sistema
- **Gerenciamento de Status**: Controlar o fluxo de status dos pedidos (Recebido → Em preparação → Pronto → Finalizado)
- **Consulta de Pedidos**: Listar pedidos por cliente, status ou fila de produção
- **Cache de Produtos**: Manter cache local de produtos para montagem de pedidos
- **Integração**: Comunicar-se com outros microsserviços via API REST

### Tecnologias Utilizadas

- **Python 3.11**: Linguagem de programação
- **Flask**: Framework web minimalista
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados (desenvolvimento)
- **Pytest**: Framework de testes
- **Pytest-BDD**: Testes comportamentais
- **Factory Boy**: Geração de dados para testes
- **Flask-CORS**: Suporte a CORS para comunicação entre microsserviços

## Estrutura do Projeto

```
pedidos-service/
├── src/
│   ├── models/
│   │   └── pedido.py          # Modelos de dados (Pedido, ItemPedido, Produto)
│   ├── routes/
│   │   └── pedidos.py         # Rotas da API REST
│   ├── static/                # Arquivos estáticos
│   └── main.py               # Ponto de entrada da aplicação
├── tests/
│   ├── unit/                 # Testes unitários
│   │   ├── test_models.py
│   │   └── test_routes.py
│   ├── bdd/                  # Testes BDD
│   │   ├── pedidos.feature
│   │   └── test_pedidos_steps.py
│   ├── fixtures/             # Factories para testes
│   │   └── factories.py
│   └── conftest.py          # Configuração dos testes
├── venv/                    # Ambiente virtual Python
├── requirements.txt         # Dependências do projeto
├── pytest.ini             # Configuração do pytest
└── README.md              # Este arquivo
```

## Modelo de Dados

### Entidades Principais

#### Pedido

- `id`: Identificador único
- `cliente_id`: CPF do cliente (opcional para pedidos anônimos)
- `status`: Status atual (Recebido, Em preparação, Pronto, Finalizado)
- `total`: Valor total do pedido
- `data_criacao`: Timestamp de criação
- `data_atualizacao`: Timestamp da última atualização

#### ItemPedido

- `id`: Identificador único
- `pedido_id`: Referência ao pedido
- `produto_id`: ID do produto (referência externa)
- `nome_produto`: Nome do produto (cache)
- `categoria`: Categoria do produto
- `quantidade`: Quantidade solicitada
- `preco_unitario`: Preço unitário no momento do pedido
- `observacoes`: Observações especiais

#### Produto (Cache Local)

- `id`: Identificador único
- `nome`: Nome do produto
- `categoria`: Categoria (Lanche, Acompanhamento, Bebida, Sobremesa)
- `preco`: Preço atual
- `descricao`: Descrição do produto
- `disponivel`: Disponibilidade do produto

## API Endpoints

### Informações do Serviço

- `GET /api/info` - Informações sobre o microsserviço
- `GET /api/health` - Health check do serviço

### Gestão de Pedidos

- `POST /api/pedidos` - Criar novo pedido
- `GET /api/pedidos` - Listar pedidos (com filtros opcionais)
- `GET /api/pedidos/{id}` - Obter pedido específico
- `PUT /api/pedidos/{id}/status` - Atualizar status do pedido
- `GET /api/pedidos/cliente/{cliente_id}` - Pedidos de um cliente
- `GET /api/pedidos/fila` - Fila de pedidos para produção

### Produtos

- `GET /api/produtos` - Listar produtos disponíveis
- `GET /api/produtos/categorias` - Listar categorias de produtos
- `POST /api/produtos/sync` - Sincronizar produtos (usado por outros serviços)

## Instalação e Execução

### Pré-requisitos

- Python 3.11+
- pip (gerenciador de pacotes Python)

### Configuração do Ambiente

1. **Clone o repositório** (ou extraia os arquivos)
2. **Navegue até o diretório do projeto**:

   ```bash
   cd pedidos-service
   ```

3. **Ative o ambiente virtual**:

   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências** (se necessário):
   ```bash
   pip install -r requirements.txt
   ```

### Executando o Serviço

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar o servidor de desenvolvimento
python src/main.py
```

O serviço estará disponível em `http://localhost:5000`

### Executando os Testes

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar todos os testes
pytest

# Executar apenas testes unitários
pytest tests/unit/

# Executar apenas testes BDD
pytest tests/bdd/

# Executar testes com relatório de cobertura
pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Exemplos de Uso da API

### Criar um Pedido

```bash
curl -X POST http://localhost:5000/api/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "12345678901",
    "itens": [
      {
        "produto_id": 1,
        "nome_produto": "Hambúrguer Clássico",
        "categoria": "Lanche",
        "quantidade": 2,
        "preco_unitario": 15.50,
        "observacoes": "Sem cebola"
      },
      {
        "produto_id": 2,
        "nome_produto": "Batata Frita",
        "categoria": "Acompanhamento",
        "quantidade": 1,
        "preco_unitario": 8.00
      }
    ]
  }'
```

### Listar Pedidos

```bash
# Todos os pedidos
curl http://localhost:5000/api/pedidos

# Filtrar por status
curl http://localhost:5000/api/pedidos?status=Recebido

# Filtrar por cliente
curl http://localhost:5000/api/pedidos?cliente_id=12345678901
```

### Atualizar Status do Pedido

```bash
curl -X PUT http://localhost:5000/api/pedidos/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Em preparação"}'
```

### Verificar Fila de Produção

```bash
curl http://localhost:5000/api/pedidos/fila
```

## Testes

### Cobertura de Testes

O projeto possui **84% de cobertura de testes**, superando o requisito mínimo de 80%.

### Tipos de Testes

#### Testes Unitários

- **Modelos**: Validação de criação, serialização e métodos dos modelos
- **Rotas**: Testes de todos os endpoints da API
- **Validações**: Testes de validação de entrada e tratamento de erros

#### Testes BDD (Behavior-Driven Development)

- **Cenários de Negócio**: Criação de pedidos, acompanhamento de status
- **Fluxos Completos**: Testes end-to-end dos principais casos de uso
- **Validações de Regras**: Verificação das regras de negócio

### Executando Testes Específicos

```bash
# Testes de modelos
pytest tests/unit/test_models.py -v

# Testes de rotas
pytest tests/unit/test_routes.py -v

# Cenários BDD específicos
pytest tests/bdd/test_pedidos_steps.py::test_criar_um_pedido_com_sucesso -v
```

## Comunicação entre Microsserviços

### Padrões Implementados

1. **API REST**: Comunicação síncrona via HTTP
2. **CORS Habilitado**: Permite requisições de qualquer origem
3. **Cache Local**: Produtos são sincronizados via endpoint `/api/produtos/sync`
4. **Tratamento de Erros**: Respostas padronizadas com códigos HTTP apropriados

### Integração com Outros Serviços

- **Serviço de Produtos**: Sincronização de catálogo via `/api/produtos/sync`
- **Serviço de Pagamento**: Recebe confirmações de pagamento (futuro)
- **Serviço de Produção**: Envia pedidos para fila de produção (futuro)

## Configuração para Produção

### Variáveis de Ambiente Recomendadas

```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:port/dbname
export SECRET_KEY=your-secret-key-here
```

### Banco de Dados

Para produção, recomenda-se substituir SQLite por PostgreSQL ou MySQL:

```python
# Em src/main.py
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pedidos.db')
```

### Deploy

O microsserviço está preparado para deploy em containers Docker ou plataformas como Heroku, AWS, etc.

## Arquitetura de Microsserviços

### Princípios Seguidos

1. **Responsabilidade Única**: Cada serviço tem uma responsabilidade bem definida
2. **Autonomia**: Banco de dados próprio, sem acesso direto a outros BDs
3. **Comunicação via API**: Interfaces bem definidas entre serviços
4. **Tolerância a Falhas**: Tratamento adequado de erros e timeouts
5. **Observabilidade**: Logs e health checks implementados

### Próximos Passos

- Implementação de eventos assíncronos (Message Queue)
- Monitoramento e métricas (Prometheus/Grafana)
- Circuit Breaker para resiliência
- Autenticação e autorização (JWT)
- Versionamento da API

## Contribuição

Este projeto foi desenvolvido como parte do Tech Challenge da FIAP. Para contribuições:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Developer │ │ GitHub Actions │ │ AWS App │
│ │ │ │ │ Runner │
│ 1. Code │───▶│ 2. Quality │───▶│ 3. Deploy │
│ 2. PR │ │ Gate │ │ 4. Serve │
│ 3. Merge │ │ 3. Auto Deploy │ │ 5. Monitor │
└─────────────────┘ └──────────────────┘ └─────────────────┘
▲ │
│ ▼
┌──────────────────┐ ┌─────────────────┐
│ GitHub Secrets │ │ Public HTTPS │
│ │ │ URL │
│ • AWS*ACCESS*_ │ │ │
│ • AWS*ACCOUNT*_ │ │ 🌐 Live API │
└──────────────────┘ └─────────────────┘
