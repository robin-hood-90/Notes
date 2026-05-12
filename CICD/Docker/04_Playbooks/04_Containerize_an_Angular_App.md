---
tags: [docker, cicd, playbook, angular, frontend, nginx, containerization, universal, ssr]
aliases: ["Containerize Angular App", "Angular Docker", "Angular Nginx Multi-Stage", "Angular SSR"]
status: stable
updated: 2026-05-03
---

# Playbook: Containerize an Angular App

> [!summary] Goal
> Serve a production Angular build from Nginx with SPA routing, runtime environment injection, and optional SSR (Angular Universal).

## Full Dockerfile (Client-Side Rendering)

```dockerfile
# === BUILD STAGE ===
FROM node:20-alpine AS builder
WORKDIR /app

# Dependencies (cached until lockfile changes)
COPY package*.json angular.json tsconfig*.json ./
RUN npm ci

# Source code
COPY . .

# Production build
RUN npm run build -- --configuration production

# === RUNTIME STAGE ===
FROM nginx:alpine AS run

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Nginx config for Angular SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist/<project-name> /usr/share/nginx/html

# Runtime env injection
COPY entrypoint.sh /docker-entrypoint.d/40-env.sh
RUN chmod +x /docker-entrypoint.d/40-env.sh

USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

## Nginx Configuration

```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Built assets with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API proxy
    location /api/ {
        proxy_pass http://api:3000;
    }

    # Security
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

## Runtime Environment Injection

```bash
#!/bin/sh
# entrypoint.sh — creates env.js with runtime variables

cat > /usr/share/nginx/html/env.js << EOF
window.__ENV__ = {
  API_URL: "${API_URL:-http://localhost:3000}",
  APP_TITLE: "${APP_TITLE:-My Angular App}",
  SENTRY_DSN: "${SENTRY_DSN:-}"
};
EOF
```

```typescript
// src/environments/env.ts
export function getEnv(key: string, fallback = ''): string {
  return (window as any).__ENV__?.[key] ?? fallback;
}
```

## Dockerfile with Angular Universal (SSR)

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production
RUN npm run build:ssr  # Builds server bundle

# Runtime — SSR requires Node, not Nginx
FROM node:20-alpine AS run
WORKDIR /app

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Copy SSR server and browser assets
COPY --from=builder /app/dist/<project-name>/browser ./dist/browser
COPY --from=builder /app/dist/<project-name>/server ./dist/server
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER appuser
EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:4000/ || exit 1
CMD ["node", "dist/server/main.js"]
```

## Docker Compose

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "8080:8080"
    environment:
      - API_URL=http://localhost:3000
      - APP_TITLE=My Angular App

  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://app:secret@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready

volumes:
  pgdata:
```

## `.dockerignore`

```
node_modules
.git
.gitignore
.env
*.md
coverage
dist
e2e
.DS_Store
```

## Best Practices for Angular

- Client-side: multi-stage build + Nginx alpine = ~25MB final image
- SSR: Node runtime instead of Nginx — use `node:20-alpine` (no Nginx needed)
- Prod build flags: `--configuration production` enables AOT, tree-shaking, minification
- Base href: use `--base-href /app/` if served from a subpath
- Nginx for CSR: better static file serving than Node + `express.static()`
- Runtime env injection: entrypoint script approach — same image for dev/staging/prod
- SSR caching: consider using Nginx reverse proxy in front of SSR server for static page caching
