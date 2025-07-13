from flask import Blueprint, jsonify, request
from src.models.pedido import Pedido, ItemPedido, Produto, StatusPedido, db
from datetime import datetime
from decimal import Decimal

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do microsserviço"""
    return jsonify({
        'status': 'healthy',
        'service': 'pedidos-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@pedidos_bp.route('/pedidos', methods=['GET'])
def listar_pedidos():
    """Lista todos os pedidos"""
    try:
        # Parâmetros de filtro opcionais
        status = request.args.get('status')
        cliente_id = request.args.get('cliente_id')
        
        query = Pedido.query
        
        if status:
            try:
                status_enum = StatusPedido(status)
                query = query.filter(Pedido.status == status_enum)
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400
        
        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)
        
        # Ordenar por data de criação (mais recentes primeiro)
        pedidos = query.order_by(Pedido.data_criacao.desc()).all()
        
        return jsonify({
            'pedidos': [pedido.to_dict() for pedido in pedidos],
            'total': len(pedidos)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@pedidos_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    """Cria um novo pedido"""
    try:
        data = request.json
        
        # Validação básica
        if not data or 'itens' not in data or not data['itens']:
            return jsonify({'erro': 'Itens do pedido são obrigatórios'}), 400
        
        # Criar o pedido
        pedido = Pedido(
            cliente_id=data.get('cliente_id')
        )
        
        db.session.add(pedido)
        db.session.flush()  # Para obter o ID do pedido
        
        # Adicionar itens ao pedido
        total = Decimal('0.00')
        for item_data in data['itens']:
            # Validar item
            if not all(k in item_data for k in ['produto_id', 'nome_produto', 'categoria', 'quantidade', 'preco_unitario']):
                return jsonify({'erro': 'Dados incompletos do item'}), 400
            
            item = ItemPedido(
                pedido_id=pedido.id,
                produto_id=item_data['produto_id'],
                nome_produto=item_data['nome_produto'],
                categoria=item_data['categoria'],
                quantidade=item_data['quantidade'],
                preco_unitario=Decimal(str(item_data['preco_unitario'])),
                observacoes=item_data.get('observacoes')
            )
            
            db.session.add(item)
            total += item.preco_unitario * item.quantidade
        
        # Atualizar total do pedido
        pedido.total = total
        
        db.session.commit()
        
        return jsonify(pedido.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@pedidos_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    """Obtém um pedido específico"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'erro': 'Pedido não encontrado'}), 404
        return jsonify(pedido.to_dict())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@pedidos_bp.route('/pedidos/<int:pedido_id>/status', methods=['PUT'])
def atualizar_status_pedido(pedido_id):
    """Atualiza o status de um pedido"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'erro': 'Pedido não encontrado'}), 404
            
        data = request.json
        
        if not data or 'status' not in data:
            return jsonify({'erro': 'Status é obrigatório'}), 400
        
        try:
            novo_status = StatusPedido(data['status'])
        except ValueError:
            return jsonify({'erro': 'Status inválido'}), 400
        
        pedido.status = novo_status
        pedido.data_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(pedido.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@pedidos_bp.route('/pedidos/cliente/<string:cliente_id>', methods=['GET'])
def listar_pedidos_cliente(cliente_id):
    """Lista pedidos de um cliente específico"""
    try:
        pedidos = Pedido.query.filter(Pedido.cliente_id == cliente_id).order_by(Pedido.data_criacao.desc()).all()
        
        return jsonify({
            'pedidos': [pedido.to_dict() for pedido in pedidos],
            'cliente_id': cliente_id,
            'total': len(pedidos)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@pedidos_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    """Lista produtos disponíveis para montagem do pedido"""
    try:
        categoria = request.args.get('categoria')
        
        query = Produto.query.filter(Produto.disponivel == True)
        
        if categoria:
            query = query.filter(Produto.categoria == categoria)
        
        produtos = query.order_by(Produto.categoria, Produto.nome).all()
        
        return jsonify({
            'produtos': [produto.to_dict() for produto in produtos],
            'total': len(produtos)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@pedidos_bp.route('/produtos/categorias', methods=['GET'])
def listar_categorias():
    """Lista as categorias de produtos disponíveis"""
    categorias = ['Lanche', 'Acompanhamento', 'Bebida', 'Sobremesa']
    return jsonify({'categorias': categorias})

@pedidos_bp.route('/pedidos/fila', methods=['GET'])
def fila_pedidos():
    """Lista pedidos na fila de produção (visão da cozinha)"""
    try:
        # Pedidos que não estão finalizados, ordenados por data de criação
        pedidos = Pedido.query.filter(
            Pedido.status.in_([StatusPedido.RECEBIDO, StatusPedido.EM_PREPARACAO, StatusPedido.PRONTO])
        ).order_by(Pedido.data_criacao.asc()).all()
        
        return jsonify({
            'fila': [pedido.to_dict() for pedido in pedidos],
            'total': len(pedidos)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Endpoints para sincronização de produtos (usado pelo serviço de produtos)
@pedidos_bp.route('/produtos/sync', methods=['POST'])
def sincronizar_produtos():
    """Sincroniza produtos com o serviço de produtos"""
    try:
        data = request.json
        
        if not data or 'produtos' not in data:
            return jsonify({'erro': 'Lista de produtos é obrigatória'}), 400
        
        # Limpar produtos existentes
        Produto.query.delete()
        
        # Adicionar novos produtos
        for produto_data in data['produtos']:
            produto = Produto(
                id=produto_data['id'],
                nome=produto_data['nome'],
                categoria=produto_data['categoria'],
                preco=Decimal(str(produto_data['preco'])),
                descricao=produto_data.get('descricao'),
                disponivel=produto_data.get('disponivel', True)
            )
            db.session.add(produto)
        
        db.session.commit()
        
        return jsonify({'mensagem': 'Produtos sincronizados com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

