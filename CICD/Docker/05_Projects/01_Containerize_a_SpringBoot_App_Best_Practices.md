---
tags: [docker, cicd, projects, spring-boot, java, multi-stage, jvm, container, best-practices]
aliases: ["Containerize Spring Boot Project", "Spring Boot Dockerfile", "Java Container Best Practices"]
status: stable
updated: 2026-05-11
---

# Project: Containerize a Spring Boot App (Best Practices)

> [!summary] Goal
> Build a small, secure Spring Boot container image with multi-stage build, non-root user, JVM flags tuned for containers, proper health endpoints, and predictable startup behavior.

## Multi-Stage Dockerfile

```dockerfile
# ---- Build stage ----
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build
COPY . .
RUN ./mvnw -B -DskipTests clean package

# ---- Run stage ----
FROM eclipse-temurin:21-jre-alpine AS runtime

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy only the JAR (not the whole build stage)
COPY --from=builder /build/target/*.jar app.jar

USER appuser

EXPOSE 8080

# JVM flags tuned for containers
ENV JAVA_OPTS="-XX:+UseContainerSupport \
  -XX:MaxRAMPercentage=75.0 \
  -XX:+ExitOnOutOfMemoryError \
  -Djava.security.egd=file:/dev/./urandom"

HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### Key decisions

```text
Multi-stage build:
  - Separates build from runtime (JDK → JRE, no Maven/tools in final image).
  - Final image has only JRE + JAR → smaller, less surface area.

Non-root user:
  - addgroup + adduser in Alpine, USER appuser.
  - Prevents container from running as root (security best practice).

JVM flags (-XX):
  -XX:+UseContainerSupport      # JVM detects container memory limits (JDK 10+)
  -XX:MaxRAMPercentage=75.0     # Heap = 75% of container memory limit (not host)
  -XX:+ExitOnOutOfMemoryError   # Exit on OOM (K8s will restart)
  -Djava.security.egd=file:/dev/./urandom  # Faster startup (avoid blocking on /dev/random)

Health check:
  - Spring Boot Actuator /actuator/health endpoint.
  - K8s liveness + readiness probes point to the same endpoint.
  - Docker HEALTHCHECK also available.
```

---

## Cross-Links

- [[CICD/Docker/01_Foundations/02_Dockerfile_Essentials]] for Dockerfile instructions
- [[CICD/Docker/01_Foundations/04_Docker_Build_Secrets_Caching_and_Dangerous_Patterns]] for build secrets
- [[SpringBoot/01_Foundations/01_Boot_Project_Structure_and_Profiles]] for Spring Boot project structure
- [[SpringBoot/03_Advanced/05_Spring_Boot_Containerization_and_K8s]] for deeper K8s integration
