# Instagram Clone

Um clone completo do Instagram desenvolvido com Python (FastAPI) no backend e React no frontend.

## 🎯 Demonstração

### Funcionalidades Principais
- 📱 **Interface idêntica ao Instagram** - Design responsivo e moderno
- 🖼️ **Posts com múltiplas mídias** - Imagens e vídeos em carrossel
- 📖 **Stories temporários** - Conteúdo que expira em 24h
- 💬 **Chat privado** - Mensagens diretas com imagens
- 🔔 **Notificações em tempo real** - Likes, comentários, seguidores
- 🔍 **Busca inteligente** - Usuários e hashtags
- #️⃣ **Hashtags automáticas** - Sistema completo de tags
- 👥 **Sistema social completo** - Seguir, curtir, comentar

## Funcionalidades

### Backend (Python/FastAPI)
- ✅ **Autenticação JWT** - Sistema completo de login/registro
- ✅ **Sistema de Posts** - Upload de imagens e vídeos
- ✅ **Sistema de Likes** - Curtir/descurtir posts
- ✅ **Sistema de Comentários** - Comentários em posts
- ✅ **Sistema de Seguidores** - Seguir/deixar de seguir usuários
- ✅ **Stories** - Conteúdo temporário (24h) com visualizações
- ✅ **Direct Messages** - Mensagens privadas com imagens
- ✅ **Notificações** - Sistema completo de notificações
- ✅ **Busca de Usuários** - Busca por username/nome
- ✅ **Hashtags** - Sistema automático de hashtags
- ✅ **Múltiplas Imagens** - Até 10 imagens por post
- ✅ **Vídeos** - Upload e reprodução de vídeos
- ✅ **Feed Personalizado** - Baseado em quem você segue
- ✅ **API REST Completa** - Documentação automática

### Frontend (React)
- ✅ **Interface Responsiva** - Similar ao Instagram original
- ✅ **Autenticação** - Login/registro com validação
- ✅ **Feed Principal** - Posts com carrossel de mídia
- ✅ **Stories** - Visualizador modal com navegação
- ✅ **Upload Avançado** - Múltiplas imagens e vídeos
- ✅ **Player de Vídeo** - Controles personalizados
- ✅ **Perfis de Usuário** - Estatísticas e grid de posts
- ✅ **Sistema de Chat** - Interface de mensagens
- ✅ **Notificações** - Centro de notificações
- ✅ **Busca Inteligente** - Busca em tempo real
- ✅ **Hashtags Clicáveis** - Páginas dedicadas por hashtag
- ✅ **Trending Hashtags** - Sidebar com hashtags populares

## Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python com relacionamentos complexos
- **SQLite** - Banco de dados (desenvolvimento)
- **JWT** - Autenticação segura com tokens
- **Pillow** - Processamento de imagens
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic** - Validação de dados e serialização

### Frontend
- **React** - Biblioteca JavaScript com hooks
- **React Router** - Roteamento SPA completo
- **Axios** - Cliente HTTP com interceptors
- **CSS3** - Estilização responsiva avançada
- **HTML5 Video** - Player de vídeo nativo

## Como Executar

### Opção 1: Com Docker (Recomendado)

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd clone-insta
```

2. Execute com Docker Compose:
```bash
docker-compose up --build
```

3. Acesse:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

4. **Criar usuários de demonstração (opcional):**
   ```bash
   python3 create_demo_users.py
   ```

5. **Fazer login:**
   - **Usuários demo**: john_doe, jane_smith, mike_wilson, sarah_jones, alex_brown
   - **Senha**: password123
   - **Ou criar sua própria conta**

6. **Teste as funcionalidades:**
   - **Posts**: Upload de múltiplas imagens/vídeos
   - **Stories**: Criar e visualizar stories temporários
   - **Messages**: Chat privado com outros usuários
   - **Notificações**: Centro de atividades
   - **Busca**: Encontrar usuários e hashtags
   - **Hashtags**: Explorar conteúdo por tópicos

### Opção 2: Execução Manual

#### Backend
1. Entre na pasta do backend:
```bash
cd backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o servidor:
```bash
uvicorn main:app --reload
```

#### Frontend
1. Entre na pasta do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Execute o servidor de desenvolvimento:
```bash
npm start
```

## Estrutura do Projeto

```
clone-insta/
├── backend/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── models.py            # Modelos de dados
│   ├── schemas.py           # Schemas Pydantic
│   ├── database.py          # Configuração do banco
│   ├── auth.py              # Sistema de autenticação
│   ├── requirements.txt     # Dependências Python
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/           # Páginas da aplicação
│   │   ├── services/        # Serviços de API
│   │   ├── App.js           # Componente principal
│   │   └── index.js         # Ponto de entrada
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

## API Endpoints

### Autenticação
- `POST /auth/register` - Registrar usuário
- `POST /auth/login` - Login

### Usuários
- `GET /users/me` - Perfil do usuário atual
- `GET /users/{username}` - Perfil de usuário
- `POST /users/{username}/follow` - Seguir usuário
- `DELETE /users/{username}/follow` - Deixar de seguir

### Posts
- `POST /posts` - Criar post (imagens/vídeos)
- `GET /posts` - Feed de posts
- `GET /posts/{post_id}` - Post específico
- `POST /posts/{post_id}/like` - Curtir post
- `DELETE /posts/{post_id}/like` - Descurtir post

### Comentários
- `POST /posts/{post_id}/comments` - Criar comentário
- `GET /posts/{post_id}/comments` - Listar comentários

### Stories
- `POST /stories` - Criar story
- `GET /stories` - Listar stories
- `GET /stories/user/{username}` - Stories de usuário
- `POST /stories/{story_id}/view` - Marcar como visto
- `GET /stories/{story_id}/views` - Ver visualizações

### Direct Messages
- `GET /conversations` - Listar conversas
- `GET /conversations/{user_id}` - Obter/criar conversa
- `GET /conversations/{conversation_id}/messages` - Mensagens
- `POST /messages` - Enviar mensagem
- `POST /messages/image` - Enviar imagem

### Notificações
- `GET /notifications` - Listar notificações
- `GET /notifications/unread-count` - Contador não lidas
- `POST /notifications/{id}/read` - Marcar como lida
- `POST /notifications/mark-all-read` - Marcar todas como lidas

### Busca
- `GET /search/users` - Buscar usuários
- `GET /search/hashtags` - Buscar hashtags

### Hashtags
- `GET /hashtags/{name}` - Dados da hashtag
- `GET /hashtags/{name}/posts` - Posts da hashtag
- `GET /hashtags/trending` - Hashtags em alta

## Configuração

### Variáveis de Ambiente (.env)
```
DATABASE_URL=sqlite:///./instagram_clone.db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Funcionalidades Implementadas ✅

- ✅ **Stories** - Conteúdo temporário com visualizações
- ✅ **Direct Messages** - Chat privado com imagens
- ✅ **Notificações** - Sistema completo de notificações
- ✅ **Busca de usuários** - Busca em tempo real
- ✅ **Hashtags** - Sistema automático com trending
- ✅ **Múltiplas imagens por post** - Até 10 imagens
- ✅ **Vídeos** - Upload e player personalizado

## Possíveis Melhorias Futuras

- [ ] **Stories Avançados** - Enquetes, perguntas, música
- [ ] **Reels** - Vídeos curtos verticais
- [ ] **IGTV** - Vídeos longos
- [ ] **Live Streaming** - Transmissões ao vivo
- [ ] **Explore Page** - Descoberta de conteúdo
- [ ] **Shopping** - Tags de produtos
- [ ] **Dark Mode** - Tema escuro
- [ ] **PWA** - Progressive Web App
- [ ] **Push Notifications** - Notificações em tempo real
- [ ] **Deploy em produção** - AWS/Heroku/Vercel

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.