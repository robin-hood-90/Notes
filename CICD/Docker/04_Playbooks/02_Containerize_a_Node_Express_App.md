---
tags: [docker, cicd, playbook, node, express, backend, containerization]
aliases: ["Containerize Node Express", "Node.js Docker", "Express Production Dockerfile"]
status: stable
updated: 2026-05-03
---

# Playbook: Containerize a Node.js/Express App

> [!summary] Goal
> Build a production-ready Docker image for a Node.js/Express API with multi-stage builds, health checks, non-root user, and Compose setup with PostgreSQL and Redis.

## Dockerfiles

### Development Dockerfile

```dockerfile
FROM node:20-alpine
WORKDIR /app
RUN apk add --no-cache curl
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### Production Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
RUN apk add --no-cache curl
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-alpine AS run
WORKDIR /app

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs

# Copy production dependencies and build output
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./

USER nodejs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', r => process.exit(r.statusCode !== 200))" || exit 1

CMD ["node", "dist/main.js"]
```

## Docker Compose

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://app:secret@db:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready -U app
      interval: 5s

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

## `.dockerignore`

```dockerfile
node_modules
.git
.gitignore
.env
.env.*
*.md
coverage
dist
.DS_Store
npm-debug.log*
```

## Best Practices for Node.js

- Always use `npm ci` not `npm install` (respects lockfile exactly)
- Run production stage without devDependencies: `npm ci --only=production`
- Use Alpine base (`node:20-alpine` = ~7MB base)
- Set `NODE_ENV=production` for optimized dependency behavior
- Enable `trust-proxy` in Express for correct IP behind reverse proxy
- Use `--cap-drop=ALL` in runtime for defense in depth
