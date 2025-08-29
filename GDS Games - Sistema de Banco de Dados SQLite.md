# GDS Games - Sistema de Banco de Dados SQLite

## Visão Geral

Este projeto implementa um sistema completo de banco de dados SQLite para a plataforma GDS Games, substituindo o armazenamento local (localStorage) por um banco de dados robusto e seguro. O sistema inclui:

- **Autenticação de usuários** com registro e login seguros
- **Gerenciamento de jogos** com CRUD completo
- **Sistema de biblioteca pessoal** para cada usuário
- **Chat da comunidade** em tempo real
- **API REST completa** para integração frontend/backend
- **Interface web responsiva** já integrada

## Arquitetura do Sistema

### Componentes Principais

1. **gds_database.py** - Módulo principal do banco de dados
2. **gds_app.py** - Aplicação Flask com API REST
3. **gds_frontend.js** - JavaScript para integração com a API
4. **GDS.html** - Interface web (arquivo original do usuário)

### Estrutura do Banco de Dados

O banco SQLite (`gds_games.db`) contém as seguintes tabelas:

#### Tabela `users`
- `id` (TEXT PRIMARY KEY) - UUID único do usuário
- `username` (TEXT UNIQUE) - Nome de usuário único
- `email` (TEXT UNIQUE) - Email único
- `password_hash` (TEXT) - Hash bcrypt da senha
- `created_at` (TEXT) - Data de criação
- `last_login` (TEXT) - Último login
- `is_active` (INTEGER) - Status ativo (1/0)
- `is_admin` (INTEGER) - Permissão admin (1/0)

#### Tabela `categories`
- `id` (INTEGER PRIMARY KEY) - ID da categoria
- `name` (TEXT UNIQUE) - Nome da categoria
- `description` (TEXT) - Descrição
- `color` (TEXT) - Cor hexadecimal

#### Tabela `games`
- `id` (TEXT PRIMARY KEY) - UUID único do jogo
- `title` (TEXT) - Título do jogo
- `description` (TEXT) - Descrição
- `category_id` (INTEGER) - FK para categories
- `image_url` (TEXT) - URL da imagem
- `game_url` (TEXT) - URL do jogo
- `added_by` (TEXT) - FK para users
- `created_at` (TEXT) - Data de criação
- `updated_at` (TEXT) - Data de atualização
- `is_active` (INTEGER) - Status ativo
- `play_count` (INTEGER) - Contador de jogadas
- `rating` (REAL) - Avaliação média

#### Tabela `user_library`
- `id` (INTEGER PRIMARY KEY) - ID da entrada
- `user_id` (TEXT) - FK para users
- `game_id` (TEXT) - FK para games
- `added_at` (TEXT) - Data de adição
- `status` (TEXT) - Status (owned, wishlist, etc.)

#### Tabela `chat_messages`
- `id` (INTEGER PRIMARY KEY) - ID da mensagem
- `user_id` (TEXT) - FK para users
- `message` (TEXT) - Conteúdo da mensagem
- `created_at` (TEXT) - Data de criação
- `is_deleted` (INTEGER) - Status de exclusão

## Instalação e Configuração

### Pré-requisitos

```bash
pip install flask flask-cors bcrypt
```

### Inicialização do Banco

O banco é criado automaticamente na primeira execução:

```python
from gds_database import GDSDatabase

# Cria e inicializa o banco
db = GDSDatabase()
```

### Executando o Servidor

```bash
python3 gds_app.py
```

O servidor estará disponível em:
- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/api

## API REST - Endpoints

### Autenticação

#### POST /api/register
Registra um novo usuário.

**Payload:**
```json
{
  "username": "usuario",
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Usuário criado com sucesso",
  "data": {
    "user_id": "uuid-do-usuario",
    "username": "usuario"
  }
}
```

#### POST /api/login
Autentica um usuário.

**Payload:**
```json
{
  "login": "usuario_ou_email",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "data": {
    "user": {
      "id": "uuid",
      "username": "usuario",
      "email": "email@example.com",
      "is_admin": false
    }
  }
}
```

#### POST /api/logout
Faz logout do usuário atual.

#### GET /api/me
Retorna dados do usuário logado.

### Jogos

#### GET /api/games
Lista jogos com filtros opcionais.

**Parâmetros de query:**
- `search` - Busca por título/descrição
- `category` - Filtra por categoria
- `limit` - Limite de resultados (máx 100)
- `offset` - Offset para paginação

#### POST /api/games
Adiciona um novo jogo (requer login).

**Payload:**
```json
{
  "title": "Nome do Jogo",
  "description": "Descrição do jogo",
  "category": "Ação",
  "image_url": "https://example.com/imagem.jpg",
  "game_url": "https://example.com/jogo"
}
```

#### GET /api/games/{id}
Busca jogo específico por ID.

#### POST /api/games/{id}/play
Registra que o usuário jogou (incrementa contador).

### Biblioteca

#### GET /api/library
Lista jogos na biblioteca do usuário logado.

#### POST /api/library/{game_id}
Adiciona jogo à biblioteca.

#### DELETE /api/library/{game_id}
Remove jogo da biblioteca.

### Chat

#### GET /api/chat/messages
Lista mensagens do chat.

**Parâmetros:**
- `limit` - Número de mensagens (máx 100)

#### POST /api/chat/messages
Envia mensagem no chat (requer login).

**Payload:**
```json
{
  "message": "Texto da mensagem"
}
```

### Outros

#### GET /api/categories
Lista todas as categorias disponíveis.

#### GET /api/stats
Retorna estatísticas do sistema.

## Segurança

### Hash de Senhas
- Utiliza bcrypt com 12 rounds para hash das senhas
- Senhas nunca são armazenadas em texto plano

### Autenticação
- Sistema de sessões Flask com cookies seguros
- Validação de entrada em todos os endpoints
- Proteção contra SQL injection (uso de prepared statements)

### Validações
- Email: formato RFC válido
- Username: 3-20 caracteres, apenas letras, números e _
- Senha: mínimo 6 caracteres
- URLs: validação básica de formato

## Uso Programático

### Exemplo de Uso Direto do Banco

```python
from gds_database import GDSDatabase

# Inicializa banco
db = GDSDatabase()

# Cria usuário
success, user_id = db.create_user("joao", "joao@example.com", "senha123")

# Autentica usuário
user = db.authenticate_user("joao", "senha123")

# Adiciona jogo
success, game_id = db.add_game(
    title="Meu Jogo",
    description="Descrição do jogo",
    category="Ação",
    image_url="https://example.com/img.jpg",
    game_url="https://example.com/jogo",
    added_by=user_id
)

# Lista jogos
games = db.get_games(search="Meu")

# Adiciona à biblioteca
db.add_to_library(user_id, game_id)
```

### Exemplo de Uso da API

```python
import requests

base_url = "http://localhost:5000/api"

# Registra usuário
response = requests.post(f"{base_url}/register", json={
    "username": "teste",
    "email": "teste@example.com", 
    "password": "senha123"
})

# Faz login
session = requests.Session()
response = session.post(f"{base_url}/login", json={
    "login": "teste",
    "password": "senha123"
})

# Adiciona jogo
response = session.post(f"{base_url}/games", json={
    "title": "Jogo Teste",
    "description": "Descrição",
    "category": "Ação",
    "image_url": "https://example.com/img.jpg",
    "game_url": "https://example.com/jogo"
})
```

## Dados Iniciais

O sistema é inicializado com:

### Usuário Administrador
- **Username**: admin
- **Email**: admin@gdsgames.com
- **Senha**: admin123

### Categorias Padrão
- Ação (#e74c3c)
- Aventura (#3498db)
- Estratégia (#9b59b6)
- Corrida (#f39c12)
- Puzzle (#2ecc71)
- RPG (#e67e22)
- Esporte (#1abc9c)
- Simulação (#34495e)

## Estrutura de Arquivos

```
projeto/
├── gds_database.py      # Módulo principal do banco
├── gds_app.py          # Aplicação Flask
├── gds_frontend.js     # JavaScript para integração
├── GDS.html           # Interface web original
├── gds_games.db       # Banco SQLite (criado automaticamente)
├── README.md          # Esta documentação
└── database_schema.md # Documentação do esquema
```

## Troubleshooting

### Erro "Address already in use"
```bash
# Mata processos na porta 5000
pkill -f "python.*gds_app"
# Ou use porta diferente
python3 gds_app.py --port 8000
```

### Banco corrompido
```bash
# Remove banco para recriar
rm gds_games.db
python3 gds_app.py
```

### Problemas de CORS
O servidor já está configurado com CORS habilitado. Se ainda houver problemas, verifique se está acessando via localhost.

## Desenvolvimento

### Adicionando Novas Funcionalidades

1. **Nova tabela**: Adicione em `_create_tables()` no `gds_database.py`
2. **Novo endpoint**: Adicione rota no `gds_app.py`
3. **Frontend**: Atualize `gds_frontend.js` se necessário

### Testes

```bash
# Testa banco diretamente
python3 gds_database.py

# Testa API
curl -X GET http://localhost:5000/api/stats
```

## Licença

Este projeto foi desenvolvido para o sistema GDS Games e está disponível para uso conforme necessário.

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs do servidor Flask
2. Consulte esta documentação
3. Teste os endpoints da API diretamente
4. Verifique se o banco SQLite foi criado corretamente

