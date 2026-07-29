# --- CertifPass — image de production ---
FROM node:20-alpine

WORKDIR /app

# Installe uniquement les dépendances de production, en tirant parti du cache
# Docker (cette étape n'est refaite que si package*.json change).
COPY package.json package-lock.json* ./
RUN npm install --omit=dev

# Copie le reste de l'application (server.js, public/index.html, etc.)
COPY . .

# Exécute l'application avec un utilisateur non-root (fourni par l'image node:alpine)
USER node

ENV PORT=3000
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://localhost:'+(process.env.PORT||3000)+'/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "server.js"]
