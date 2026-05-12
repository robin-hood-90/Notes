---
tags: [spring-boot, foundations, configuration, validation, properties]
aliases: ["Configuration Properties", "Spring Validation", "@ConfigurationProperties"]
status: stable
updated: 2026-04-26
---

# Config Properties and Validation

> [!tip] Quick Reference
> Start with [[SpringBoot/00_Cheat_Sheets]] when you need a fast lookup (config binding, validation, common properties).

## Overview

Type-safe configuration binding eliminates magic strings, provides IDE support, and enables validation at startup. `@ConfigurationProperties` is the recommended way to externalize configuration in Spring Boot.

> [!summary] Goal
> Master type-safe configuration binding with `@ConfigurationProperties`, validation strategies, property conversion, and best practices for managing application configuration.

---

## Why @ConfigurationProperties?

## Binding Flow (What Happens at Startup)

```mermaid
flowchart TD
    A[Property Sources\napplication.yml, env vars, CLI args] --> B[Environment\nProperty resolution + precedence]
    B --> C[Binder\nSpring Boot properties binder]
    C --> D[@ConfigurationProperties bean\ncreates + binds fields]
    D --> E{Conversion needed?}
    E -->|No| G[Bound object]
    E -->|Yes| F[ConversionService\nString -> int/Duration/DataSize/Enum]
    F --> G
    G --> H{Validation enabled?\n@Validated present}
    H -->|No| J[ApplicationContext refresh continues]
    H -->|Yes| I[JSR-380 Validator\n@NotBlank/@Min/... + @Valid nested]
    I --> K{Violations?}
    K -->|No| J
    K -->|Yes| L[Startup fails\nBindException / ValidationException]
```

**Key takeaways**:
- Binding happens during context refresh; invalid config should fail fast.
- Nested validation requires `@Valid` on nested properties.
- Type conversion is centralized (avoid custom parsing in your code).

### The Problem with @Value

```java
// ❌ BAD: Using @Value everywhere
@Service
public class EmailService {
    
    @Value("${email.smtp.host}")
    private String smtpHost;
    
    @Value("${email.smtp.port}")
    private int smtpPort;
    
    @Value("${email.from.address}")
    private String fromAddress;
    
    @Value("${email.from.name}")
    private String fromName;
    
    @Value("${email.retry.max-attempts:3}")
    private int maxRetries;
    
    @Value("${email.retry.delay-ms:1000}")
    private long retryDelay;
    
    // Scattered configuration, no validation, no IDE support
}
```

**Issues**:
- ❌ Magic strings (typos not caught at compile time)
- ❌ No type safety or validation
- ❌ Hard to test (need Spring context)
- ❌ No IDE autocomplete
- ❌ Scattered across classes

### The Solution: @ConfigurationProperties

```java
// ✅ GOOD: Type-safe configuration class
@ConfigurationProperties(prefix = "email")
@Validated
public class EmailProperties {
    
    private Smtp smtp = new Smtp();
    private From from = new From();
    private Retry retry = new Retry();
    
    public static class Smtp {
        @NotBlank
        private String host;
        
        @Min(1)
        @Max(65535)
        private int port = 587;
        
        private boolean tlsEnabled = true;
        
        // Getters and setters
    }
    
    public static class From {
        @NotBlank
        @Email
        private String address;
        
        @NotBlank
        private String name;
        
        // Getters and setters
    }
    
    public static class Retry {
        @Min(1)
        @Max(10)
        private int maxAttempts = 3;
        
        @Min(100)
        private long delayMs = 1000;
        
        // Getters and setters
    }
    
    // Getters and setters for nested classes
}
```

```yaml
# application.yml
email:
  smtp:
    host: smtp.gmail.com
    port: 587
    tls-enabled: true
  from:
    address: noreply@example.com
    name: Example App
  retry:
    max-attempts: 3
    delay-ms: 1000
```

**Benefits**:
- ✅ Type-safe (compile-time checks)
- ✅ Validated at startup
- ✅ IDE autocomplete in YAML/properties files
- ✅ Easy to test (just instantiate)
- ✅ Centralized configuration
- ✅ Hierarchical structure

---

## Basic Usage

### @PropertySource — Importing Custom Property Files

Load properties from a specific `.properties` file (not `application.yml`):

```java
@Configuration
@PropertySource("classpath:mail.properties")
public class MailConfig {
    // mail.properties keys are now available in Environment
}

@Configuration
@PropertySource("classpath:db-${spring.profiles.active}.properties")
@ConfigurationProperties(prefix = "database")
public class DatabaseConfig {
    private String url;
    private String username;
    private String password;
}
```

```bash
# db-production.properties
database.url=jdbc:postgresql://prod-db:5432/mydb
database.username=admin
database.password=${DB_PASSWORD}
```

> [!tip] `@PropertySource` is useful for loading config from non-standard locations. For most applications, `application.yml` + `application-{profile}.yml` is sufficient. Use `@PropertySource` when you need to load configuration from an external file that doesn't follow Spring Boot's naming conventions.

### Step 1: Create Properties Class

### Step 1: Create Properties Class

```java
package com.example.demo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;
import jakarta.validation.constraints.*;

@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    /**
     * Application name
     */
    @NotBlank
    private String name;
    
    /**
     * Application version
     */
    @NotBlank
    private String version;
    
    /**
     * Maximum concurrent users
     */
    @Min(1)
    @Max(10000)
    private int maxConcurrentUsers = 100;
    
    /**
     * Feature flags
     */
    private boolean experimentalFeaturesEnabled = false;
    
    // Getters and setters (required!)
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    
    public int getMaxConcurrentUsers() { return maxConcurrentUsers; }
    public void setMaxConcurrentUsers(int maxConcurrentUsers) {
        this.maxConcurrentUsers = maxConcurrentUsers;
    }
    
    public boolean isExperimentalFeaturesEnabled() { return experimentalFeaturesEnabled; }
    public void setExperimentalFeaturesEnabled(boolean experimentalFeaturesEnabled) {
        this.experimentalFeaturesEnabled = experimentalFeaturesEnabled;
    }
}
```

### Step 2: Enable Configuration Properties Scanning

```java
// Option 1: Enable scanning on main class
@SpringBootApplication
@ConfigurationPropertiesScan  // Scans for @ConfigurationProperties classes
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}

// Option 2: Enable on @Configuration class
@Configuration
@ConfigurationPropertiesScan(basePackages = "com.example.demo.config")
public class PropertiesConfig {}

// Option 3: Explicitly enable specific properties class
@Configuration
@EnableConfigurationProperties(AppProperties.class)
public class PropertiesConfig {}
```

### Step 3: Configure Properties

```yaml
# application.yml
app:
  name: My Application
  version: 1.0.0
  max-concurrent-users: 500
  experimental-features-enabled: false
```

### Step 4: Inject and Use

```java
@Service
public class ApplicationService {
    
    private final AppProperties appProperties;
    
    // Constructor injection (recommended)
    public ApplicationService(AppProperties appProperties) {
        this.appProperties = appProperties;
    }
    
    public void logStartup() {
        logger.info("Starting {} version {}", 
            appProperties.getName(), 
            appProperties.getVersion()
        );
        logger.info("Max concurrent users: {}", 
            appProperties.getMaxConcurrentUsers()
        );
    }
}
```

---

## Using Records (Java 16+)

```java
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.ConstructorBinding;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Min;

/**
 * Immutable configuration with Java records
 * 
 * - No setters needed (records are immutable)
 * - Cleaner syntax
 * - @ConstructorBinding for parameter binding
 */
@ConfigurationProperties(prefix = "database")
public record DatabaseProperties(
    
    @NotBlank
    String url,
    
    @NotBlank
    String username,
    
    @NotBlank
    String password,
    
    PoolConfig pool
) {
    
    public record PoolConfig(
        @Min(1)
        int minSize,
        
        @Min(1)
        int maxSize,
        
        @Min(1000)
        long connectionTimeoutMs
    ) {
        // Default values via compact constructor
        public PoolConfig {
            if (minSize == 0) minSize = 5;
            if (maxSize == 0) maxSize = 10;
            if (connectionTimeoutMs == 0) connectionTimeoutMs = 30000;
        }
    }
}
```

```yaml
database:
  url: jdbc:postgresql://localhost:5432/mydb
  username: dbuser
  password: dbpass
  pool:
    min-size: 5
    max-size: 20
    connection-timeout-ms: 30000
```

---

## Nested Configuration

### Complex Hierarchical Configuration

```java
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    private Database database = new Database();
    private Cache cache = new Cache();
    private Security security = new Security();
    
    @Valid  // Important: validates nested objects
    public static class Database {
        @NotBlank
        private String url;
        
        @NotBlank
        private String username;
        
        private String password;
        
        @Valid
        private Pool pool = new Pool();
        
        public static class Pool {
            @Min(1)
            private int minSize = 5;
            
            @Min(1)
            private int maxSize = 20;
            
            // Getters and setters
        }
        
        // Getters and setters
    }
    
    @Valid
    public static class Cache {
        @NotBlank
        private String provider = "caffeine";
        
        @Min(0)
        private long ttlSeconds = 3600;
        
        @Min(0)
        private int maxEntries = 1000;
        
        // Getters and setters
    }
    
    @Valid
    public static class Security {
        @Valid
        private Jwt jwt = new Jwt();
        
        public static class Jwt {
            @NotBlank
            private String secret;
            
            @Min(60)
            private long expirationSeconds = 3600;
            
            // Getters and setters
        }
        
        // Getters and setters
    }
    
    // Getters and setters for nested classes
}
```

```yaml
app:
  database:
    url: jdbc:postgresql://localhost:5432/mydb
    username: dbuser
    password: ${DB_PASSWORD}  # From environment variable
    pool:
      min-size: 5
      max-size: 20
  
  cache:
    provider: redis
    ttl-seconds: 1800
    max-entries: 5000
  
  security:
    jwt:
      secret: ${JWT_SECRET}
      expiration-seconds: 7200
```

---

## Lists, Maps, and Complex Types

### List Properties

```java
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    
    /**
     * Simple list
     */
    private List<String> allowedOrigins = new ArrayList<>();
    
    /**
     * List of objects
     */
    private List<ApiKey> apiKeys = new ArrayList<>();
    
    public static class ApiKey {
        @NotBlank
        private String name;
        
        @NotBlank
        private String key;
        
        private List<String> permissions = new ArrayList<>();
        
        // Getters and setters
    }
    
    // Getters and setters
}
```

```yaml
app:
  allowed-origins:
    - http://localhost:3000
    - http://localhost:8080
    - https://example.com
  
  api-keys:
    - name: admin-key
      key: admin-secret-key-123
      permissions:
        - read
        - write
        - delete
    - name: read-only-key
      key: readonly-secret-key-456
      permissions:
        - read
```

### Map Properties

```java
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    
    /**
     * Simple map
     */
    private Map<String, String> labels = new HashMap<>();
    
    /**
     * Map of objects
     */
    private Map<String, Endpoint> endpoints = new HashMap<>();
    
    public static class Endpoint {
        @NotBlank
        private String url;
        
        @Min(1000)
        private int timeoutMs;
        
        private boolean retryEnabled;
        
        // Getters and setters
    }
    
    // Getters and setters
}
```

```yaml
app:
  labels:
    environment: production
    team: backend
    version: 1.0.0
  
  endpoints:
    payment:
      url: https://payment-api.example.com
      timeout-ms: 5000
      retry-enabled: true
    
    notification:
      url: https://notification-api.example.com
      timeout-ms: 3000
      retry-enabled: false
```

### Duration and DataSize

```java
import org.springframework.boot.convert.DurationUnit;
import org.springframework.boot.convert.DataSizeUnit;
import org.springframework.util.unit.DataSize;
import java.time.Duration;
import java.time.temporal.ChronoUnit;

@ConfigurationProperties(prefix = "app")
public class AppProperties {
    
    /**
     * Duration (supports multiple formats)
     */
    private Duration requestTimeout = Duration.ofSeconds(30);
    
    @DurationUnit(ChronoUnit.SECONDS)
    private Duration sessionTimeout = Duration.ofMinutes(30);
    
    /**
     * DataSize (supports KB, MB, GB, etc.)
     */
    @DataSizeUnit(org.springframework.util.unit.DataUnit.MEGABYTES)
    private DataSize maxUploadSize = DataSize.ofMegabytes(10);
    
    private DataSize cacheSize = DataSize.ofGigabytes(1);
    
    // Getters and setters
}
```

```yaml
app:
  request-timeout: 30s  # or 30000ms, or PT30S
  session-timeout: 1800  # In seconds (due to @DurationUnit)
  max-upload-size: 10MB  # or 10485760 bytes
  cache-size: 1GB
```

---

## Validation

### Standard Validation Annotations

```java
import jakarta.validation.constraints.*;
import jakarta.validation.Valid;

@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    // String validation
    @NotNull
    private String name;
    
    @NotBlank  // Not null, not empty, not whitespace
    private String description;
    
    @Size(min = 3, max = 50)
    private String code;
    
    @Pattern(regexp = "^[A-Z0-9]+$", message = "Must be uppercase alphanumeric")
    private String apiKey;
    
    @Email
    private String contactEmail;
    
    // Numeric validation
    @Min(1)
    @Max(100)
    private int maxConnections;
    
    @Positive
    private int port;
    
    @PositiveOrZero
    private int retryAttempts;
    
    @DecimalMin("0.0")
    @DecimalMax("100.0")
    private double percentage;
    
    // Collection validation
    @NotEmpty
    private List<String> requiredList;
    
    @Size(min = 1, max = 10)
    private List<String> limitedList;
    
    // Date/time validation
    @Future
    private LocalDateTime expiryDate;
    
    @Past
    private LocalDate startDate;
    
    // Boolean validation
    @AssertTrue(message = "Terms must be accepted")
    private boolean termsAccepted;
    
    // Nested validation
    @Valid
    @NotNull
    private DatabaseConfig database;
    
    // Getters and setters
}
```

### Custom Validators

```java
// Custom annotation
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UrlValidator.class)
public @interface ValidUrl {
    String message() default "Invalid URL";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
    String[] protocols() default {"http", "https"};
}

// Validator implementation
public class UrlValidator implements ConstraintValidator<ValidUrl, String> {
    
    private String[] protocols;
    
    @Override
    public void initialize(ValidUrl annotation) {
        this.protocols = annotation.protocols();
    }
    
    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null || value.isEmpty()) {
            return true;  // Use @NotBlank for null check
        }
        
        try {
            URL url = new URL(value);
            String protocol = url.getProtocol();
            return Arrays.asList(protocols).contains(protocol);
        } catch (MalformedURLException e) {
            return false;
        }
    }
}

// Usage
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    @ValidUrl(protocols = {"https"})  // Only HTTPS allowed
    private String apiEndpoint;
    
    @ValidUrl
    private String callbackUrl;  // HTTP or HTTPS
    
    // Getters and setters
}
```

### Cross-Field Validation

```java
import jakarta.validation.Constraint;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

// Custom annotation for class-level validation
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = DateRangeValidator.class)
public @interface ValidDateRange {
    String message() default "End date must be after start date";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

// Validator
public class DateRangeValidator implements ConstraintValidator<ValidDateRange, AppProperties.EventConfig> {
    
    @Override
    public boolean isValid(AppProperties.EventConfig config, ConstraintValidatorContext context) {
        if (config.getStartDate() == null || config.getEndDate() == null) {
            return true;  // Null checks handled by @NotNull
        }
        return config.getEndDate().isAfter(config.getStartDate());
    }
}

// Usage
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    @Valid
    private EventConfig event;
    
    @ValidDateRange
    public static class EventConfig {
        @NotNull
        private LocalDate startDate;
        
        @NotNull
        private LocalDate endDate;
        
        // Getters and setters
    }
    
    // Getters and setters
}
```

---

## Property Conversion

### Custom Converters

```java
import org.springframework.boot.context.properties.ConfigurationPropertiesBinding;
import org.springframework.core.convert.converter.Converter;
import org.springframework.stereotype.Component;

// Custom type
public class Endpoint {
    private final String host;
    private final int port;
    
    public Endpoint(String host, int port) {
        this.host = host;
        this.port = port;
    }
    
    // Getters
}

// Converter from String to Endpoint
@Component
@ConfigurationPropertiesBinding
public class EndpointConverter implements Converter<String, Endpoint> {
    
    @Override
    public Endpoint convert(String source) {
        String[] parts = source.split(":");
        if (parts.length != 2) {
            throw new IllegalArgumentException("Invalid endpoint format. Expected host:port");
        }
        
        String host = parts[0];
        int port = Integer.parseInt(parts[1]);
        
        return new Endpoint(host, port);
    }
}

// Usage
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    
    private Endpoint primaryEndpoint;
    private Endpoint secondaryEndpoint;
    
    // Getters and setters
}
```

```yaml
app:
  primary-endpoint: localhost:8080
  secondary-endpoint: backup.example.com:8081
```

---

## Profile-Specific Properties

```java
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    private String environment;
    private Database database = new Database();
    
    public static class Database {
        private String url;
        private int poolSize;
        
        // Getters and setters
    }
    
    // Getters and setters
}
```

```yaml
# application.yml (common)
app:
  environment: unknown

# application-dev.yml
app:
  environment: development
  database:
    url: jdbc:h2:mem:testdb
    pool-size: 5

# application-prod.yml
app:
  environment: production
  database:
    url: ${DB_URL}  # From environment variable
    pool-size: 50
```

---

## Testing Configuration Properties

```java
import org.junit.jupiter.api.Test;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.test.context.ConfigDataApplicationContextInitializer;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;
import org.springframework.beans.factory.annotation.Autowired;

@SpringJUnitConfig
@EnableConfigurationProperties(AppProperties.class)
@TestPropertySource(properties = {
    "app.name=Test App",
    "app.version=1.0.0",
    "app.max-concurrent-users=100"
})
class AppPropertiesTest {
    
    @Autowired
    private AppProperties appProperties;
    
    @Test
    void testPropertiesLoaded() {
        assertThat(appProperties.getName()).isEqualTo("Test App");
        assertThat(appProperties.getVersion()).isEqualTo("1.0.0");
        assertThat(appProperties.getMaxConcurrentUsers()).isEqualTo(100);
    }
}

// Test without Spring context (using records)
@Test
void testRecordProperties() {
    DatabaseProperties props = new DatabaseProperties(
        "jdbc:h2:mem:testdb",
        "sa",
        "",
        new DatabaseProperties.PoolConfig(5, 10, 30000)
    );
    
    assertThat(props.url()).isEqualTo("jdbc:h2:mem:testdb");
    assertThat(props.pool().minSize()).isEqualTo(5);
}
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Missing Getters/Setters

**Problem**: Properties not bound.

```java
// ❌ BAD: No getters/setters
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;  // Not bound!
}

// ✅ GOOD: With getters/setters
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}

// ✅ BETTER: Use record (immutable)
@ConfigurationProperties(prefix = "app")
public record AppProperties(String name) {}
```

### Pitfall 2: Kebab-case vs camelCase

```yaml
# ✅ GOOD: Kebab-case in YAML (recommended)
app:
  max-concurrent-users: 100
  api-base-url: https://api.example.com

# Maps to:
private int maxConcurrentUsers;
private String apiBaseUrl;

# Also works: camelCase in YAML
app:
  maxConcurrentUsers: 100
  apiBaseUrl: https://api.example.com

# Also works: snake_case
app:
  max_concurrent_users: 100
  api_base_url: https://api.example.com
```

### Pitfall 3: Forgetting @Valid for Nested Objects

```java
// ❌ BAD: Nested validation not triggered
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    private Database database;  // Validation ignored!
    
    public static class Database {
        @NotBlank
        private String url;  // Never validated
    }
}

// ✅ GOOD: @Valid enables nested validation
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    @Valid
    @NotNull
    private Database database;  // Validation triggered
    
    public static class Database {
        @NotBlank
        private String url;  // Validated
    }
}
```

### Pitfall 4: Using @Value and @ConfigurationProperties Together

```java
// ❌ AVOID: Mixing approaches
@Service
public class MyService {
    @Value("${app.name}")
    private String appName;
    
    @Autowired
    private AppProperties appProperties;
}

// ✅ GOOD: Consistent approach
@Service
public class MyService {
    private final AppProperties appProperties;
    
    public MyService(AppProperties appProperties) {
        this.appProperties = appProperties;
    }
}
```

---

## Best Practices

> [!tip] Configuration Best Practices
> 1. **Use @ConfigurationProperties over @Value**: Type-safe, validated, testable
> 2. **Use records for immutable config**: Cleaner syntax, immutable by default
> 3. **Enable @Validated**: Fail fast on startup if config invalid
> 4. **Use @Valid for nested objects**: Ensures nested validation triggered
> 5. **Provide defaults**: Sensible defaults for optional properties
> 6. **Document properties**: JavaDoc on fields
> 7. **Use kebab-case in YAML**: Consistent with Spring Boot conventions
> 8. **Externalize secrets**: Use environment variables for passwords/keys
> 9. **Group related properties**: Use nested classes/records
> 10. **Test configuration**: Unit test properties binding

---

## Related Notes

- [[01_Boot_Project_Structure_and_Profiles]] - Profile-specific configuration
- [[03_Web_MVC_Basics]] - Request validation
- [[02_DI_and_Bean_Lifecycle]] - Bean injection

---

> [!question]- Interview Questions
> 
> **Q: What's the difference between @Value and @ConfigurationProperties?**
> A: `@Value` injects single properties with magic strings, no type safety or validation. `@ConfigurationProperties` binds groups of properties to type-safe POJOs with validation, IDE support, and testability. Use `@ConfigurationProperties` for structured configuration, `@Value` for simple one-off values.
> 
> **Q: How do you enable validation on @ConfigurationProperties?**
> A: Add `@Validated` to the properties class and use Jakarta validation annotations (`@NotBlank`, `@Min`, etc.). For nested objects, add `@Valid` to trigger recursive validation. Spring validates properties at startup and fails if invalid.
> 
> **Q: Can you use records with @ConfigurationProperties?**
> A: Yes (Spring Boot 2.6+). Records are immutable, cleaner syntax, no getters/setters needed. Example: `@ConfigurationProperties(prefix = "app") public record AppProps(String name, int port) {}`. Spring binds via constructor parameters.
> 
> **Q: How does Spring Boot handle property name mapping?**
> A: Spring Boot supports multiple formats: kebab-case (`max-users`), camelCase (`maxUsers`), snake_case (`max_users`), and uppercase (`MAX_USERS` for env vars). All map to Java camelCase field (`maxUsers`). Recommendation: Use kebab-case in YAML.
> 
> **Q: Why use @Valid on nested configuration objects?**
> A: Without `@Valid`, Spring doesn't validate nested objects even if they have validation annotations. `@Valid` triggers recursive validation. Example: `@Valid private Database database;` ensures `database.url` is validated if annotated with `@NotBlank`.
