# Instagram Clone

Um clone do Instagram desenvolvido com Python (FastAPI) no backend e React no frontend.

## Funcionalidades

### Backend (Python/FastAPI)
- ✅ Autenticação JWT
- ✅ Registro e login de usuários
- ✅ Upload de imagens
- ✅ Sistema de posts
- ✅ Sistema de likes
- ✅ Sistema de comentários
- ✅ Sistema de seguir/seguidores
- ✅ Feed personalizado
- ✅ API REST completa

### Frontend (React)
- ✅ Interface responsiva similar ao Instagram
- ✅ Autenticação de usuários
- ✅ Feed de posts
- ✅ Upload de fotos
- ✅ Perfil de usuário
- ✅ Sistema de likes e comentários
- ✅ Sistema de seguir/não seguir

## Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **SQLite** - Banco de dados (desenvolvimento)
- **JWT** - Autenticação
- **Pillow** - Processamento de imagens
- **Uvicorn** - Servidor ASGI

### Frontend
- **React** - Biblioteca JavaScript
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **CSS3** - Estilização

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
- `POST /posts` - Criar post
- `GET /posts` - Feed de posts
- `GET /posts/{post_id}` - Post específico
- `POST /posts/{post_id}/like` - Curtir post
- `DELETE /posts/{post_id}/like` - Descurtir post

### Comentários
- `POST /posts/{post_id}/comments` - Criar comentário
- `GET /posts/{post_id}/comments` - Listar comentários

## Configuração

### Variáveis de Ambiente (.env)
```
DATABASE_URL=sqlite:///./instagram_clone.db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Próximos Passos

- [ ] Stories
- [ ] Direct Messages
- [ ] Notificações
- [ ] Busca de usuários
- [ ] Hashtags
- [ ] Múltiplas imagens por post
- [ ] Vídeos
- [ ] Deploy em produção

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.