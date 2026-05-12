---
tags: [springboot, cheatsheet, annotations, configurations, commands]
aliases: ["SpringBoot Cheat Sheets", "Spring Annotations Reference", "Spring Configuration Quick Reference"]
status: stable
updated: 2026-04-27
---

# SpringBoot Cheat Sheets

> [!summary] Quick Reference
> Comprehensive cheat sheets for SpringBoot: 50+ annotations, configurations, commands, and best practices. Use for quick lookups during development.

## Table of Contents

1. [[#SpringBoot Annotations Cheat Sheet]]
2. [[#Configuration Properties Cheat Sheet]]
3. [[#Spring Data JPA Cheat Sheet]]
4. [[#Transactions and Locking Cheat Sheet]]
5. [[#Common Commands and Properties]]
6. [[#Dependency Injection Patterns]]
7. [[#Web MVC Cheat Sheet]]
8. [[#Testing Cheat Sheet]]
9. [[#Security Cheat Sheet]]
10. [[#Monitoring and Observability Cheat Sheet]]

---

## SpringBoot Annotations Cheat Sheet

### Core Boot Annotations
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@SpringBootApplication` | Main app class, combines @Configuration, @EnableAutoConfiguration, @ComponentScan | `@SpringBootApplication(scanBasePackages = "com.example")` |
| `@EnableAutoConfiguration` | Auto-configures beans based on classpath | Usually included in @SpringBootApplication |
| `@ComponentScan` | Scans for @Component classes | `@ComponentScan(basePackages = "com.example")` |
| `@Configuration` | Marks class as bean definition source | `@Configuration public class AppConfig {}` |
| `@Import` | Imports configuration classes | `@Import(DataSourceConfig.class)` |
| `@ConditionalOnClass` | Creates bean only if class is on classpath | `@ConditionalOnClass(DataSource.class)` |
| `@ConditionalOnMissingClass` | Creates bean only if class is NOT on classpath | `@ConditionalOnMissingClass("com.mysql.Driver")` |
| `@ConditionalOnProperty` | Creates bean based on property value | `@ConditionalOnProperty(name = "app.feature.enabled", havingValue = "true")` |
| `@ConditionalOnBean` | Creates bean only if another bean exists | `@ConditionalOnBean(DataSource.class)` |
| `@ConditionalOnMissingBean` | Creates bean only if another bean does NOT exist | `@ConditionalOnMissingBean(DataSource.class)` |

### Component Stereotypes
| Annotation | Purpose | Scope | Example |
|------------|---------|-------|---------|
| `@Component` | Generic component | Singleton | `@Component public class MyService {}` |
| `@Service` | Business logic service | Singleton | `@Service public class UserService {}` |
| `@Repository` | Data access component | Singleton | `@Repository public class UserRepository {}` |
| `@Controller` | Web controller | Singleton | `@Controller public class UserController {}` |
| `@RestController` | REST controller (combines @Controller + @ResponseBody) | Singleton | `@RestController public class ApiController {}` |
| `@Configuration` | Configuration class | Singleton | See above |

### Dependency Injection
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@Autowired` | Injects dependencies | `@Autowired private UserService userService;` |
| `@Qualifier` | Specifies which bean to inject | `@Autowired @Qualifier("primaryDataSource") DataSource ds;` |
| `@Primary` | Marks bean as primary choice for autowiring | `@Primary @Bean public DataSource primaryDs() {}` |
| `@Resource` | JSR-250 injection by name | `@Resource(name="myBean") MyBean bean;` |
| `@Inject` | JSR-330 injection | `@Inject private UserService userService;` |
| `@Value` | Injects property values | `@Value("${app.name}") private String appName;` |
| `@ConfigurationProperties` | Binds properties to object | `@ConfigurationProperties(prefix = "app") public class AppProperties {}` |

### Web MVC Annotations
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@RequestMapping` | Maps HTTP requests | `@RequestMapping("/users")` |
| `@GetMapping` | Maps GET requests | `@GetMapping("/users/{id}")` |
| `@PostMapping` | Maps POST requests | `@PostMapping("/users")` |
| `@PutMapping` | Maps PUT requests | `@PutMapping("/users/{id}")` |
| `@DeleteMapping` | Maps DELETE requests | `@DeleteMapping("/users/{id}")` |
| `@PatchMapping` | Maps PATCH requests | `@PatchMapping("/users/{id}")` |
| `@RequestParam` | Binds query parameters | `@RequestParam("name") String name` |
| `@PathVariable` | Binds URI variables | `@PathVariable("id") Long id` |
| `@RequestBody` | Binds request body | `@RequestBody UserDto user` |
| `@ResponseBody` | Returns object as response body | `@ResponseBody public User getUser() {}` |
| `@ModelAttribute` | Binds form data | `@ModelAttribute UserForm form` |
| `@SessionAttribute` | Binds session attributes | `@SessionAttribute("user") User user` |
| `@CookieValue` | Binds cookie values | `@CookieValue("sessionId") String sid` |
| `@RequestHeader` | Binds request headers | `@RequestHeader("User-Agent") String ua` |

### Validation Annotations
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@Valid` | Validates nested objects | `@PostMapping public ResponseEntity save(@Valid @RequestBody UserDto dto)` |
| `@NotNull` | Field must not be null | `@NotNull private String name;` |
| `@NotEmpty` | Collection/string must not be empty | `@NotEmpty private List<String> items;` |
| `@NotBlank` | String must not be blank | `@NotBlank private String email;` |
| `@Size` | Size constraints | `@Size(min = 2, max = 50) private String name;` |
| `@Min/@Max` | Numeric constraints | `@Min(18) private int age;` |
| `@Email` | Email format | `@Email private String email;` |
| `@Pattern` | Regex pattern | `@Pattern(regexp = "^[0-9]{10}$") private String phone;` |

### Aspect-Oriented Programming
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableAspectJAutoProxy` | Enables AOP proxying | Usually in @Configuration |
| `@Aspect` | Marks class as aspect | `@Aspect @Component public class LoggingAspect {}` |
| `@Before` | Advice before method execution | `@Before("execution(* com.example.*.*(..))")` |
| `@After` | Advice after method execution | `@After("execution(* com.example.*.*(..))")` |
| `@AfterReturning` | Advice after successful return | `@AfterReturning(pointcut = "serviceMethods()", returning = "result")` |
| `@AfterThrowing` | Advice after exception | `@AfterThrowing(pointcut = "serviceMethods()", throwing = "ex")` |
| `@Around` | Advice around method execution | `@Around("serviceMethods()")` |
| `@Pointcut` | Defines reusable pointcut | `@Pointcut("execution(* com.example.service.*.*(..))") public void serviceMethods() {}` |

### Transaction Management
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableTransactionManagement` | Enables declarative transactions | Usually in @Configuration |
| `@Transactional` | Marks method/class as transactional | `@Transactional public void save(User user) {}` |
| `@Transactional(readOnly = true)` | Read-only transaction | `@Transactional(readOnly = true) public User findById(Long id) {}` |
| `@Transactional(isolation = Isolation.SERIALIZABLE)` | Sets isolation level | `@Transactional(isolation = Isolation.READ_COMMITTED)` |
| `@Transactional(propagation = Propagation.REQUIRES_NEW)` | Sets propagation | `@Transactional(propagation = Propagation.REQUIRED)` |
| `@Transactional(rollbackFor = Exception.class)` | Rollback triggers | `@Transactional(rollbackFor = {Exception.class})` |

### Caching
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableCaching` | Enables Spring caching | Usually in @Configuration |
| `@Cacheable` | Caches method result | `@Cacheable("users") public User findById(Long id) {}` |
| `@CachePut` | Updates cache with result | `@CachePut(value = "users", key = "#user.id")` |
| `@CacheEvict` | Removes from cache | `@CacheEvict(value = "users", key = "#id")` |
| `@Caching` | Groups multiple cache operations | `@Caching(evict = {@CacheEvict("users"), @CacheEvict("userNames")})` |

### Scheduling
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableScheduling` | Enables task scheduling | Usually in @Configuration |
| `@Scheduled` | Schedules method execution | `@Scheduled(fixedRate = 5000)` |
| `@Scheduled(cron = "0 0 * * * *")` | Cron expression | `@Scheduled(cron = "0 */30 * * * *")` |

### Async Processing
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableAsync` | Enables async processing | Usually in @Configuration |
| `@Async` | Executes method asynchronously | `@Async public CompletableFuture<User> findById(Long id) {}` |

### Event Handling
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EventListener` | Listens for application events | `@EventListener public void handleContextStart(ContextStartedEvent event) {}` |
| `@Async` | Async event listener | `@EventListener @Async public void handleAsyncEvent(MyEvent event) {}` |

### Security (Basic)
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableWebSecurity` | Enables web security | Usually in @Configuration |
| `@PreAuthorize` | Method-level authorization | `@PreAuthorize("hasRole('ADMIN')")` |
| `@Secured` | Role-based security | `@Secured("ROLE_ADMIN")` |
| `@EnableGlobalMethodSecurity` | Enables method security | Usually in @Configuration |

### Testing
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@SpringBootTest` | Full application context test | `@SpringBootTest public class ApplicationTests {}` |
| `@WebMvcTest` | MVC layer test | `@WebMvcTest(UserController.class)` |
| `@DataJpaTest` | JPA layer test | `@DataJpaTest public class RepositoryTests {}` |
| `@Test` | Test method | `@Test public void testMethod() {}` |
| `@MockBean` | Mocks Spring bean | `@MockBean private UserService userService;` |
| `@Autowired` | Injects test dependencies | `@Autowired private MockMvc mockMvc;` |

### Actuator/Monitoring
| Annotation | Purpose | Example |
|------------|---------|---------|
| `@EnableActuator` | Enables Spring Boot Actuator | Usually in @Configuration |
| `@Endpoint` | Custom actuator endpoint | `@Endpoint(id = "custom") public class CustomEndpoint {}` |
| `@ReadOperation` | Read endpoint method | `@ReadOperation public Map<String, Object> info() {}` |

---

## Configuration Properties Cheat Sheet

### Application Properties
```properties
# Server Configuration
server.port=8080
server.servlet.context-path=/api
server.error.include-message=always

# Database Configuration
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=user
spring.datasource.password=password
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA/Hibernate
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect

# Logging
logging.level.com.example=DEBUG
logging.level.org.springframework.web=INFO
logging.file.name=app.log
logging.logback.rollingpolicy.max-file-size=10MB

# Profiles
spring.profiles.active=dev,local
```

### YAML Format
```yaml
server:
  port: 8080
  servlet:
    context-path: /api

spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: user
    password: password
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
  profiles:
    active: dev,local

logging:
  level:
    com.example: DEBUG
  file:
    name: app.log
```

---

## Spring Data JPA Cheat Sheet

### Repository Methods
```java
public interface UserRepository extends JpaRepository<User, Long> {
    // Basic CRUD (inherited)
    User save(User user);
    Optional<User> findById(Long id);
    List<User> findAll();
    void deleteById(Long id);
    
    // Custom queries
    List<User> findByEmail(String email);
    List<User> findByNameContaining(String name);
    List<User> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    // JPQL
    @Query("SELECT u FROM User u WHERE u.status = :status")
    List<User> findActiveUsers(@Param("status") String status);
    
    // Native SQL
    @Query(value = "SELECT * FROM users WHERE age > ?", nativeQuery = true)
    List<User> findUsersOlderThan(int age);
    
    // Modifying queries
    @Modifying
    @Query("UPDATE User u SET u.lastLogin = :now WHERE u.id = :id")
    void updateLastLogin(@Param("id") Long id, @Param("now") LocalDateTime now);
}
```

### Entity Relationships
```java
// One-to-One
@Entity
public class User {
    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL)
    private Profile profile;
}

@Entity
public class Profile {
    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;
}

// One-to-Many
@Entity
public class User {
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Order> orders = new ArrayList<>();
}

@Entity
public class Order {
    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;
}

// Many-to-Many
@Entity
public class User {
    @ManyToMany
    @JoinTable(name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id"))
    private Set<Role> roles = new HashSet<>();
}
```

### Fetch Strategies
```java
// Lazy Loading (default for collections)
@OneToMany(fetch = FetchType.LAZY)
private List<Order> orders;

// Eager Loading
@ManyToOne(fetch = FetchType.EAGER)
private User user;

// Fetch Join in queries
@Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
User findUserWithOrders(@Param("id") Long id);

// Entity Graph
@NamedEntityGraph(name = "User.withOrders", 
    attributeNodes = @NamedAttributeNode("orders"))
@Entity
public class User { }

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    @EntityGraph("User.withOrders")
    User findById(Long id);
}
```

---

## Transactions and Locking Cheat Sheet

### Transaction Propagation
| Propagation | Behavior |
|-------------|----------|
| REQUIRED | Uses existing or creates new (default) |
| REQUIRES_NEW | Always creates new transaction |
| SUPPORTS | Uses existing if present, no transaction otherwise |
| NOT_SUPPORTED | Suspends existing, runs without transaction |
| MANDATORY | Requires existing transaction |
| NEVER | Fails if transaction exists |
| NESTED | Creates nested transaction if supported |

### Isolation Levels
| Isolation | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|-----------|------------|---------------------|--------------|-------------|
| READ_UNCOMMITTED | ✓ | ✓ | ✓ | Fastest |
| READ_COMMITTED | ✗ | ✓ | ✓ | Default (PostgreSQL) |
| REPEATABLE_READ | ✗ | ✗ | ✓ | Slower |
| SERIALIZABLE | ✗ | ✗ | ✗ | Slowest |

### Locking Types
```java
// Optimistic Locking
@Entity
public class Product {
    @Version
    private Long version;
    
    @Transactional
    public void updateStock(Long id, int newStock) {
        Product product = productRepository.findById(id)
            .orElseThrow();
        product.setStock(newStock);
        productRepository.save(product); // Version check happens here
    }
}

// Pessimistic Locking
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Product findByIdWithLock(@Param("id") Long id);
}

@Service
public class ProductService {
    @Transactional
    public void updateStock(Long id, int newStock) {
        Product product = productRepository.findByIdWithLock(id);
        product.setStock(newStock);
        productRepository.save(product);
    }
}
```

---

## Common Commands and Properties

### Maven Commands
```bash
# Run application
mvn spring-boot:run

# Build JAR
mvn clean package

# Run JAR
java -jar target/myapp-0.0.1-SNAPSHOT.jar

# Run with profile
mvn spring-boot:run -Dspring-boot.run.profiles=prod

# Test with profile
mvn test -Dspring.profiles.active=test
```

### Gradle Commands
```bash
# Run application
./gradlew bootRun

# Build JAR
./gradlew build

# Run JAR
java -jar build/libs/myapp-0.0.1-SNAPSHOT.jar

# Run with profile
./gradlew bootRun --args='--spring.profiles.active=prod'
```

### Actuator Endpoints
```
GET /actuator/health      # Application health
GET /actuator/info        # Application info
GET /actuator/metrics     # Metrics
GET /actuator/env         # Environment properties
GET /actuator/beans       # Spring beans
GET /actuator/configprops # Configuration properties
GET /actuator/mappings    # Request mappings
GET /actuator/loggers     # Logger configuration
```

### Key Properties
```properties
# Externalized Configuration
spring.config.location=file:/path/to/config/
spring.config.name=application,myapp

# Profiles
spring.profiles.active=dev
spring.profiles.include=common,local

# Logging
logging.level.root=INFO
logging.level.com.example=DEBUG
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} - %msg%n
logging.pattern.file=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n

# Database Connection Pool (HikariCP)
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=20000
spring.datasource.hikari.idle-timeout=300000
```

---

## Dependency Injection Patterns

### Constructor Injection (Recommended)
```java
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}
```

### Setter Injection
```java
@Service
public class UserService {
    private UserRepository userRepository;
    
    @Autowired
    public void setUserRepository(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

### Field Injection
```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
}
```

### Configuration Class
```java
@Configuration
public class AppConfig {
    @Bean
    public UserService userService(UserRepository userRepository) {
        return new UserService(userRepository);
    }
    
    @Bean
    @Primary
    public DataSource primaryDataSource() {
        // Configure primary datasource
    }
    
    @Bean
    @Qualifier("secondary")
    public DataSource secondaryDataSource() {
        // Configure secondary datasource
    }
}
```

---

## Web MVC Cheat Sheet

### Controller Patterns
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<UserDto> getAllUsers() {
        return userService.getAllUsers();
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(user -> ResponseEntity.ok(toDto(user)))
            .orElse(ResponseEntity.notFound().build());
    }
    
    @PostMapping
    public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserRequest request) {
        User user = userService.createUser(request);
        return ResponseEntity.created(URI.create("/api/users/" + user.getId()))
            .body(toDto(user));
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<UserDto> updateUser(@PathVariable Long id, @Valid @RequestBody UpdateUserRequest request) {
        User user = userService.updateUser(id, request);
        return ResponseEntity.ok(toDto(user));
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

### Exception Handling
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("USER_NOT_FOUND", ex.getMessage()));
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error -> 
            errors.put(error.getField(), error.getDefaultMessage()));
        
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", "Validation failed", errors));
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred"));
    }
}
```

### Content Negotiation
```java
@GetMapping(value = "/users/{id}", produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE})
public UserDto getUser(@PathVariable Long id) {
    return userService.findById(id);
}

// Custom response based on Accept header
@GetMapping("/report")
public ResponseEntity<byte[]> getReport(@RequestParam String format) {
    byte[] report = reportService.generateReport(format);
    HttpHeaders headers = new HttpHeaders();
    
    if ("pdf".equals(format)) {
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("attachment", "report.pdf");
    } else {
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
    }
    
    return ResponseEntity.ok().headers(headers).body(report);
}
```

---

## Testing Cheat Sheet

### Unit Tests
```java
@SpringBootTest
public class UserServiceTest {
    
    @Test
    public void shouldCreateUser() {
        // Given
        CreateUserRequest request = new CreateUserRequest("John", "john@example.com");
        
        // When
        User user = userService.createUser(request);
        
        // Then
        assertThat(user.getId()).isNotNull();
        assertThat(user.getName()).isEqualTo("John");
        assertThat(user.getEmail()).isEqualTo("john@example.com");
    }
}
```

### Integration Tests
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class UserControllerIT {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    public void shouldGetUser() {
        // When
        ResponseEntity<UserDto> response = restTemplate.getForEntity("/api/users/1", UserDto.class);
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().getName()).isEqualTo("John");
    }
}
```

### Web Layer Tests
```java
@WebMvcTest(UserController.class)
public class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    public void shouldReturnUser() throws Exception {
        // Given
        UserDto userDto = new UserDto(1L, "John", "john@example.com");
        when(userService.findById(1L)).thenReturn(Optional.of(userDto));
        
        // When & Then
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("John"))
            .andExpect(jsonPath("$.email").value("john@example.com"));
    }
}
```

### Data Layer Tests
```java
@DataJpaTest
public class UserRepositoryTest {
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    public void shouldSaveAndFindUser() {
        // Given
        User user = new User("John", "john@example.com");
        
        // When
        User saved = userRepository.save(user);
        
        // Then
        assertThat(saved.getId()).isNotNull();
        assertThat(userRepository.findById(saved.getId())).isPresent();
    }
}
```

---

## Security Cheat Sheet

### Basic Security Configuration
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/api/public/**").permitAll()
                .antMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .formLogin()
            .and()
            .httpBasic();
    }
    
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth
            .inMemoryAuthentication()
            .withUser("user").password(passwordEncoder().encode("password")).roles("USER")
            .and()
            .withUser("admin").password(passwordEncoder().encode("password")).roles("ADMIN");
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### Method Security
```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class MethodSecurityConfig extends GlobalMethodSecurityConfiguration {
}

@Service
public class UserService {
    
    @PreAuthorize("hasRole('ADMIN') or #userId == principal.id")
    public User updateUser(Long userId, UpdateUserRequest request) {
        // Only admin or user themselves can update
    }
    
    @Secured("ROLE_ADMIN")
    public void deleteUser(Long userId) {
        // Only admin can delete
    }
    
    @PostAuthorize("returnObject.owner == principal.username")
    public User getUser(Long userId) {
        // Check after method execution
    }
}
```

### JWT Configuration
```java
@Configuration
public class JwtConfig {
    
    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withJwkSetUri("https://example.com/.well-known/jwks.json").build();
    }
    
    @Bean
    public JwtEncoder jwtEncoder() {
        JWK jwk = new RSAKey.Builder(rsaKey().toRSAPublicKey())
            .privateKey(rsaKey().toRSAPrivateKey())
            .build();
        return new NimbusJwtEncoder(new ImmutableJWKSet<>(new JWKSet(jwk)));
    }
}
```

---

## Monitoring and Observability Cheat Sheet

### Metrics
```java
@Service
public class UserService {
    
    @Autowired
    private MeterRegistry meterRegistry;
    
    public User createUser(CreateUserRequest request) {
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            User user = userRepository.save(new User(request.getName(), request.getEmail()));
            meterRegistry.counter("users.created").increment();
            return user;
        } finally {
            sample.stop(Timer.builder("user.creation.time").register(meterRegistry));
        }
    }
}
```

### Custom Health Indicator
```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            connection.createStatement().execute("SELECT 1");
            return Health.up().build();
        } catch (Exception e) {
            return Health.down().withDetail("error", e.getMessage()).build();
        }
    }
}
```

### Logging
```java
@Service
public class UserService {
    
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    
    @Transactional
    public User createUser(CreateUserRequest request) {
        logger.info("Creating user with email: {}", request.getEmail());
        
        try {
            User user = userRepository.save(new User(request.getName(), request.getEmail()));
            logger.info("Successfully created user with id: {}", user.getId());
            return user;
        } catch (Exception e) {
            logger.error("Failed to create user with email: {}", request.getEmail(), e);
            throw e;
        }
    }
}
```

### Distributed Tracing
```java
@Configuration
public class TracingConfig {
    
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder.build();
    }
}

@Service
public class UserService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    public User getUserWithDetails(Long userId) {
        // This span will be automatically created
        User user = userRepository.findById(userId).orElseThrow();
        
        // Call external service - new span
        ResponseEntity<UserDetails> response = restTemplate.getForEntity(
            "http://user-details-service/users/{id}/details", 
            UserDetails.class, 
            userId);
        
        user.setDetails(response.getBody());
        return user;
    }
}
```

---

## Cross-Links

- **Project Structure**: [[SpringBoot/01_Foundations/01_Boot_Project_Structure_and_Profiles]]
- **Dependency Injection**: [[SpringBoot/01_Foundations/02_Dependency_Injection_and_IoC_Container]]
- **JPA Essentials**: [[SpringBoot/02_Core/01_Spring_Data_JPA_Essentials]]
- **Transactions**: [[SpringBoot/02_Core/02_Transactions_and_Propagation]]
- **Web MVC**: [[SpringBoot/01_Foundations/03_Web_MVC_Request_Processing]]

## References

- [Spring Boot Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Spring Framework Documentation](https://docs.spring.io/spring-framework/docs/current/reference/html/)
- [Spring Data JPA Documentation](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/)
- [Spring Security Documentation](https://docs.spring.io/spring-security/reference/)

---

**Status**: stable  
**Last Updated**: 2026-04-27  
**Lines**: 650