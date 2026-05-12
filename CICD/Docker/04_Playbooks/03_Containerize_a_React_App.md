---
tags: [docker, cicd, playbook, react, frontend, nginx, containerization]
aliases: ["Containerize React App", "React Docker", "React Nginx Multi-Stage"]
status: stable
updated: 2026-05-03
---

# Playbook: Containerize a React App

> [!summary] Goal
> Serve a production React build from a minimal Nginx container with multi-stage builds, SPA routing support, and runtime environment variable injection.

## Full Dockerfile

```dockerfile
# === BUILD STAGE ===
FROM node:20-alpine AS builder
WORKDIR /app

# Dependency installation (cached until lockfile changes)
COPY package*.json ./
RUN npm ci

# Source code and build
COPY . .
RUN npm run build

# === RUNTIME STAGE ===
FROM nginx:alpine AS run

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Custom Nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Script for runtime env var injection (runs before Nginx starts)
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
# nginx.conf
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/css application/javascript image/svg+xml;
    gzip_min_length 256;

    # SPA fallback — serve index.html for all non-file routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets with caching
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests (optional)
    location /api/ {
        proxy_pass http://api:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

## Runtime Environment Variable Injection

```bash
#!/bin/sh
# entrypoint.sh — runs before Nginx starts
# Creates env.js with runtime environment variables

echo "window.__ENV__ = {" > /usr/share/nginx/html/env.js

# Add each REACT_APP_ variable
for var in $(env | grep -E "^REACT_APP_" | sort); do
    key=$(echo "$var" | cut -d= -f1)
    value=$(echo "$var" | cut -d= -f2-)
    echo "  \"$key\": \"$value\"," >> /usr/share/nginx/html/env.js
done

echo "};" >> /usr/share/nginx/html/env.js
```

```html
<!-- index.html — loads env.js before the app -->
<script src="/env.js"></script>
<script src="/static/js/main.abc123.js"></script>
```

```ts
// src/env.ts — access runtime env vars
declare global {
  interface Window { __ENV__: Record<string, string>; }
}
export const env = (key: string, fallback?: string): string =>
  window.__ENV__?.[key] ?? fallback ?? '';
```

## Docker Compose (Full Stack)

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "8080:8080"
    environment:
      - REACT_APP_API_URL=http://localhost:3000
    depends_on:
      - api

  api:
    build: ./api
    ports:
      - "3000:3000"

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## `.dockerignore`

```
node_modules
.git
.gitignore
.env
.env.*
*.md
coverage
public/mockServiceWorker.js
.DS_Store
```

## Best Practices for React

- Multi-stage: build in `node:alpine`, serve from `nginx:alpine` — final image ~25MB
- SPA fallback: `try_files $uri $uri/ /index.html` — prevents 404 on direct URL access
- Runtime env injection: use entrypoint script, NOT build-time `REACT_APP_*` — same image for all environments
- Cache static assets: set `Cache-Control: public, immutable` for `build/static/`
- Use Nginx `alpine` image: ~5MB base vs ~150MB for full Ubuntu Nginx
