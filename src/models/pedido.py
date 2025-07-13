from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class StatusPedido(Enum):
    RECEBIDO = "Recebido"
    EM_PREPARACAO = "Em preparação"
    PRONTO = "Pronto"
    FINALIZADO = "Finalizado"

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.String(11), nullable=True)  # CPF do cliente (opcional)
    status = db.Column(db.Enum(StatusPedido), nullable=False, default=StatusPedido.RECEBIDO)
    total = db.Column(Numeric(10, 2), nullable=False, default=0.00)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com itens do pedido
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pedido {self.id} - {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'status': self.status.value,
            'total': float(self.total),
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat(),
            'itens': [item.to_dict() for item in self.itens]
        }
    
    def calcular_total(self):
        """Calcula o total do pedido baseado nos itens"""
        self.total = sum(item.preco_unitario * item.quantidade for item in self.itens)
        return self.total

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, nullable=False)  # ID do produto (vem do serviço de produtos)
    nome_produto = db.Column(db.String(100), nullable=False)  # Cache do nome do produto
    categoria = db.Column(db.String(50), nullable=False)  # Lanche, Acompanhamento, Bebida, Sobremesa
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(Numeric(10, 2), nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<ItemPedido {self.nome_produto} x{self.quantidade}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'nome_produto': self.nome_produto,
            'categoria': self.categoria,
            'quantidade': self.quantidade,
            'preco_unitario': float(self.preco_unitario),
            'observacoes': self.observacoes,
            'subtotal': float(self.preco_unitario * self.quantidade)
        }

class Produto(db.Model):
    """Modelo para cache local de produtos (sincronizado com o serviço de produtos)"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # Lanche, Acompanhamento, Bebida, Sobremesa
    preco = db.Column(Numeric(10, 2), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    data_atualizacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria,
            'preco': float(self.preco),
            'descricao': self.descricao,
            'disponivel': self.disponivel
        }

