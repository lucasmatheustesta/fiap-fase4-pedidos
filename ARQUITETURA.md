# Documentação de Arquitetura - Microsserviço de Pedidos

## Visão Geral da Arquitetura

O microsserviço de Pedidos foi projetado seguindo os princípios de arquitetura de microsserviços, com foco em responsabilidade única, autonomia e comunicação via APIs bem definidas.

## Padrões de Design Implementados

### 1. Repository Pattern
Embora não explicitamente implementado como classes separadas, o padrão está presente na separação entre modelos (acesso a dados) e rotas (lógica de apresentação).

### 2. Factory Pattern
Utilizado na configuração da aplicação Flask e na criação de objetos de teste através do Factory Boy.

### 3. MVC (Model-View-Controller)
- **Model**: Classes em `src/models/pedido.py`
- **View**: Respostas JSON das APIs
- **Controller**: Funções em `src/routes/pedidos.py`

### 4. Dependency Injection
Implementado através do sistema de fixtures do pytest para injeção de dependências nos testes.

## Estrutura de Camadas

```
┌─────────────────────────────────────┐
│           API Layer                 │
│        (Flask Routes)               │
├─────────────────────────────────────┤
│         Business Logic              │
│      (Route Functions)              │
├─────────────────────────────────────┤
│         Data Access                 │
│      (SQLAlchemy Models)            │
├─────────────────────────────────────┤
│         Database                    │
│         (SQLite)                    │
└─────────────────────────────────────┘
```

## Fluxo de Dados

### Criação de Pedido
1. Cliente envia POST para `/api/pedidos`
2. Validação dos dados de entrada
3. Criação do objeto Pedido
4. Criação dos objetos ItemPedido
5. Cálculo do total do pedido
6. Persistência no banco de dados
7. Retorno do pedido criado

### Atualização de Status
1. Sistema externo envia PUT para `/api/pedidos/{id}/status`
2. Validação do status
3. Busca do pedido no banco
4. Atualização do status e timestamp
5. Persistência da alteração
6. Retorno do pedido atualizado

## Comunicação entre Microsserviços

### Padrões de Comunicação

#### Síncrona (Implementada)
- **HTTP/REST**: Para consultas e operações imediatas
- **JSON**: Formato de troca de dados
- **CORS**: Habilitado para comunicação cross-origin

#### Assíncrona (Planejada)
- **Message Queue**: Para eventos de mudança de status
- **Event Sourcing**: Para auditoria de mudanças

### Endpoints de Integração

#### Recebimento de Dados
- `POST /api/produtos/sync`: Sincronização de produtos do serviço de produtos

#### Envio de Dados (Futuro)
- Eventos de criação de pedidos para o serviço de pagamento
- Eventos de mudança de status para o serviço de produção

## Estratégia de Persistência

### Banco de Dados
- **Desenvolvimento**: SQLite (simplicidade)
- **Produção**: PostgreSQL/MySQL (recomendado)

### Modelos de Dados

#### Relacionamentos
```
Pedido (1) ←→ (N) ItemPedido
Produto (1) ←→ (N) ItemPedido (referência)
```

#### Estratégias de Cache
- **Produtos**: Cache local sincronizado via API
- **Pedidos**: Sem cache (dados transacionais)

## Tratamento de Erros

### Códigos de Status HTTP
- `200`: Sucesso
- `201`: Criado com sucesso
- `400`: Erro de validação
- `404`: Recurso não encontrado
- `500`: Erro interno do servidor

### Estrutura de Resposta de Erro
```json
{
  "erro": "Descrição do erro"
}
```

## Segurança

### Implementado
- **CORS**: Configurado para permitir comunicação entre serviços
- **Validação de Entrada**: Validação de dados em todas as rotas

### Planejado
- **Autenticação**: JWT tokens
- **Autorização**: Role-based access control
- **Rate Limiting**: Proteção contra abuso
- **HTTPS**: Comunicação criptografada

## Monitoramento e Observabilidade

### Health Checks
- `GET /api/health`: Status do serviço
- `GET /api/info`: Informações do serviço

### Logging
- Logs de erro automáticos via Flask
- Estrutura preparada para logging estruturado

### Métricas (Planejado)
- Tempo de resposta das APIs
- Número de pedidos por status
- Taxa de erro por endpoint

## Escalabilidade

### Horizontal
- Stateless design permite múltiplas instâncias
- Banco de dados compartilhado entre instâncias

### Vertical
- Otimizações de query no SQLAlchemy
- Índices de banco de dados apropriados

### Cache
- Cache de produtos em memória
- Possibilidade de Redis para cache distribuído

## Resiliência

### Implementado
- Tratamento de exceções em todas as rotas
- Rollback automático de transações em caso de erro

### Planejado
- **Circuit Breaker**: Para chamadas a serviços externos
- **Retry Logic**: Para operações que podem falhar temporariamente
- **Timeout**: Para evitar bloqueios indefinidos

## Testes

### Estratégia de Testes
- **Unitários**: 70% da cobertura
- **BDD**: 10% da cobertura
- **Integração**: 4% da cobertura

### Pirâmide de Testes
```
    /\
   /  \    E2E (BDD)
  /____\
 /      \   Integration
/________\
Unit Tests
```

### Cobertura por Módulo
- `src/models/pedido.py`: 94%
- `src/routes/pedidos.py`: 83%
- `src/main.py`: 70%
- **Total**: 84%

## Performance

### Otimizações Implementadas
- Lazy loading de relacionamentos
- Queries otimizadas com SQLAlchemy
- Serialização eficiente com `to_dict()`

### Benchmarks (Estimados)
- Criação de pedido: ~50ms
- Listagem de pedidos: ~30ms
- Atualização de status: ~40ms

## Deployment

### Containerização (Preparado)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 5000
CMD ["python", "src/main.py"]
```

### Configuração de Ambiente
- Variáveis de ambiente para configuração
- Separação entre desenvolvimento e produção
- Health checks para orquestração

## Evolução da Arquitetura

### Próximas Iterações

#### Fase 1: Eventos Assíncronos
- Implementação de message queue (RabbitMQ/Apache Kafka)
- Eventos de domínio para mudanças de estado

#### Fase 2: Observabilidade Avançada
- Distributed tracing (Jaeger/Zipkin)
- Métricas customizadas (Prometheus)
- Dashboards (Grafana)

#### Fase 3: Segurança Avançada
- Autenticação e autorização
- Audit logs
- Criptografia de dados sensíveis

#### Fase 4: Performance
- Cache distribuído (Redis)
- Read replicas
- Otimizações de query

## Considerações de Design

### Trade-offs Realizados

#### Simplicidade vs. Flexibilidade
- **Escolha**: Simplicidade
- **Razão**: Facilita manutenção e entendimento
- **Impacto**: Menos configurabilidade

#### Consistência vs. Disponibilidade
- **Escolha**: Consistência
- **Razão**: Dados transacionais críticos
- **Impacto**: Possível indisponibilidade em falhas

#### Performance vs. Legibilidade
- **Escolha**: Legibilidade
- **Razão**: Código educacional
- **Impacto**: Possíveis otimizações futuras necessárias

### Lições Aprendidas

1. **Separação de Responsabilidades**: Clara divisão entre camadas facilita testes
2. **Validação de Entrada**: Essencial para robustez da API
3. **Testes BDD**: Valiosos para validar regras de negócio
4. **Documentação**: Fundamental para manutenibilidade

---

Esta documentação serve como guia para entendimento, manutenção e evolução do microsserviço de Pedidos.

