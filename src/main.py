import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.pedido import db
from src.routes.pedidos import pedidos_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'pedidos_service_secret_key_2024'

# Configurar CORS para permitir comunicação entre microsserviços
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(pedidos_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'pedidos.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas
with app.app_context():
    db.create_all()

@app.route('/api/info', methods=['GET'])
def service_info():
    """Informações sobre o microsserviço"""
    return jsonify({
        'service': 'pedidos-service',
        'version': '1.0.0',
        'description': 'Microsservico responsavel pelo gerenciamento de pedidos',
        'endpoints': {
            'health': '/api/health',
            'pedidos': '/api/pedidos',
            'produtos': '/api/produtos',
            'fila': '/api/pedidos/fila'
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'service': 'pedidos-service',
                'message': 'Microsserviço de Pedidos está funcionando!',
                'api_docs': '/api/info'
            })

if __name__ == '__main__':
    print("test 3")
    app.run(host='0.0.0.0', port=5000, debug=True)
