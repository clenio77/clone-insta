FROM node:16

WORKDIR /app

# Criar usuário não-root
RUN groupadd -r nodeuser && useradd -r -g nodeuser nodeuser

# Copiar package.json e instalar dependências
COPY package*.json ./
RUN npm install

# Copiar código fonte
COPY . .

# Ajustar permissões
RUN chown -R nodeuser:nodeuser /app
RUN chmod -R 755 /app

# Mudar para usuário não-root
USER nodeuser

EXPOSE 3000

CMD ["npm", "start"]
