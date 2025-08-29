#!/usr/bin/env python3
"""
GDS Games - Aplicação Flask Backend
Autor: Sistema GDS
Data: 2025

Esta aplicação Flask fornece uma API REST completa para o sistema GDS Games,
incluindo autenticação, gerenciamento de jogos, biblioteca de usuários e chat.
"""

from flask import Flask, request, jsonify, session, render_template_string, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
from functools import wraps
from gds_database import GDSDatabase

# Configuração da aplicação
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gds-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # True em produção com HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Habilita CORS para todas as rotas
CORS(app, supports_credentials=True)

# Instância do banco de dados
db = GDSDatabase()

# Decorador para rotas que requerem autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rotas que requerem admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticação necessária'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if not user or not user.get('is_admin'):
            return jsonify({'error': 'Acesso negado - Admin necessário'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Utilitários
def get_current_user():
    """Retorna dados do usuário atual da sessão"""
    if 'user_id' not in session:
        return None
    return db.get_user_by_id(session['user_id'])

def format_response(success=True, message="", data=None):
    """Formata resposta padrão da API"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return response

# Rotas de autenticação
@app.route('/api/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(format_response(False, "Dados não fornecidos")), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not all([username, email, password]):
            return jsonify(format_response(False, "Todos os campos são obrigatórios")), 400
        
        success, result = db.create_user(username, email, password)
        
        if success:
            return jsonify(format_response(True, "Usuário criado com sucesso", {
                'user_id': result,
                'username': username
            })), 201
        else:
            return jsonify(format_response(False, result)), 400
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Autentica usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(format_response(False, "Dados não fornecidos")), 400
        
        login_field = data.get('login', '').strip()  # username ou email
        password = data.get('password', '')
        
        if not all([login_field, password]):
            return jsonify(format_response(False, "Login e senha são obrigatórios")), 400
        
        user = db.authenticate_user(login_field, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            return jsonify(format_response(True, "Login realizado com sucesso", {
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user['is_admin']
                }
            }))
        else:
            return jsonify(format_response(False, "Credenciais inválidas")), 401
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Faz logout do usuário"""
    session.clear()
    return jsonify(format_response(True, "Logout realizado com sucesso"))

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user_info():
    """Retorna informações do usuário atual"""
    user = get_current_user()
    if user:
        return jsonify(format_response(True, "Dados do usuário", user))
    else:
        return jsonify(format_response(False, "Usuário não encontrado")), 404

# Rotas de jogos
@app.route('/api/games', methods=['GET'])
def get_games():
    """Lista jogos com filtros opcionais"""
    try:
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        limit = min(int(request.args.get('limit', 50)), 100)  # máximo 100
        offset = int(request.args.get('offset', 0))
        
        games = db.get_games(
            search=search if search else None,
            category=category if category else None,
            limit=limit,
            offset=offset
        )
        
        return jsonify(format_response(True, "Jogos encontrados", {
            'games': games,
            'count': len(games),
            'search': search,
            'category': category
        }))
        
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/games', methods=['POST'])
@login_required
def add_game():
    """Adiciona um novo jogo"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(format_response(False, "Dados não fornecidos")), 400
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', '').strip()
        image_url = data.get('image_url', '').strip()
        game_url = data.get('game_url', '').strip()
        
        if not all([title, description, category, image_url, game_url]):
            return jsonify(format_response(False, "Todos os campos são obrigatórios")), 400
        
        success, result = db.add_game(
            title=title,
            description=description,
            category=category,
            image_url=image_url,
            game_url=game_url,
            added_by=session['user_id']
        )
        
        if success:
            game = db.get_game_by_id(result)
            return jsonify(format_response(True, "Jogo adicionado com sucesso", {
                'game': game
            })), 201
        else:
            return jsonify(format_response(False, result)), 400
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/games/<game_id>', methods=['GET'])
def get_game(game_id):
    """Busca jogo por ID"""
    try:
        game = db.get_game_by_id(game_id)
        if game:
            return jsonify(format_response(True, "Jogo encontrado", game))
        else:
            return jsonify(format_response(False, "Jogo não encontrado")), 404
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/games/<game_id>/play', methods=['POST'])
@login_required
def play_game(game_id):
    """Registra que o usuário jogou um jogo"""
    try:
        game = db.get_game_by_id(game_id)
        if not game:
            return jsonify(format_response(False, "Jogo não encontrado")), 404
        
        # Incrementa contador de jogadas
        db.increment_play_count(game_id)
        
        # Adiciona à biblioteca se não estiver
        db.add_to_library(session['user_id'], game_id)
        
        return jsonify(format_response(True, "Jogo iniciado", {
            'game_url': game['game_url'],
            'title': game['title']
        }))
        
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

# Rotas de biblioteca
@app.route('/api/library', methods=['GET'])
@login_required
def get_user_library():
    """Busca biblioteca do usuário"""
    try:
        games = db.get_user_library(session['user_id'])
        return jsonify(format_response(True, "Biblioteca do usuário", {
            'games': games,
            'count': len(games)
        }))
        
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/library/<game_id>', methods=['POST'])
@login_required
def add_to_library(game_id):
    """Adiciona jogo à biblioteca"""
    try:
        success, message = db.add_to_library(session['user_id'], game_id)
        
        if success:
            return jsonify(format_response(True, message))
        else:
            return jsonify(format_response(False, message)), 400
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/library/<game_id>', methods=['DELETE'])
@login_required
def remove_from_library(game_id):
    """Remove jogo da biblioteca"""
    try:
        success = db.remove_from_library(session['user_id'], game_id)
        
        if success:
            return jsonify(format_response(True, "Jogo removido da biblioteca"))
        else:
            return jsonify(format_response(False, "Jogo não encontrado na biblioteca")), 404
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

# Rotas de chat
@app.route('/api/chat/messages', methods=['GET'])
def get_chat_messages():
    """Busca mensagens do chat"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        messages = db.get_chat_messages(limit)
        
        return jsonify(format_response(True, "Mensagens do chat", {
            'messages': messages,
            'count': len(messages)
        }))
        
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

@app.route('/api/chat/messages', methods=['POST'])
@login_required
def send_chat_message():
    """Envia mensagem no chat"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(format_response(False, "Dados não fornecidos")), 400
        
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify(format_response(False, "Mensagem não pode estar vazia")), 400
        
        success, result = db.add_chat_message(session['user_id'], message)
        
        if success:
            return jsonify(format_response(True, result))
        else:
            return jsonify(format_response(False, result)), 400
            
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

# Rotas de categorias
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Lista todas as categorias"""
    try:
        categories = db.get_categories()
        return jsonify(format_response(True, "Categorias encontradas", {
            'categories': categories
        }))
        
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

# Rotas de estatísticas
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Busca estatísticas do sistema"""
    try:
        stats = db.get_stats()
        return jsonify(format_response(True, "Estatísticas do sistema", stats))
        
    except Exception as e:
        return jsonify(format_response(False, f"Erro interno: {str(e)}")), 500

# Rota para servir o frontend
@app.route('/')
def index():
    """Serve a página principal"""
    try:
        with open('/home/ubuntu/upload/GDS.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Modifica o HTML para usar a API
        modified_html = html_content.replace(
            'localStorage.getItem',
            '// localStorage.getItem'
        ).replace(
            'localStorage.setItem',
            '// localStorage.setItem'
        )
        
        return render_template_string(modified_html)
    except FileNotFoundError:
        return jsonify(format_response(False, "Arquivo HTML não encontrado")), 404

# Rota para servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    return send_from_directory('/home/ubuntu/upload', filename)

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify(format_response(False, "Endpoint não encontrado")), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(format_response(False, "Erro interno do servidor")), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(format_response(False, "Método não permitido")), 405

# Middleware para logging
@app.before_request
def log_request():
    """Log de requisições"""
    if request.endpoint and not request.endpoint.startswith('static'):
        print(f"[{datetime.now()}] {request.method} {request.path} - User: {session.get('username', 'Anonymous')}")

# Configuração para desenvolvimento
if __name__ == '__main__':
    print("Iniciando servidor GDS Games...")
    print("Banco de dados inicializado")
    print("API disponível em: http://localhost:5000")
    print("Frontend disponível em: http://localhost:5000")
    print("\nEndpoints da API:")
    print("POST /api/register - Registrar usuário")
    print("POST /api/login - Fazer login")
    print("POST /api/logout - Fazer logout")
    print("GET  /api/me - Dados do usuário atual")
    print("GET  /api/games - Listar jogos")
    print("POST /api/games - Adicionar jogo")
    print("GET  /api/games/<id> - Buscar jogo")
    print("POST /api/games/<id>/play - Jogar jogo")
    print("GET  /api/library - Biblioteca do usuário")
    print("POST /api/library/<id> - Adicionar à biblioteca")
    print("DELETE /api/library/<id> - Remover da biblioteca")
    print("GET  /api/chat/messages - Mensagens do chat")
    print("POST /api/chat/messages - Enviar mensagem")
    print("GET  /api/categories - Listar categorias")
    print("GET  /api/stats - Estatísticas do sistema")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

