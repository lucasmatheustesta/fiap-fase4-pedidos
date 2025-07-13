Feature: Gerenciamento de Pedidos
  Como um cliente da lanchonete
  Eu quero poder fazer pedidos
  Para que eu possa comprar produtos

  Background:
    Given que o sistema está funcionando
    And existem produtos disponíveis

  Scenario: Criar um pedido com sucesso
    Given que sou um cliente identificado com CPF "12345678901"
    When eu faço um pedido com os seguintes itens:
      | produto_id | nome_produto | categoria | quantidade | preco_unitario |
      | 1          | Hambúrguer   | Lanche    | 2          | 15.50          |
      | 2          | Batata Frita | Acompanhamento | 1     | 8.00           |
    Then o pedido deve ser criado com sucesso
    And o status do pedido deve ser "Recebido"
    And o total do pedido deve ser 39.00

  Scenario: Criar um pedido anônimo
    Given que sou um cliente anônimo
    When eu faço um pedido com os seguintes itens:
      | produto_id | nome_produto | categoria | quantidade | preco_unitario |
      | 1          | Hambúrguer   | Lanche    | 1          | 15.50          |
    Then o pedido deve ser criado com sucesso
    And o cliente_id deve ser nulo
    And o total do pedido deve ser 15.50

  Scenario: Acompanhar status do pedido
    Given que existe um pedido com status "Recebido"
    When o status do pedido é atualizado para "Em preparação"
    Then o status do pedido deve ser "Em preparação"
    And a data de atualização deve ser modificada

  Scenario: Falha ao criar pedido sem itens
    Given que sou um cliente identificado com CPF "12345678901"
    When eu tento fazer um pedido sem itens
    Then o pedido não deve ser criado
    And deve retornar erro "Itens do pedido são obrigatórios"

