#!/usr/bin/env python3
"""
GDS Database - Sistema de banco de dados SQLite para a plataforma GDS Games
Autor: Sistema GDS
Data: 2025

Este módulo implementa todas as funcionalidades de banco de dados necessárias
para o sistema GDS Games, incluindo:
- Gerenciamento de usuários (registro, login, autenticação)
- Gerenciamento de jogos (CRUD completo)
- Sistema de biblioteca de usuários
- Sistema de chat da comunidade
- Segurança com hash de senhas
"""

import sqlite3
import uuid
import datetime
import bcrypt
import re
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

# Configurações
DATABASE_PATH = "gds_games.db"
BCRYPT_ROUNDS = 12

class GDSDatabase:
    """Classe principal para gerenciamento do banco de dados GDS"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Inicializa o banco de dados criando todas as tabelas necessárias"""
        with self.get_connection() as conn:
            self._create_tables(conn)
            self._create_indexes(conn)
            self._insert_default_data(conn)
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Cria todas as tabelas do sistema"""
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                is_admin INTEGER DEFAULT 0,
                profile_image TEXT,
                bio TEXT
            )
        """)
        
        # Tabela de categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#6c5ce7'
            )
        """)
        
        # Tabela de jogos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                game_url TEXT NOT NULL,
                added_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                play_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (added_by) REFERENCES users(id)
            )
        """)
        
        # Tabela de biblioteca do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                game_id TEXT NOT NULL,
                added_at TEXT NOT NULL,
                status TEXT DEFAULT 'owned',
                last_played TEXT,
                play_time INTEGER DEFAULT 0,
                UNIQUE(user_id, game_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de mensagens do chat
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de avaliações de jogos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                game_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, game_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de sessões de usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Cria índices para otimização de consultas"""
        cursor = conn.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_games_title ON games(title)",
            "CREATE INDEX IF NOT EXISTS idx_games_category ON games(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_games_created_at ON games(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_user_library_user_id ON user_library(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_library_game_id ON user_library(game_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_game_ratings_game_id ON game_ratings(game_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
    
    def _insert_default_data(self, conn: sqlite3.Connection):
        """Insere dados padrão no banco"""
        cursor = conn.cursor()
        
        # Verifica se já existem dados
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            return
        
        # Categorias padrão
        categories = [
            ('acao', 'Ação', 'Jogos de ação e aventura', '#e74c3c'),
            ('aventura', 'Aventura', 'Jogos de aventura e exploração', '#3498db'),
            ('estrategia', 'Estratégia', 'Jogos de estratégia e planejamento', '#9b59b6'),
            ('corrida', 'Corrida', 'Jogos de corrida e velocidade', '#f39c12'),
            ('puzzle', 'Puzzle', 'Jogos de quebra-cabeça e lógica', '#2ecc71'),
            ('rpg', 'RPG', 'Jogos de interpretação de papéis', '#e67e22'),
            ('esporte', 'Esporte', 'Jogos esportivos', '#1abc9c'),
            ('simulacao', 'Simulação', 'Jogos de simulação', '#34495e')
        ]
        
        for cat_id, name, desc, color in categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, description, color)
                VALUES (?, ?, ?)
            """, (name, desc, color))
        
        # Usuário administrador padrão
        admin_id = str(uuid.uuid4())
        admin_password = self._hash_password("admin123")
        now = self._get_timestamp()
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, email, password_hash, created_at, is_admin)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (admin_id, "admin", "admin@gdsgames.com", admin_password, now))
        
        conn.commit()
    
    # Utilitários
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em formato ISO"""
        return datetime.datetime.utcnow().isoformat()
    
    def _generate_uuid(self) -> str:
        """Gera um UUID único"""
        return str(uuid.uuid4())
    
    def _hash_password(self, password: str) -> str:
        """Gera hash da senha usando bcrypt"""
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_username(self, username: str) -> bool:
        """Valida formato de username"""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    # Métodos de usuário
    def create_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Cria um novo usuário
        Retorna: (sucesso, mensagem/user_id)
        """
        # Validações
        if not self._validate_username(username):
            return False, "Nome de usuário inválido. Use apenas letras, números e _ (3-20 caracteres)"
        
        if not self._validate_email(email):
            return False, "Email inválido"
        
        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se usuário já existe
            cursor.execute("""
                SELECT 1 FROM users WHERE username = ? OR email = ?
            """, (username, email))
            
            if cursor.fetchone():
                return False, "Nome de usuário ou email já existe"
            
            # Cria usuário
            user_id = self._generate_uuid()
            password_hash = self._hash_password(password)
            now = self._get_timestamp()
            
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, email, password_hash, now))
            
            conn.commit()
            return True, user_id
    
    def authenticate_user(self, login: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário por username ou email
        Retorna: dados do usuário se sucesso, None se falha
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) AND is_active = 1
            """, (login, login))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            if not self._verify_password(password, user['password_hash']):
                return None
            
            # Atualiza último login
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (self._get_timestamp(), user['id']))
            
            conn.commit()
            
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': bool(user['is_admin']),
                'created_at': user['created_at'],
                'last_login': user['last_login']
            }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, created_at, last_login, is_admin, profile_image, bio
                FROM users WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    # Métodos de jogos
    def add_game(self, title: str, description: str, category: str, image_url: str, 
                 game_url: str, added_by: str) -> Tuple[bool, str]:
        """
        Adiciona um novo jogo
        Retorna: (sucesso, mensagem/game_id)
        """
        if not all([title, description, category, image_url, game_url]):
            return False, "Todos os campos são obrigatórios"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Busca ID da categoria
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            cat_row = cursor.fetchone()
            if not cat_row:
                return False, "Categoria inválida"
            
            category_id = cat_row['id']
            
            # Verifica se jogo já existe
            cursor.execute("SELECT 1 FROM games WHERE title = ? AND added_by = ?", (title, added_by))
            if cursor.fetchone():
                return False, "Você já adicionou um jogo com este título"
            
            # Adiciona jogo
            game_id = self._generate_uuid()
            now = self._get_timestamp()
            
            cursor.execute("""
                INSERT INTO games (id, title, description, category_id, image_url, 
                                 game_url, added_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (game_id, title, description, category_id, image_url, 
                  game_url, added_by, now, now))
            
            conn.commit()
            return True, game_id
    
    def get_games(self, search: str = None, category: str = None, 
                  limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Busca jogos com filtros opcionais
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT g.*, c.name as category_name, c.color as category_color,
                       u.username as added_by_username
                FROM games g
                JOIN categories c ON g.category_id = c.id
                JOIN users u ON g.added_by = u.id
                WHERE g.is_active = 1
            """
            params = []
            
            if search:
                query += " AND (g.title LIKE ? OR g.description LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            
            if category:
                query += " AND c.name = ?"
                params.append(category)
            
            query += " ORDER BY g.created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            games = cursor.fetchall()
            
            return [dict(game) for game in games]
    
    def get_game_by_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Busca jogo por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.*, c.name as category_name, c.color as category_color,
                       u.username as added_by_username
                FROM games g
                JOIN categories c ON g.category_id = c.id
                JOIN users u ON g.added_by = u.id
                WHERE g.id = ? AND g.is_active = 1
            """, (game_id,))
            
            game = cursor.fetchone()
            return dict(game) if game else None
    
    def increment_play_count(self, game_id: str):
        """Incrementa contador de jogadas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE games SET play_count = play_count + 1 WHERE id = ?
            """, (game_id,))
            conn.commit()
    
    # Métodos de biblioteca
    def add_to_library(self, user_id: str, game_id: str) -> Tuple[bool, str]:
        """Adiciona jogo à biblioteca do usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se jogo existe
            cursor.execute("SELECT 1 FROM games WHERE id = ? AND is_active = 1", (game_id,))
            if not cursor.fetchone():
                return False, "Jogo não encontrado"
            
            # Verifica se já está na biblioteca
            cursor.execute("""
                SELECT 1 FROM user_library WHERE user_id = ? AND game_id = ?
            """, (user_id, game_id))
            
            if cursor.fetchone():
                return False, "Jogo já está na sua biblioteca"
            
            # Adiciona à biblioteca
            cursor.execute("""
                INSERT INTO user_library (user_id, game_id, added_at)
                VALUES (?, ?, ?)
            """, (user_id, game_id, self._get_timestamp()))
            
            conn.commit()
            return True, "Jogo adicionado à biblioteca"
    
    def get_user_library(self, user_id: str) -> List[Dict[str, Any]]:
        """Busca biblioteca do usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.*, c.name as category_name, c.color as category_color,
                       ul.added_at, ul.status, ul.last_played, ul.play_time
                FROM user_library ul
                JOIN games g ON ul.game_id = g.id
                JOIN categories c ON g.category_id = c.id
                WHERE ul.user_id = ? AND g.is_active = 1
                ORDER BY ul.added_at DESC
            """, (user_id,))
            
            games = cursor.fetchall()
            return [dict(game) for game in games]
    
    def remove_from_library(self, user_id: str, game_id: str) -> bool:
        """Remove jogo da biblioteca"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_library WHERE user_id = ? AND game_id = ?
            """, (user_id, game_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Métodos de chat
    def add_chat_message(self, user_id: str, message: str) -> Tuple[bool, str]:
        """Adiciona mensagem ao chat"""
        if not message.strip():
            return False, "Mensagem não pode estar vazia"
        
        if len(message) > 500:
            return False, "Mensagem muito longa (máximo 500 caracteres)"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (user_id, message, created_at)
                VALUES (?, ?, ?)
            """, (user_id, message.strip(), self._get_timestamp()))
            
            conn.commit()
            return True, "Mensagem enviada"
    
    def get_chat_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca mensagens do chat"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cm.*, u.username
                FROM chat_messages cm
                JOIN users u ON cm.user_id = u.id
                WHERE cm.is_deleted = 0
                ORDER BY cm.created_at DESC
                LIMIT ?
            """, (limit,))
            
            messages = cursor.fetchall()
            return [dict(msg) for msg in reversed(messages)]
    
    # Métodos de categorias
    def get_categories(self) -> List[Dict[str, Any]]:
        """Busca todas as categorias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            categories = cursor.fetchall()
            return [dict(cat) for cat in categories]
    
    # Métodos de estatísticas
    def get_stats(self) -> Dict[str, Any]:
        """Busca estatísticas gerais do sistema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de usuários
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            total_users = cursor.fetchone()[0]
            
            # Total de jogos
            cursor.execute("SELECT COUNT(*) FROM games WHERE is_active = 1")
            total_games = cursor.fetchone()[0]
            
            # Total de mensagens
            cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE is_deleted = 0")
            total_messages = cursor.fetchone()[0]
            
            # Jogo mais popular
            cursor.execute("""
                SELECT title, play_count FROM games 
                WHERE is_active = 1 
                ORDER BY play_count DESC 
                LIMIT 1
            """)
            popular_game = cursor.fetchone()
            
            return {
                'total_users': total_users,
                'total_games': total_games,
                'total_messages': total_messages,
                'popular_game': dict(popular_game) if popular_game else None
            }


# Instância global do banco
db = GDSDatabase()

# Funções de conveniência para compatibilidade
def get_connection():
    """Função de compatibilidade"""
    return db.get_connection()

def create_user(username: str, email: str, password: str):
    """Função de compatibilidade"""
    return db.create_user(username, email, password)

def authenticate_user(login: str, password: str):
    """Função de compatibilidade"""
    return db.authenticate_user(login, password)


if __name__ == "__main__":
    # Teste básico
    print("Inicializando banco de dados GDS...")
    
    # Testa criação de usuário
    success, result = db.create_user("teste", "teste@example.com", "senha123")
    if success:
        print(f"Usuário criado com sucesso: {result}")
    else:
        print(f"Erro ao criar usuário: {result}")
    
    # Testa autenticação
    user = db.authenticate_user("teste", "senha123")
    if user:
        print(f"Login bem-sucedido: {user['username']}")
    else:
        print("Falha no login")
    
    # Mostra estatísticas
    stats = db.get_stats()
    print(f"Estatísticas: {stats}")
    
    print("Banco de dados inicializado com sucesso!")

