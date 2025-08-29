# Guia de Instalação Rápida - GDS Games

## Passo a Passo para Usar o Sistema

### 1. Preparação do Ambiente

```bash
# Instale as dependências necessárias
pip install flask flask-cors bcrypt

# Ou se preferir usar pip3
pip3 install flask flask-cors bcrypt
```

### 2. Arquivos Necessários

Certifique-se de ter os seguintes arquivos no mesmo diretório:

- `gds_database.py` - Sistema de banco de dados
- `gds_app.py` - Servidor Flask
- `gds_frontend.js` - JavaScript para integração (opcional)
- `GDS.html` - Interface web (seu arquivo original)

### 3. Executando o Sistema

```bash
# Execute o servidor Flask
python3 gds_app.py
```

Você verá uma saída similar a:
```
Iniciando servidor GDS Games...
Banco de dados inicializado
API disponível em: http://localhost:5000
Frontend disponível em: http://localhost:5000
```

### 4. Acessando o Sistema

Abra seu navegador e acesse:
- **Interface Web**: http://localhost:5000
- **API REST**: http://localhost:5000/api

### 5. Primeiro Uso

#### Login como Administrador
- **Usuário**: admin
- **Senha**: admin123

#### Ou Crie uma Nova Conta
1. Clique em "Registrar"
2. Preencha os dados
3. Faça login com suas credenciais

### 6. Funcionalidades Disponíveis

✅ **Registro e Login de Usuários**
- Senhas criptografadas com bcrypt
- Sessões seguras
- Validação de dados

✅ **Gerenciamento de Jogos**
- Adicionar novos jogos
- Buscar jogos por título/categoria
- Visualizar detalhes dos jogos

✅ **Biblioteca Pessoal**
- Adicionar jogos à sua biblioteca
- Visualizar jogos salvos
- Controle de acesso

✅ **Chat da Comunidade**
- Mensagens em tempo real
- Histórico persistente
- Usuários identificados

### 7. Estrutura de Dados

O sistema criará automaticamente:
- `gds_games.db` - Banco SQLite com todas as tabelas
- Categorias padrão (Ação, Aventura, Estratégia, etc.)
- Usuário administrador

### 8. Testando a API

```bash
# Teste básico da API
curl http://localhost:5000/api/stats

# Registrar novo usuário
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "teste", "email": "teste@example.com", "password": "senha123"}'

# Fazer login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"login": "teste", "password": "senha123"}' \
  -c cookies.txt

# Listar jogos
curl http://localhost:5000/api/games
```

### 9. Solução de Problemas Comuns

#### Porta já em uso
```bash
# Se a porta 5000 estiver ocupada, mate o processo
pkill -f "python.*gds_app"

# Ou edite gds_app.py e mude a porta na última linha:
# app.run(host='0.0.0.0', port=8000, debug=True)
```

#### Erro de dependências
```bash
# Instale as dependências uma por uma
pip3 install flask
pip3 install flask-cors  
pip3 install bcrypt
```

#### Banco não criado
```bash
# Execute o módulo do banco diretamente para testar
python3 gds_database.py
```

### 10. Próximos Passos

Após a instalação bem-sucedida:

1. **Personalize as categorias** editando `gds_database.py`
2. **Adicione jogos** através da interface web
3. **Teste o chat** com múltiplos usuários
4. **Explore a API** para integrações customizadas

### 11. Backup dos Dados

```bash
# Faça backup do banco de dados
cp gds_games.db gds_games_backup.db

# Para restaurar
cp gds_games_backup.db gds_games.db
```

### 12. Modo de Produção

Para usar em produção:

1. Mude `debug=False` em `gds_app.py`
2. Configure uma `SECRET_KEY` segura
3. Use um servidor WSGI como Gunicorn
4. Configure HTTPS

```bash
# Exemplo com Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 gds_app:app
```

---

## Resumo dos Comandos

```bash
# Instalação
pip3 install flask flask-cors bcrypt

# Execução
python3 gds_app.py

# Acesso
# http://localhost:5000
```

**Pronto! Seu sistema GDS Games com banco SQLite está funcionando!** 🎮

