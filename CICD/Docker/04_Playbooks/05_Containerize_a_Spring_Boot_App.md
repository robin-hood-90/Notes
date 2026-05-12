---
tags: [docker, cicd, playbook, spring-boot, java, maven, gradle, containerization]
aliases: ["Containerize Spring Boot", "Spring Boot Docker", "Java Docker", "Layered JAR"]
status: stable
updated: 2026-05-03
---

# Playbook: Containerize a Spring Boot App

> [!summary] Goal
> Build a small, secure, production-ready Spring Boot Docker image with layered JARs, JVM container-awareness, health endpoints, and multi-stage builds.

## Maven Multi-Stage Dockerfile

```dockerfile
# === BUILD STAGE ===
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app

# Download dependencies first (cached until pom changes)
COPY mvnw pom.xml ./
COPY .mvn .mvn
RUN --mount=type=cache,target=/root/.m2 \
    ./mvnw dependency:go-offline -DskipTests

# Build
COPY src src
RUN --mount=type=cache,target=/root/.m2 \
    ./mvnw package -DskipTests

# Extract layered JAR for optimal caching
RUN java -Djarmode=layertools -jar target/*.jar extract --destination /extract

# === RUNTIME STAGE ===
FROM eclipse-temurin:21-jre-alpine AS run
WORKDIR /app

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring

# Copy layers in dependency order — slowest-changing first
COPY --from=build /extract/dependencies/ ./
COPY --from=build /extract/spring-boot-loader/ ./
COPY --from=build /extract/snapshot-dependencies/ ./
COPY --from=build /extract/application/ ./

USER spring
EXPOSE 8080

# JVM container-aware flags
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError -Djava.security.egd=file:/dev/./urandom"

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

## Gradle Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM gradle:8-jdk21-alpine AS build
WORKDIR /app
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle gradle
RUN --mount=type=cache,target=/root/.gradle gradle dependencies --no-daemon
COPY src src
RUN --mount=type=cache,target=/root/.gradle gradle build -x test --no-daemon
RUN java -Djarmode=layertools -jar build/libs/*.jar extract --destination /extract

# Runtime stage (same as Maven)
FROM eclipse-temurin:21-jre-alpine AS run
WORKDIR /app
RUN addgroup -S spring && adduser -S spring -G spring
COPY --from=build /extract/dependencies/ ./
COPY --from=build /extract/spring-boot-loader/ ./
COPY --from=build /extract/snapshot-dependencies/ ./
COPY --from=build /extract/application/ ./
USER spring
EXPOSE 8080
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

## Distroless Runtime Alternative

```dockerfile
# Runtime — distroless (no shell, no package manager)
FROM gcr.io/distroless/java21-debian12 AS run
COPY --from=build /extract/dependencies/ ./
COPY --from=build /extract/spring-boot-loader/ ./
COPY --from=build /extract/snapshot-dependencies/ ./
COPY --from=build /extract/application/ ./
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
# ~12MB base instead of ~200MB JDK image
```

## Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DATABASE_URL=jdbc:postgresql://db:5432/appdb
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready
      interval: 5s

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

## `.dockerignore`

```
target
!.mvn
*.jar
.git
.gitignore
*.md
.DS_Store
```

## Application Properties

```properties
# src/main/resources/application-prod.properties
server.port=8080
management.endpoints.web.base-path=/actuator
management.endpoint.health.show-details=always

# Active profile set via SPRING_PROFILES_ACTIVE env var
```

## Best Practices for Spring Boot

- **Container-aware JVM**: `-XX:+UseContainerSupport` (default since Java 10) respects container cgroup limits
- **MaxRAMPercentage**: `-XX:MaxRAMPercentage=75.0` — leaves memory for the OS within the container limit
- **Layered JARs**: extract JAR into layers (`dependencies`, `spring-boot-loader`, `snapshot-dependencies`, `application`) — code changes only rebuild the last layer
- **Health endpoint**: use Spring Boot Actuator + `HEALTHCHECK` for orchestration-aware lifecycle
- **Exit on OOM**: `-XX:+ExitOnOutOfMemoryError` ensures the container restarts instead of hanging
- **Distroless**: `gcr.io/distroless/java21` reduces image by ~200MB and eliminates shell-based attacks
- **Gradle vs Maven**: both produce the same final image — choose whichever your project uses
- **Devtools**: exclude `spring-boot-devtools` from production builds (disabled by `spring.devtools.restart.enabled=false` in prod profile)

### Alternative: Native Image with GraalVM

Using GraalVM native-image eliminates the JVM entirely — your Spring Boot app becomes a static binary with zero Java dependencies:

```dockerfile
FROM ghcr.io/graalvm/native-image:22 AS build
WORKDIR /app
COPY . .
RUN ./mvnw -Pnative package -DskipTests -Dnative-image.docker-build=true

FROM gcr.io/distroless/base
COPY --from=build /app/target/my-app /app
EXPOSE 8080
CMD ["/app"]
```

| Metric | JRE image | Native image |
|--------|-----------|-------------|
| **Image size** | ~200MB | **~52MB** |
| **Startup time** | 3-5 seconds | **<0.1 seconds** |
| **Memory (RSS)** | ~200MB | **~50MB** |

**When to use**: Serverless, short-lived containers, high-density deployments, cold-start sensitive apps.
**When to avoid**: Need JMX/heap dumps, heavy JPA with complex lazy loading, runtime `@Profile` switching.

See [[SpringBoot/02_Core/04_Building_Native_Images_with_GraalVM]] for full setup guide.
