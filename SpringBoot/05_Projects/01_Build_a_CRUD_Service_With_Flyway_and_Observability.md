---
tags: [spring-boot, projects, crud, flyway, observability]
aliases: ["Spring Boot CRUD Project", "Production CRUD Service"]
status: stable
updated: 2026-04-27
---

# Project: CRUD Service With Flyway and Observability

> [!tip] Quick Reference
> See [[SpringBoot/00_Cheat_Sheets]] for a condensed lookup while building.

> [!summary] Goal
> Build a production-ready REST service with database migrations, validation, comprehensive observability (logs, metrics, traces), and proper error handling. Complete hands-on implementation from scratch.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Part 1: Project Setup](#part-1-project-setup)
3. [Part 2: Database Layer](#part-2-database-layer)
4. [Part 3: Service Layer](#part-3-service-layer)
5. [Part 4: REST API Layer](#part-4-rest-api-layer)
6. [Part 5: Observability](#part-5-observability)
7. [Part 6: Testing](#part-6-testing)
8. [Part 7: Docker Deployment](#part-7-docker-deployment)
9. [Verification Steps](#verification-steps)
10. [Next Steps](#next-steps)

---

## Project Overview

**What we're building:**
A User and Posts management service with:
- REST API for CRUD operations
- PostgreSQL database with Flyway migrations
- Optimistic locking for concurrency control
- Comprehensive validation
- Structured logging with correlation IDs
- Prometheus metrics
- Health/readiness endpoints
- Docker deployment

**Technology stack:**
- Spring Boot 3.2+
- Spring Data JPA
- PostgreSQL 15
- Flyway
- Micrometer (metrics)
- Logback (logging)
- TestContainers (testing)
- Docker

**Architecture:**
```mermaid
graph TB
    Client[HTTP Client]
    Controller[UserController<br/>PostController]
    Service[UserService<br/>PostService]
    Repository[UserRepository<br/>PostRepository]
    DB[(PostgreSQL)]
    Actuator[Actuator Endpoints]
    Prometheus[Prometheus]
    
    Client -->|REST API| Controller
    Controller -->|Validation| Service
    Service -->|@Transactional| Repository
    Repository -->|JPA| DB
    Actuator -->|Metrics| Prometheus
    Controller -->|Metrics| Actuator
    Service -->|Metrics| Actuator
```

---

## Part 1: Project Setup

### Step 1: Initialize Project

**Using Spring Initializr** (https://start.spring.io):
- **Project**: Maven
- **Language**: Java 17+
- **Spring Boot**: 3.2.x
- **Group**: com.example
- **Artifact**: crud-service
- **Packaging**: Jar
- **Dependencies**:
  - Spring Web
  - Spring Data JPA
  - PostgreSQL Driver
  - Flyway Migration
  - Validation
  - Spring Boot Actuator
  - Lombok

**Or use this Maven `pom.xml`:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
        <relativePath/>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>crud-service</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>crud-service</name>
    <description>Production CRUD service with observability</description>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        
        <!-- Database -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        
        <!-- Micrometer for Prometheus -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        
        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        
        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>testcontainers</artifactId>
            <version>1.19.7</version>
            <scope>test</scope>
        </dependency>
        
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <version>1.19.7</version>
            <scope>test</scope>
        </dependency>
        
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>1.19.7</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### Step 2: Project Structure

```
crud-service/
├── src/
│   ├── main/
│   │   ├── java/com/example/crudservice/
│   │   │   ├── CrudServiceApplication.java
│   │   │   ├── config/
│   │   │   │   ├── LoggingConfig.java
│   │   │   │   └── MetricsConfig.java
│   │   │   ├── controller/
│   │   │   │   ├── UserController.java
│   │   │   │   └── PostController.java
│   │   │   ├── dto/
│   │   │   │   ├── CreateUserRequest.java
│   │   │   │   ├── UpdateUserRequest.java
│   │   │   │   ├── UserResponse.java
│   │   │   │   ├── CreatePostRequest.java
│   │   │   │   └── PostResponse.java
│   │   │   ├── entity/
│   │   │   │   ├── User.java
│   │   │   │   └── Post.java
│   │   │   ├── exception/
│   │   │   │   ├── GlobalExceptionHandler.java
│   │   │   │   ├── ResourceNotFoundException.java
│   │   │   │   └── ErrorResponse.java
│   │   │   ├── repository/
│   │   │   │   ├── UserRepository.java
│   │   │   │   └── PostRepository.java
│   │   │   ├── service/
│   │   │   │   ├── UserService.java
│   │   │   │   └── PostService.java
│   │   │   └── filter/
│   │   │       └── CorrelationIdFilter.java
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── logback-spring.xml
│   │       └── db/migration/
│   │           ├── V1__Create_users_table.sql
│   │           ├── V2__Create_posts_table.sql
│   │           ├── V3__Add_user_posts_relationship.sql
│   │           ├── V4__Add_indexes.sql
│   │           └── V5__Insert_sample_data.sql
│   └── test/
│       └── java/com/example/crudservice/
│           ├── UserServiceTest.java
│           ├── UserRepositoryTest.java
│           └── UserControllerIntegrationTest.java
├── Dockerfile
├── docker-compose.yml
└── pom.xml
```

### Step 3: Application Configuration

**`src/main/resources/application.yml`:**

```yaml
spring:
  application:
    name: crud-service
  
  # Database Configuration
  datasource:
    url: jdbc:postgresql://localhost:5432/cruddb
    username: postgres
    password: postgres
    driver-class-name: org.postgresql.Driver
    
    # HikariCP Connection Pool
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      leak-detection-threshold: 60000  # 60 seconds - detect connection leaks
  
  # JPA Configuration
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    hibernate:
      ddl-auto: validate  # Use Flyway for schema management
    show-sql: false  # Use logging configuration instead
    open-in-view: false  # Disable to prevent lazy loading issues
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true
  
  # Flyway Configuration
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    validate-on-migrate: true

# Actuator Configuration
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true  # For Kubernetes liveness/readiness
  metrics:
    tags:
      application: ${spring.application.name}
    export:
      prometheus:
        enabled: true
  
  # Health indicators
  health:
    defaults:
      enabled: true
    db:
      enabled: true

# Logging Configuration
logging:
  level:
    root: INFO
    com.example.crudservice: DEBUG
    org.springframework.web: INFO
    org.springframework.transaction: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{correlationId}] [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{correlationId}] [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/crud-service.log
    max-size: 10MB
    max-history: 30

# Server Configuration
server:
  port: 8080
  error:
    include-message: always
    include-binding-errors: always
    include-stacktrace: on_param  # Include stacktrace if 'trace' param present
    include-exception: false
  compression:
    enabled: true
```

### Step 4: Main Application Class

**`src/main/java/com/example/crudservice/CrudServiceApplication.java`:**

```java
package com.example.crudservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing  // Enable automatic createdAt/updatedAt timestamps
public class CrudServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CrudServiceApplication.class, args);
    }
}
```

---

## Part 2: Database Layer

### Flyway Migrations

**`src/main/resources/db/migration/V1__Create_users_table.sql`:**

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    version BIGINT NOT NULL DEFAULT 0,  -- For optimistic locking
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Add comment
COMMENT ON TABLE users IS 'User accounts';
COMMENT ON COLUMN users.version IS 'Optimistic lock version';
```

**`src/main/resources/db/migration/V2__Create_posts_table.sql`:**

```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT false,
    user_id BIGINT NOT NULL,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_posts_user FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE
);

-- Add comment
COMMENT ON TABLE posts IS 'Blog posts';
COMMENT ON COLUMN posts.user_id IS 'Author of the post';
```

**`src/main/resources/db/migration/V3__Add_user_posts_relationship.sql`:**

```sql
-- Already created via FK in V2, this migration adds any additional constraints

-- Ensure user_id is not null
ALTER TABLE posts 
    ALTER COLUMN user_id SET NOT NULL;

-- Add check constraint
ALTER TABLE posts
    ADD CONSTRAINT check_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);

ALTER TABLE posts
    ADD CONSTRAINT check_content_not_empty CHECK (LENGTH(TRIM(content)) > 0);
```

**`src/main/resources/db/migration/V4__Add_indexes.sql`:**

```sql
-- Index on email for fast user lookup
CREATE INDEX idx_users_email ON users(email);

-- Index on active users
CREATE INDEX idx_users_active ON users(active) WHERE active = true;

-- Index on user_id for post queries
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Index on published posts
CREATE INDEX idx_posts_published ON posts(published) WHERE published = true;

-- Composite index for user's published posts
CREATE INDEX idx_posts_user_published ON posts(user_id, published);

-- Index on created_at for sorting
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

**`src/main/resources/db/migration/V5__Insert_sample_data.sql`:**

```sql
-- Insert sample users
INSERT INTO users (email, first_name, last_name, active) VALUES
    ('john.doe@example.com', 'John', 'Doe', true),
    ('jane.smith@example.com', 'Jane', 'Smith', true),
    ('bob.wilson@example.com', 'Bob', 'Wilson', false);

-- Insert sample posts
INSERT INTO posts (title, content, published, user_id) VALUES
    ('Getting Started with Spring Boot', 
     'Spring Boot makes it easy to create stand-alone, production-grade Spring based Applications.', 
     true, 1),
    ('Database Migrations with Flyway', 
     'Flyway is an open-source database migration tool that enables version control for your database.', 
     true, 1),
    ('Draft Post', 
     'This is a draft post that is not yet published.', 
     false, 2);
```

### Entity Classes

**`src/main/java/com/example/crudservice/entity/User.java`:**

```java
package com.example.crudservice.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(name = "first_name", nullable = false, length = 100)
    private String firstName;

    @Column(name = "last_name", nullable = false, length = 100)
    private String lastName;

    @Column(nullable = false)
    @Builder.Default
    private Boolean active = true;

    @Version  // Enables optimistic locking
    private Long version;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Post> posts = new ArrayList<>();

    // Helper methods for bidirectional relationship
    public void addPost(Post post) {
        posts.add(post);
        post.setUser(this);
    }

    public void removePost(Post post) {
        posts.remove(post);
        post.setUser(null);
    }
}
```

**`src/main/java/com/example/crudservice/entity/Post.java`:**

```java
package com.example.crudservice.entity;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "posts")
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false)
    @Builder.Default
    private Boolean published = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Version
    private Long version;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
```

### Repository Interfaces

**`src/main/java/com/example/crudservice/repository/UserRepository.java`:**

```java
package com.example.crudservice.repository;

import com.example.crudservice.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Find user by email
     */
    Optional<User> findByEmail(String email);

    /**
     * Find all active users
     */
    List<User> findByActiveTrue();

    /**
     * Find user with posts eagerly loaded (prevents LazyInitializationException)
     */
    @Query("SELECT u FROM User u LEFT JOIN FETCH u.posts WHERE u.id = :id")
    Optional<User> findByIdWithPosts(@Param("id") Long id);

    /**
     * Check if email exists (for validation)
     */
    boolean existsByEmail(String email);
}
```

**`src/main/java/com/example/crudservice/repository/PostRepository.java`:**

```java
package com.example.crudservice.repository;

import com.example.crudservice.entity.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {

    /**
     * Find all posts by user ID
     */
    @Query("SELECT p FROM Post p WHERE p.user.id = :userId ORDER BY p.createdAt DESC")
    List<Post> findByUserId(@Param("userId") Long userId);

    /**
     * Find published posts by user ID
     */
    @Query("SELECT p FROM Post p WHERE p.user.id = :userId AND p.published = true ORDER BY p.createdAt DESC")
    List<Post> findPublishedPostsByUserId(@Param("userId") Long userId);

    /**
     * Find all published posts
     */
    List<Post> findByPublishedTrueOrderByCreatedAtDesc();
}
```

---

## Part 3: Service Layer

**`src/main/java/com/example/crudservice/service/UserService.java`:**

```java
package com.example.crudservice.service;

import com.example.crudservice.dto.CreateUserRequest;
import com.example.crudservice.dto.UpdateUserRequest;
import com.example.crudservice.dto.UserResponse;
import com.example.crudservice.dto.PostResponse;
import com.example.crudservice.entity.User;
import com.example.crudservice.exception.ResourceNotFoundException;
import com.example.crudservice.repository.UserRepository;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final MeterRegistry meterRegistry;

    /**
     * Create a new user
     */
    @Transactional
    public UserResponse createUser(CreateUserRequest request) {
        log.info("Creating user with email: {}", request.getEmail());

        // Validate email uniqueness
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already exists: " + request.getEmail());
        }

        // Build and save user
        User user = User.builder()
                .email(request.getEmail())
                .firstName(request.getFirstName())
                .lastName(request.getLastName())
                .active(true)
                .build();

        User saved = userRepository.save(user);
        log.info("User created successfully with ID: {}", saved.getId());

        // Increment counter metric
        Counter.builder("users.created")
                .description("Number of users created")
                .tag("status", "success")
                .register(meterRegistry)
                .increment();

        return toResponse(saved);
    }

    /**
     * Get user by ID
     */
    @Transactional(readOnly = true)
    public UserResponse getUserById(Long id) {
        log.debug("Fetching user by ID: {}", id);

        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));

        return toResponse(user);
    }

    /**
     * Get all users
     */
    @Transactional(readOnly = true)
    public List<UserResponse> getAllUsers() {
        log.debug("Fetching all users");

        return userRepository.findAll().stream()
                .map(this::toResponse)
                .collect(Collectors.toList());
    }

    /**
     * Update user (with optimistic locking)
     */
    @Transactional
    public UserResponse updateUser(Long id, UpdateUserRequest request) {
        log.info("Updating user with ID: {}", id);

        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));

        // Update fields
        if (request.getFirstName() != null) {
            user.setFirstName(request.getFirstName());
        }
        if (request.getLastName() != null) {
            user.setLastName(request.getLastName());
        }
        if (request.getActive() != null) {
            user.setActive(request.getActive());
        }

        // Save will automatically check version for optimistic locking
        User updated = userRepository.save(user);
        log.info("User updated successfully: {}", updated.getId());

        return toResponse(updated);
    }

    /**
     * Delete user (cascades to posts)
     */
    @Transactional
    public void deleteUser(Long id) {
        log.info("Deleting user with ID: {}", id);

        if (!userRepository.existsById(id)) {
            throw new ResourceNotFoundException("User not found with ID: " + id);
        }

        userRepository.deleteById(id);
        log.info("User deleted successfully: {}", id);

        // Increment counter
        Counter.builder("users.deleted")
                .description("Number of users deleted")
                .register(meterRegistry)
                .increment();
    }

    /**
     * Get user's posts
     */
    @Transactional(readOnly = true)
    public List<PostResponse> getUserPosts(Long userId) {
        log.debug("Fetching posts for user ID: {}", userId);

        // Use fetch join to avoid LazyInitializationException
        User user = userRepository.findByIdWithPosts(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));

        return user.getPosts().stream()
                .map(post -> PostResponse.builder()
                        .id(post.getId())
                        .title(post.getTitle())
                        .content(post.getContent())
                        .published(post.getPublished())
                        .userId(user.getId())
                        .createdAt(post.getCreatedAt())
                        .updatedAt(post.getUpdatedAt())
                        .build())
                .collect(Collectors.toList());
    }

    /**
     * Convert entity to response DTO
     */
    private UserResponse toResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .firstName(user.getFirstName())
                .lastName(user.getLastName())
                .active(user.getActive())
                .version(user.getVersion())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}
```

**`src/main/java/com/example/crudservice/service/PostService.java`:**

```java
package com.example.crudservice.service;

import com.example.crudservice.dto.CreatePostRequest;
import com.example.crudservice.dto.PostResponse;
import com.example.crudservice.entity.Post;
import com.example.crudservice.entity.User;
import com.example.crudservice.exception.ResourceNotFoundException;
import com.example.crudservice.repository.PostRepository;
import com.example.crudservice.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PostService {

    private final PostRepository postRepository;
    private final UserRepository userRepository;

    /**
     * Create a new post
     */
    @Transactional
    public PostResponse createPost(CreatePostRequest request) {
        log.info("Creating post for user ID: {}", request.getUserId());

        // Validate user exists
        User user = userRepository.findById(request.getUserId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + request.getUserId()));

        // Business rule: inactive users cannot create posts
        if (!user.getActive()) {
            throw new IllegalStateException("Inactive users cannot create posts");
        }

        // Build and save post
        Post post = Post.builder()
                .title(request.getTitle())
                .content(request.getContent())
                .published(request.getPublished() != null ? request.getPublished() : false)
                .user(user)
                .build();

        Post saved = postRepository.save(post);
        log.info("Post created successfully with ID: {}", saved.getId());

        return toResponse(saved);
    }

    /**
     * Get all published posts
     */
    @Transactional(readOnly = true)
    public List<PostResponse> getPublishedPosts() {
        log.debug("Fetching all published posts");

        return postRepository.findByPublishedTrueOrderByCreatedAtDesc().stream()
                .map(this::toResponse)
                .collect(Collectors.toList());
    }

    /**
     * Convert entity to response DTO
     */
    private PostResponse toResponse(Post post) {
        return PostResponse.builder()
                .id(post.getId())
                .title(post.getTitle())
                .content(post.getContent())
                .published(post.getPublished())
                .userId(post.getUser().getId())
                .createdAt(post.getCreatedAt())
                .updatedAt(post.getUpdatedAt())
                .build();
    }
}
```

---

## Part 4: REST API Layer

### DTOs (Data Transfer Objects)

**`src/main/java/com/example/crudservice/dto/CreateUserRequest.java`:**

```java
package com.example.crudservice.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateUserRequest {

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    private String email;

    @NotBlank(message = "First name is required")
    @Size(min = 1, max = 100, message = "First name must be between 1 and 100 characters")
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Size(min = 1, max = 100, message = "Last name must be between 1 and 100 characters")
    private String lastName;
}
```

**`src/main/java/com/example/crudservice/dto/UpdateUserRequest.java`:**

```java
package com.example.crudservice.dto;

import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UpdateUserRequest {

    @Size(min = 1, max = 100, message = "First name must be between 1 and 100 characters")
    private String firstName;

    @Size(min = 1, max = 100, message = "Last name must be between 1 and 100 characters")
    private String lastName;

    private Boolean active;
}
```

**`src/main/java/com/example/crudservice/dto/UserResponse.java`:**

```java
package com.example.crudservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserResponse {
    private Long id;
    private String email;
    private String firstName;
    private String lastName;
    private Boolean active;
    private Long version;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

**`src/main/java/com/example/crudservice/dto/CreatePostRequest.java`:**

```java
package com.example.crudservice.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreatePostRequest {

    @NotBlank(message = "Title is required")
    @Size(max = 255, message = "Title must not exceed 255 characters")
    private String title;

    @NotBlank(message = "Content is required")
    private String content;

    private Boolean published;

    @NotNull(message = "User ID is required")
    private Long userId;
}
```

**`src/main/java/com/example/crudservice/dto/PostResponse.java`:**

```java
package com.example.crudservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PostResponse {
    private Long id;
    private String title;
    private String content;
    private Boolean published;
    private Long userId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

### Controllers

**`src/main/java/com/example/crudservice/controller/UserController.java`:**

```java
package com.example.crudservice.controller;

import com.example.crudservice.dto.CreateUserRequest;
import com.example.crudservice.dto.PostResponse;
import com.example.crudservice.dto.UpdateUserRequest;
import com.example.crudservice.dto.UserResponse;
import com.example.crudservice.service.UserService;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.MeterRegistry;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserService userService;
    private final MeterRegistry meterRegistry;

    /**
     * Create a new user
     * POST /api/users
     */
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        log.info("POST /api/users - Creating user with email: {}", request.getEmail());

        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            UserResponse response = userService.createUser(request);
            sample.stop(Timer.builder("http.server.requests")
                    .tag("uri", "/api/users")
                    .tag("method", "POST")
                    .tag("status", "201")
                    .register(meterRegistry));
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            sample.stop(Timer.builder("http.server.requests")
                    .tag("uri", "/api/users")
                    .tag("method", "POST")
                    .tag("status", "500")
                    .register(meterRegistry));
            throw e;
        }
    }

    /**
     * Get user by ID
     * GET /api/users/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long id) {
        log.info("GET /api/users/{} - Fetching user", id);

        UserResponse response = userService.getUserById(id);
        return ResponseEntity.ok(response);
    }

    /**
     * Get all users
     * GET /api/users
     */
    @GetMapping
    public ResponseEntity<List<UserResponse>> getAllUsers() {
        log.info("GET /api/users - Fetching all users");

        List<UserResponse> response = userService.getAllUsers();
        return ResponseEntity.ok(response);
    }

    /**
     * Update user
     * PUT /api/users/{id}
     */
    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        log.info("PUT /api/users/{} - Updating user", id);

        UserResponse response = userService.updateUser(id, request);
        return ResponseEntity.ok(response);
    }

    /**
     * Delete user
     * DELETE /api/users/{id}
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        log.info("DELETE /api/users/{} - Deleting user", id);

        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Get user's posts
     * GET /api/users/{id}/posts
     */
    @GetMapping("/{id}/posts")
    public ResponseEntity<List<PostResponse>> getUserPosts(@PathVariable Long id) {
        log.info("GET /api/users/{}/posts - Fetching user's posts", id);

        List<PostResponse> response = userService.getUserPosts(id);
        return ResponseEntity.ok(response);
    }
}
```

**`src/main/java/com/example/crudservice/controller/PostController.java`:**

```java
package com.example.crudservice.controller;

import com.example.crudservice.dto.CreatePostRequest;
import com.example.crudservice.dto.PostResponse;
import com.example.crudservice.service.PostService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
@Slf4j
public class PostController {

    private final PostService postService;

    /**
     * Create a new post
     * POST /api/posts
     */
    @PostMapping
    public ResponseEntity<PostResponse> createPost(@Valid @RequestBody CreatePostRequest request) {
        log.info("POST /api/posts - Creating post for user {}", request.getUserId());

        PostResponse response = postService.createPost(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Get all published posts
     * GET /api/posts
     */
    @GetMapping
    public ResponseEntity<List<PostResponse>> getPublishedPosts() {
        log.info("GET /api/posts - Fetching published posts");

        List<PostResponse> response = postService.getPublishedPosts();
        return ResponseEntity.ok(response);
    }
}
```

### Exception Handling

**`src/main/java/com/example/crudservice/exception/ResourceNotFoundException.java`:**

```java
package com.example.crudservice.exception;

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
```

**`src/main/java/com/example/crudservice/exception/ErrorResponse.java`:**

```java
package com.example.crudservice.exception;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {
    private LocalDateTime timestamp;
    private int status;
    private String error;
    private String message;
    private String path;
    private List<ValidationError> validationErrors;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ValidationError {
        private String field;
        private String message;
    }
}
```

**`src/main/java/com/example/crudservice/exception/GlobalExceptionHandler.java`:**

```java
package com.example.crudservice.exception;

import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    /**
     * Handle resource not found
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(
            ResourceNotFoundException ex,
            HttpServletRequest request) {

        log.error("Resource not found: {}", ex.getMessage());

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.NOT_FOUND.value())
                .error(HttpStatus.NOT_FOUND.getReasonPhrase())
                .message(ex.getMessage())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    /**
     * Handle validation errors
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(
            MethodArgumentNotValidException ex,
            HttpServletRequest request) {

        log.error("Validation error: {}", ex.getMessage());

        List<ErrorResponse.ValidationError> validationErrors = ex.getBindingResult()
                .getAllErrors()
                .stream()
                .map(error -> ErrorResponse.ValidationError.builder()
                        .field(((FieldError) error).getField())
                        .message(error.getDefaultMessage())
                        .build())
                .collect(Collectors.toList());

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error(HttpStatus.BAD_REQUEST.getReasonPhrase())
                .message("Validation failed")
                .path(request.getRequestURI())
                .validationErrors(validationErrors)
                .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    /**
     * Handle illegal argument exceptions
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(
            IllegalArgumentException ex,
            HttpServletRequest request) {

        log.error("Illegal argument: {}", ex.getMessage());

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error(HttpStatus.BAD_REQUEST.getReasonPhrase())
                .message(ex.getMessage())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    /**
     * Handle illegal state exceptions
     */
    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<ErrorResponse> handleIllegalState(
            IllegalStateException ex,
            HttpServletRequest request) {

        log.error("Illegal state: {}", ex.getMessage());

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.CONFLICT.value())
                .error(HttpStatus.CONFLICT.getReasonPhrase())
                .message(ex.getMessage())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }

    /**
     * Handle all other exceptions
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex,
            HttpServletRequest request) {

        log.error("Unexpected error: ", ex);

        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .error(HttpStatus.INTERNAL_SERVER_ERROR.getReasonPhrase())
                .message("An unexpected error occurred")
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

---

## Part 5: Observability

### Correlation ID Filter

**`src/main/java/com/example/crudservice/filter/CorrelationIdFilter.java`:**

```java
package com.example.crudservice.filter;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.UUID;

@Component
public class CorrelationIdFilter implements Filter {

    private static final String CORRELATION_ID_HEADER = "X-Correlation-ID";
    private static final String CORRELATION_ID_MDC_KEY = "correlationId";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        try {
            // Get correlation ID from header or generate new one
            String correlationId = httpRequest.getHeader(CORRELATION_ID_HEADER);
            if (correlationId == null || correlationId.isEmpty()) {
                correlationId = UUID.randomUUID().toString();
            }

            // Add to MDC for logging
            MDC.put(CORRELATION_ID_MDC_KEY, correlationId);

            // Add to response header
            httpResponse.setHeader(CORRELATION_ID_HEADER, correlationId);

            chain.doFilter(request, response);
        } finally {
            // Clean up MDC
            MDC.remove(CORRELATION_ID_MDC_KEY);
        }
    }
}
```

### Logging Configuration

**`src/main/resources/logback-spring.xml`:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    
    <!-- Console appender -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{correlationId}] [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <!-- File appender -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/crud-service.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/crud-service.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>10MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{correlationId}] [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <!-- Root logger -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
    
    <!-- Application logger -->
    <logger name="com.example.crudservice" level="DEBUG"/>
    
    <!-- Spring framework -->
    <logger name="org.springframework.web" level="INFO"/>
    <logger name="org.springframework.transaction" level="DEBUG"/>
    
    <!-- Hibernate SQL -->
    <logger name="org.hibernate.SQL" level="DEBUG"/>
    <logger name="org.hibernate.type.descriptor.sql.BasicBinder" level="TRACE"/>
    
</configuration>
```

### Metrics Configuration

**`src/main/java/com/example/crudservice/config/MetricsConfig.java`:**

```java
package com.example.crudservice.config;

import io.micrometer.core.aop.TimedAspect;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MetricsConfig {

    /**
     * Enable @Timed annotation for method-level metrics
     */
    @Bean
    public TimedAspect timedAspect(MeterRegistry registry) {
        return new TimedAspect(registry);
    }
}
```

### Health Check Configuration

Spring Boot Actuator provides health checks out of the box. Access them at:
- **Health**: `http://localhost:8080/actuator/health`
- **Readiness**: `http://localhost:8080/actuator/health/readiness`
- **Liveness**: `http://localhost:8080/actuator/health/liveness`
- **Metrics**: `http://localhost:8080/actuator/metrics`
- **Prometheus**: `http://localhost:8080/actuator/prometheus`

---

## Part 6: Testing

### Unit Tests

**`src/test/java/com/example/crudservice/UserServiceTest.java`:**

```java
package com.example.crudservice;

import com.example.crudservice.dto.CreateUserRequest;
import com.example.crudservice.dto.UserResponse;
import com.example.crudservice.entity.User;
import com.example.crudservice.exception.ResourceNotFoundException;
import com.example.crudservice.repository.UserRepository;
import com.example.crudservice.service.UserService;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    private MeterRegistry meterRegistry;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
        meterRegistry = new SimpleMeterRegistry();
        userService = new UserService(userRepository, meterRegistry);
    }

    @Test
    void createUser_Success() {
        // Given
        CreateUserRequest request = CreateUserRequest.builder()
                .email("test@example.com")
                .firstName("John")
                .lastName("Doe")
                .build();

        User savedUser = User.builder()
                .id(1L)
                .email("test@example.com")
                .firstName("John")
                .lastName("Doe")
                .active(true)
                .version(0L)
                .build();

        when(userRepository.existsByEmail(anyString())).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        // When
        UserResponse response = userService.createUser(request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.getId()).isEqualTo(1L);
        assertThat(response.getEmail()).isEqualTo("test@example.com");
        verify(userRepository, times(1)).save(any(User.class));
    }

    @Test
    void createUser_EmailAlreadyExists_ThrowsException() {
        // Given
        CreateUserRequest request = CreateUserRequest.builder()
                .email("test@example.com")
                .firstName("John")
                .lastName("Doe")
                .build();

        when(userRepository.existsByEmail(anyString())).thenReturn(true);

        // When & Then
        assertThatThrownBy(() -> userService.createUser(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Email already exists");
    }

    @Test
    void getUserById_NotFound_ThrowsException() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.empty());

        // When & Then
        assertThatThrownBy(() -> userService.getUserById(1L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("User not found");
    }
}
```

### Repository Tests

**`src/test/java/com/example/crudservice/UserRepositoryTest.java`:**

```java
package com.example.crudservice;

import com.example.crudservice.entity.User;
import com.example.crudservice.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_Success() {
        // Given
        User user = User.builder()
                .email("test@example.com")
                .firstName("John")
                .lastName("Doe")
                .active(true)
                .build();
        entityManager.persist(user);
        entityManager.flush();

        // When
        Optional<User> found = userRepository.findByEmail("test@example.com");

        // Then
        assertThat(found).isPresent();
        assertThat(found.get().getEmail()).isEqualTo("test@example.com");
    }

    @Test
    void existsByEmail_ReturnsTrue() {
        // Given
        User user = User.builder()
                .email("test@example.com")
                .firstName("John")
                .lastName("Doe")
                .active(true)
                .build();
        entityManager.persist(user);
        entityManager.flush();

        // When
        boolean exists = userRepository.existsByEmail("test@example.com");

        // Then
        assertThat(exists).isTrue();
    }
}
```

### Integration Tests with TestContainers

**`src/test/java/com/example/crudservice/UserControllerIntegrationTest.java`:**

```java
package com.example.crudservice;

import com.example.crudservice.dto.CreateUserRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class UserControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void createUser_Success() throws Exception {
        CreateUserRequest request = CreateUserRequest.builder()
                .email("integration@example.com")
                .firstName("Integration")
                .lastName("Test")
                .build();

        mockMvc.perform(post("/api/users")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value("integration@example.com"))
                .andExpect(jsonPath("$.id").exists());
    }

    @Test
    void getUserById_NotFound() throws Exception {
        mockMvc.perform(get("/api/users/99999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.message").value("User not found with ID: 99999"));
    }
}
```

---

## Part 7: Docker Deployment

### Dockerfile

**`Dockerfile`:**

```dockerfile
# Multi-stage build

# Stage 1: Build
FROM maven:3.9-eclipse-temurin-17-alpine AS build
WORKDIR /app

# Copy pom.xml and download dependencies (cached layer)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code and build
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# Copy JAR from build stage
COPY --from=build /app/target/crud-service-*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Docker Compose

**`docker-compose.yml`:**

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: crud-postgres
    environment:
      POSTGRES_DB: cruddb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - crud-network

  # Spring Boot Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: crud-service
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/cruddb
      SPRING_DATASOURCE_USERNAME: postgres
      SPRING_DATASOURCE_PASSWORD: postgres
    ports:
      - "8080:8080"
    networks:
      - crud-network
    restart: unless-stopped

  # Prometheus (optional - for metrics)
  prometheus:
    image: prom/prometheus:latest
    container_name: crud-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - crud-network

networks:
  crud-network:
    driver: bridge

volumes:
  postgres_data:
  prometheus_data:
```

### Prometheus Configuration (Optional)

**`prometheus.yml`:**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'crud-service'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['app:8080']
```

### Running with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Verification Steps

### 1. Start Application

```bash
# Local development (requires PostgreSQL running)
mvn spring-boot:run

# Or with Docker
docker-compose up -d
```

### 2. Test Health Endpoints

```bash
# Health check
curl http://localhost:8080/actuator/health

# Response:
# {
#   "status": "UP",
#   "components": {
#     "db": {"status": "UP"},
#     "diskSpace": {"status": "UP"},
#     "ping": {"status": "UP"}
#   }
# }

# Prometheus metrics
curl http://localhost:8080/actuator/prometheus
```

### 3. Test CRUD Operations

```bash
# Create user
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "firstName": "Test",
    "lastName": "User"
  }'

# Get user (replace {id} with ID from create response)
curl http://localhost:8080/api/users/1

# Get all users
curl http://localhost:8080/api/users

# Update user
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Updated",
    "active": false
  }'

# Get user's posts
curl http://localhost:8080/api/users/1/posts

# Delete user
curl -X DELETE http://localhost:8080/api/users/1
```

### 4. Test Validation

```bash
# Invalid email
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "firstName": "Test",
    "lastName": "User"
  }'

# Response: 400 Bad Request with validation errors
```

### 5. Check Logs

```bash
# View application logs (look for correlation IDs)
tail -f logs/crud-service.log

# Sample log:
# 2026-04-26 10:15:30.123 [abc-123-def] [http-nio-8080-exec-1] INFO  c.e.c.controller.UserController - POST /api/users - Creating user with email: test@example.com
```

### 6. Test Metrics

```bash
# View specific metric
curl http://localhost:8080/actuator/metrics/users.created

# Response:
# {
#   "name": "users.created",
#   "measurements": [{"statistic": "COUNT", "value": 5.0}],
#   "availableTags": [{"tag": "status", "values": ["success"]}]
# }
```

---

## Next Steps

### Enhancements

1. **Add Pagination**:
   ```java
   @GetMapping
   public Page<UserResponse> getAllUsers(Pageable pageable) {
       return userService.getAllUsers(pageable);
   }
   ```

2. **Add Caching** (Redis):
   ```java
   @Cacheable(value = "users", key = "#id")
   public UserResponse getUserById(Long id) { ... }
   ```

3. **Add API Versioning**:
   ```java
   @RestController
   @RequestMapping("/api/v1/users")
   ```

4. **Add Search/Filtering**:
   ```java
   @GetMapping("/search")
   public List<UserResponse> searchUsers(
       @RequestParam String query) { ... }
   ```

5. **Add Rate Limiting** (Bucket4j)

6. **Add Authentication** (Spring Security + JWT)

7. **Add Distributed Tracing** (Zipkin/Jaeger)

### Testing Checklist

- [x] Unit tests for service layer
- [x] Repository tests with @DataJpaTest
- [x] Integration tests with TestContainers
- [ ] Load tests (JMeter/Gatling)
- [ ] Contract tests (Pact)
- [ ] End-to-end tests (Selenium)

---

## Cross-Links

- **Flyway migrations**: [[SpringBoot/02_Core/03_Flyway_Migrations]]
- **Spring Data JPA**: [[SpringBoot/02_Core/01_Spring_Data_JPA_Essentials]]
- **Transactions**: [[SpringBoot/02_Core/02_Transactions_and_Propagation]]
- **Observability**: [[SystemDesign/02_Core/05_Observability_Logs_Metrics_Traces]]
- **Validation**: [[SpringBoot/01_Foundations/04_Config_Properties_and_Validation]]
- **Production checklist**: [[SpringBoot/04_Playbooks/01_Production_Configuration_Checklist]]
