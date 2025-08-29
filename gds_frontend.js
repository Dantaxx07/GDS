/**
 * GDS Frontend API Integration
 * JavaScript para integração do frontend GDS.html com a API Flask
 */

class GDSApi {
    constructor() {
        this.baseUrl = window.location.origin;
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Verifica se usuário está logado
        await this.checkAuth();
        this.setupEventListeners();
    }

    // Utilitários para requisições
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/api${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include', // Para incluir cookies de sessão
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error('Erro na API:', error);
            throw error;
        }
    }

    // Autenticação
    async checkAuth() {
        try {
            const response = await this.request('/me');
            this.currentUser = response.data;
            this.updateUI();
            return true;
        } catch (error) {
            this.currentUser = null;
            this.updateUI();
            return false;
        }
    }

    async register(username, email, password) {
        try {
            const response = await this.request('/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async login(login, password) {
        try {
            const response = await this.request('/login', {
                method: 'POST',
                body: JSON.stringify({ login, password })
            });
            this.currentUser = response.data.user;
            this.updateUI();
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async logout() {
        try {
            await this.request('/logout', { method: 'POST' });
            this.currentUser = null;
            this.updateUI();
            return { success: true };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    // Jogos
    async getGames(search = '', category = '') {
        try {
            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (category) params.append('category', category);
            
            const response = await this.request(`/games?${params}`);
            return { success: true, data: response.data.games };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async addGame(gameData) {
        try {
            const response = await this.request('/games', {
                method: 'POST',
                body: JSON.stringify(gameData)
            });
            return { success: true, data: response.data.game };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async playGame(gameId) {
        try {
            const response = await this.request(`/games/${gameId}/play`, {
                method: 'POST'
            });
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    // Biblioteca
    async getLibrary() {
        try {
            const response = await this.request('/library');
            return { success: true, data: response.data.games };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async addToLibrary(gameId) {
        try {
            const response = await this.request(`/library/${gameId}`, {
                method: 'POST'
            });
            return { success: true, message: response.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    // Chat
    async getChatMessages() {
        try {
            const response = await this.request('/chat/messages');
            return { success: true, data: response.data.messages };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async sendChatMessage(message) {
        try {
            const response = await this.request('/chat/messages', {
                method: 'POST',
                body: JSON.stringify({ message })
            });
            return { success: true, message: response.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    // Categorias
    async getCategories() {
        try {
            const response = await this.request('/categories');
            return { success: true, data: response.data.categories };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    // UI Updates
    updateUI() {
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        
        if (this.currentUser) {
            // Usuário logado
            loginBtn.innerHTML = `<i class="fas fa-user"></i> ${this.currentUser.username}`;
            loginBtn.onclick = () => this.logout();
            
            registerBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Sair';
            registerBtn.onclick = () => this.logout();
        } else {
            // Usuário não logado
            loginBtn.innerHTML = '<i class="fas fa-user"></i> Entrar';
            loginBtn.onclick = () => this.showAuthModal('login');
            
            registerBtn.innerHTML = '<i class="fas fa-user-plus"></i> Registrar';
            registerBtn.onclick = () => this.showAuthModal('register');
        }
    }

    showAuthModal(tab = 'login') {
        const modal = document.getElementById('authModal');
        modal.style.display = 'flex';
        this.switchTab(tab);
    }

    switchTab(tabId) {
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        tabContents.forEach(content => {
            if (content.id === `${tabId}Tab`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    setupEventListeners() {
        // Modal de autenticação
        const authModal = document.getElementById('authModal');
        const closeModalBtn = document.querySelector('.close-modal');
        const tabs = document.querySelectorAll('.tab');

        closeModalBtn?.addEventListener('click', () => {
            authModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === authModal) {
                authModal.style.display = 'none';
            }
        });

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                this.switchTab(tabId);
            });
        });

        // Formulário de login
        const loginForm = document.getElementById('loginForm');
        loginForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            const result = await this.login(email, password);
            if (result.success) {
                alert('Login realizado com sucesso!');
                authModal.style.display = 'none';
                this.loadGames();
                this.loadMessages();
            } else {
                alert(result.message || 'Erro no login');
            }
        });

        // Formulário de registro
        const registerForm = document.getElementById('registerForm');
        registerForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('registerName').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('registerConfirmPassword').value;
            
            if (password !== confirmPassword) {
                alert('As senhas não coincidem!');
                return;
            }
            
            const result = await this.register(name, email, password);
            if (result.success) {
                alert('Conta criada com sucesso!');
                authModal.style.display = 'none';
                this.switchTab('login');
            } else {
                alert(result.message || 'Erro no registro');
            }
        });

        // Formulário de adicionar jogo
        const gameForm = document.getElementById('gameForm');
        gameForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!this.currentUser) {
                alert('Você precisa estar logado para adicionar um jogo');
                return;
            }
            
            const gameData = {
                title: document.getElementById('gameTitle').value,
                description: document.getElementById('gameDescription').value,
                category: document.getElementById('gameCategory').value,
                image_url: document.getElementById('gameImageURL').value,
                game_url: document.getElementById('gameURL').value
            };
            
            const result = await this.addGame(gameData);
            if (result.success) {
                alert(`Jogo "${gameData.title}" adicionado com sucesso!`);
                gameForm.reset();
                this.loadGames();
            } else {
                alert(result.message || 'Erro ao adicionar jogo');
            }
        });

        // Chat
        const sendMessageBtn = document.getElementById('sendMessageBtn');
        const messageInput = document.getElementById('messageInput');

        sendMessageBtn?.addEventListener('click', () => this.sendMessage());
        messageInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Busca
        const searchInput = document.getElementById('searchInput');
        searchInput?.addEventListener('input', (e) => {
            this.searchGames(e.target.value);
        });
    }

    async sendMessage() {
        if (!this.currentUser) {
            alert('Você precisa estar logado para enviar mensagens');
            return;
        }
        
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (message) {
            const result = await this.sendChatMessage(message);
            if (result.success) {
                messageInput.value = '';
                this.loadMessages();
            } else {
                alert(result.message || 'Erro ao enviar mensagem');
            }
        }
    }

    async loadGames() {
        const result = await this.getGames();
        if (result.success) {
            this.displayGames(result.data);
        }
    }

    async searchGames(searchTerm) {
        const result = await this.getGames(searchTerm);
        if (result.success) {
            this.displayGames(result.data);
        }
    }

    displayGames(games) {
        const gamesGrid = document.getElementById('gamesGrid');
        if (!gamesGrid) return;
        
        gamesGrid.innerHTML = '';
        
        games.forEach(game => {
            const gameCard = document.createElement('div');
            gameCard.className = 'game-card';
            gameCard.innerHTML = `
                <img src="${game.image_url}" alt="${game.title}" onerror="this.src='https://via.placeholder.com/400x200/2d2d4d/6c5ce7?text=Imagem+Indisponível'">
                <div class="game-info">
                    <h3 class="game-title">${game.title}</h3>
                    <p class="game-description">${game.description}</p>
                    <div class="game-meta">
                        <div class="game-rating"><i class="fas fa-star"></i> ${game.rating || '4.8'}</div>
                        <div class="game-category">${game.category_name}</div>
                    </div>
                    <button class="btn-play" onclick="gdsApi.handlePlayGame('${game.id}', '${game.game_url}')">
                        <i class="fas fa-play"></i> Jogar Agora
                    </button>
                </div>
            `;
            gamesGrid.appendChild(gameCard);
        });
    }

    async handlePlayGame(gameId, gameUrl) {
        if (!this.currentUser) {
            alert('Você precisa estar logado para jogar');
            return;
        }
        
        const result = await this.playGame(gameId);
        if (result.success) {
            window.open(gameUrl, '_blank');
        } else {
            alert(result.message || 'Erro ao iniciar jogo');
        }
    }

    async loadMessages() {
        const result = await this.getChatMessages();
        if (result.success) {
            this.displayMessages(result.data);
        }
    }

    displayMessages(messages) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        chatMessages.innerHTML = '';
        
        messages.forEach(msg => {
            const isUser = this.currentUser && msg.username === this.currentUser.username;
            const messageElement = document.createElement('div');
            messageElement.className = `message ${isUser ? 'user' : 'other'}`;
            
            const time = new Date(msg.created_at).toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            messageElement.innerHTML = `
                <div class="message-content">
                    <div class="message-sender">${isUser ? 'Você' : msg.username}</div>
                    <div class="message-text">${msg.message}</div>
                    <div class="message-time">${time}</div>
                </div>
            `;
            
            chatMessages.appendChild(messageElement);
        });
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Inicializa a API quando a página carrega
let gdsApi;
window.addEventListener('DOMContentLoaded', () => {
    gdsApi = new GDSApi();
    
    // Carrega dados iniciais
    setTimeout(() => {
        gdsApi.loadGames();
        gdsApi.loadMessages();
    }, 500);
});

// Atualiza mensagens periodicamente
setInterval(() => {
    if (gdsApi) {
        gdsApi.loadMessages();
    }
}, 10000); // A cada 10 segundos

