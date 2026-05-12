---
tags: [java, advanced, reflection, annotations, method-handles, proxy, annotation-processing]
aliases: ["Reflection API", "Annotations", "MethodHandle", "VarHandle", "Proxy", "Annotation Processing"]
status: stable
updated: 2026-05-09
---

# Reflection and Annotations

> [!summary] Goal
> Master Java reflection: inspect and invoke classes/methods/fields at runtime. Understand annotations (declaration, retention, processing at compile-time and runtime). Use `MethodHandle`, `VarHandle`, and `Proxy` for advanced reflective patterns.

## Table of Contents

1. [Reflection API](#reflection-api)
2. [Annotations](#annotations)
3. [MethodHandle and VarHandle](#methodhandle-and-varhandle)
4. [Dynamic Proxy](#dynamic-proxy)
5. [Annotation Processing](#annotation-processing)
6. [Pitfalls](#pitfalls)

---

## Reflection API

> [!info] Reflection
> Reflection allows a program to inspect and manipulate its own structure at runtime: load classes dynamically, discover methods/fields/constructors, invoke methods, and access fields — all by name. This is the foundation of frameworks (Spring, Hibernate, Jackson) but has performance cost and bypasses compile-time safety.

```java
// Getting a Class object
Class<?> clazz1 = String.class;                    // 1. Class literal
Class<?> clazz2 = "hello".getClass();               // 2. Object.getClass()
Class<?> clazz3 = Class.forName("java.lang.String"); // 3. Class.forName (dynamic loading)

// Inspecting a class
Class<?> clazz = User.class;
System.out.println(clazz.getName());                // "com.example.User"
System.out.println(clazz.getSimpleName());          // "User"
System.out.println(clazz.getPackageName());         // "com.example"
System.out.println(Modifier.toString(clazz.getModifiers())); // "public"

// Methods
Method[] methods = clazz.getMethods();              // Public methods including inherited
Method[] declared = clazz.getDeclaredMethods();     // All methods in this class only

// Fields
Field[] fields = clazz.getDeclaredFields();

// Constructors
Constructor<?>[] ctors = clazz.getDeclaredConstructors();
```

### Dynamic invocation

```java
public class User {
    private String name;
    
    public User(String name) { this.name = name; }
    
    public String greet(String greeting) {
        return greeting + ", " + name + "!";
    }
}

// Dynamic instantiation and invocation
Class<?> clazz = Class.forName("com.example.User");

// Constructor
Constructor<?> ctor = clazz.getConstructor(String.class);
Object user = ctor.newInstance("Alice");

// Method invocation
Method greetMethod = clazz.getMethod("greet", String.class);
String result = (String) greetMethod.invoke(user, "Hello");
System.out.println(result);                        // "Hello, Alice!"

// Field access (private — need setAccessible)
Field nameField = clazz.getDeclaredField("name");
nameField.setAccessible(true);                     // Bypass access control!
String name = (String) nameField.get(user);
System.out.println(name);                          // "Alice"
```

### setAccessible and modules

```java
// In Java 9+, setAccessible on internal APIs fails unless the package is opened
// Fix: add opens in module-info.java:
// opens com.example.model to some.module;

// Or JVM flag:
// --add-opens java.base/java.lang=ALL-UNNAMED
```

---

## Annotations

> [!info] Annotation
> An annotation adds metadata to Java code (classes, methods, fields, parameters). Annotations can be processed at compile time (code generation, validation) or at runtime (serialization, DI, testing). They don't directly affect program semantics — other code reads and acts on them.

```java
// Declaring an annotation
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)      // Available at runtime
@Target({ElementType.METHOD, ElementType.TYPE})  // Applies to methods and classes
public @interface Loggable {
    String level() default "INFO";       // Element with default value
    boolean includeArgs() default false;
}

// Using the annotation
@Loggable
public class OrderService {
    
    @Loggable(level = "DEBUG", includeArgs = true)
    public void createOrder(String userId, double amount) {
        // ...
    }
}
```

### Retention policies

| Retention | Available at runtime? | Use case |
|-----------|:---------------------:|----------|
| `SOURCE` | ❌ (discarded after compilation) | `@SuppressWarnings`, `@Override` — compile-time checks |
| `CLASS` | ❌ (in bytecode, not loaded) | Bytecode processing tools |
| `RUNTIME` | ✅ (loaded into JVM) | `@Test`, `@Autowired`, serialization annotations |

### Reading annotations at runtime

```java
// Read class-level annotation
Class<OrderService> clazz = OrderService.class;
Loggable classLog = clazz.getAnnotation(Loggable.class);
if (classLog != null) {
    System.out.println("Class log level: " + classLog.level());
}

// Read method-level annotation
Method method = clazz.getMethod("createOrder", String.class, double.class);
Loggable methodLog = method.getAnnotation(Loggable.class);
if (methodLog != null) {
    System.out.println("Method log level: " + methodLog.level());
    System.out.println("Include args: " + methodLog.includeArgs());
}

// Find all annotated methods
for (Method m : clazz.getMethods()) {
    if (m.isAnnotationPresent(Loggable.class)) {
        System.out.println("Annotated method: " + m.getName());
    }
}
```

---

## MethodHandle and VarHandle

> [!info] MethodHandle
> `MethodHandle` is a modern, typesafe alternative to reflection for method invocation. It's faster than `Method.invoke()` (the JVM can inline and optimize it) and more type-safe (it has a method type signature). Prefer it over reflection in performance-sensitive code.

```java
import java.lang.invoke.*;

// MethodHandle — invoke a method by handle (faster than reflection)
MethodHandles.Lookup lookup = MethodHandles.lookup();

// Static method
MethodHandle staticHello = lookup.findStatic(Utils.class, "format",
    MethodType.methodType(String.class, String.class, Object[].class));
String result = (String) staticHello.invoke("Hello %s!", "World");

// Instance method
MethodHandle greet = lookup.findVirtual(User.class, "greet",
    MethodType.methodType(String.class, String.class));
User user = new User("Alice");
String msg = (String) greet.invoke(user, "Hi");

// Constructor
MethodHandle ctor = lookup.findConstructor(User.class,
    MethodType.methodType(void.class, String.class));
User newUser = (User) ctor.invoke("Bob");
```

### VarHandle — atomic field access

```java
// VarHandle provides atomic operations on object fields
// Faster and safer than comparing-and-swapping via reflection
import java.lang.invoke.VarHandle;

public class Counter {
    private volatile int count = 0;
    
    private static final VarHandle COUNT;
    
    static {
        try {
            COUNT = MethodHandles.lookup()
                .findVarHandle(Counter.class, "count", int.class);
        } catch (Exception e) {
            throw new Error(e);
        }
    }
    
    public void increment() {
        COUNT.getAndAdd(this, 1);                    // Atomic increment
    }
    
    public boolean compareAndSet(int expected, int newValue) {
        return COUNT.compareAndSet(this, expected, newValue);  // CAS
    }
}
```

---

## Dynamic Proxy

> [!info] Dynamic proxy
> `Proxy.newProxyInstance()` creates an implementation of an interface at runtime. Each method call on the proxy is forwarded to an `InvocationHandler`. This is the foundation of AOP (Aspect Oriented Programming) — used by Spring transactions, Hibernate lazy loading, and caching proxies.

```java
import java.lang.reflect.Proxy;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;

// Interface to proxy
public interface DataService {
    String fetchData(String key);
}

// Real implementation
public class RealDataService implements DataService {
    @Override public String fetchData(String key) {
        System.out.println("Fetching " + key + " from DB...");
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        return "data_for_" + key;
    }
}

// Logging proxy
public class LoggingHandler implements InvocationHandler {
    private final Object target;
    
    public LoggingHandler(Object target) { this.target = target; }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        long start = System.nanoTime();
        Object result = method.invoke(target, args);       // Forward to real implementation
        long elapsed = (System.nanoTime() - start) / 1_000_000;
        
        System.out.println(method.getName() + " took " + elapsed + "ms");
        return result;
    }
}

// Usage — create proxy at runtime
DataService realService = new RealDataService();
DataService proxied = (DataService) Proxy.newProxyInstance(
    DataService.class.getClassLoader(),
    new Class[]{DataService.class},
    new LoggingHandler(realService)
);

String data = proxied.fetchData("users");  // Automatically logged!
```

---

## Annotation Processing

> [!info] Annotation processing
> Compile-time annotation processing generates code (Java files, resources) based on annotations. Processors run during compilation (`javac`). Used by: Lombok (`@Data` generates getters/setters), MapStruct (generates mapper implementations), Google Auto (generates `ServiceLoader` config).

```java
// javax.annotation.processing API
import javax.annotation.processing.*;

@SupportedAnnotationTypes("com.example.Loggable")
@SupportedSourceVersion(SourceVersion.RELEASE_21)
public class LogProcessor extends AbstractProcessor {
    
    @Override
    public boolean process(Set<? extends TypeElement> annotations, RoundEnvironment roundEnv) {
        for (Element element : roundEnv.getElementsAnnotatedWith(Loggable.class)) {
            if (element.getKind() == ElementKind.METHOD) {
                MethodElement method = (MethodElement) element;
                // Generate code, validate, or emit errors
                processingEnv.getMessager().printMessage(
                    Diagnostic.Kind.NOTE,
                    "Processing annotation on: " + method.getSimpleName()
                );
            }
        }
        return true;
    }
}
```

---

## Pitfalls

### Reflection performance

`Method.invoke()` is significantly slower than direct invocation (it boxes arguments, checks access, and can't be JIT-inlined after the first few calls). `MethodHandle.invoke()` is faster (the JVM can inline it). Use direct calls in hot paths, reflection/sparingly.

### setAccessible in a module

With JPMS, `setAccessible(true)` throws `InaccessibleObjectException` unless the target package is opened. Add `opens com.example.model;` to `module-info.java` or use `--add-opens` flags. This affects all reflection-heavy frameworks.

### Annotation processor not running

Maven requires explicit configuration for annotation processors:
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <annotationProcessorPaths>
            <path><groupId>org.projectlombok</groupId>
                 <artifactId>lombok</artifactId></path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

### Caching reflective lookups

`Class.forName()`, `Class.getMethod()`, and `Class.getField()` are expensive. Cache the results (`Map<Class, Map<String, Method>>`) when repeatedly accessing the same class.

---

> [!question]- Interview Questions
>
> **Q: How does `Proxy.newProxyInstance` work?**
> A: It dynamically creates a class that implements the specified interfaces. Each method call on the proxy is forwarded to the `InvocationHandler.invoke()` method, which can intercept, log, wrap, or delegate to the real implementation. Spring uses this for AOP proxies (transactions, security, caching). The proxy class is generated in memory at runtime.
>
> **Q: What is the difference between `Method.invoke()` and `MethodHandle.invoke()`?**
> A: `Method.invoke()` uses traditional reflection — JIT can't inline it after the first few invocations (it's a native method with argument boxing). `MethodHandle.invoke()` has a typed signature (`MethodType`) that the JVM understands and can inline like a direct call. In benchmarks, `MethodHandle` can be 2-10× faster than reflection in hot code.
>
> **Q: What are the retention policies for annotations?**
> A: `SOURCE` — discarded after compilation (compile-time checks like `@Override`). `CLASS` — stored in bytecode but not loaded at runtime (bytecode processing tools). `RUNTIME` — available via reflection at runtime (most frameworks). Choose the most restrictive policy that still allows your use case.
>
> **Q: How does the module system affect reflection?**
> A: In Java 9+, `setAccessible(true)` on private members of classes in other modules fails by default. The target package must be `opens` (open) in its module-info. This fixes a long-standing encapsulation hole — previously, any code could use reflection to access any private member. Frameworks need explicit `opens` declarations.
>
> **Q: What is compile-time annotation processing?**
> A: Annotation processors run during `javac` compilation. They read annotations and can generate new Java source files, emit errors/warnings, or process metadata. Examples: Lombok (generate getters/setters/constructors), MapStruct (generate mapper implementations), Google Auto (generate ServiceLoader files). Processors are discovered via `META-INF/services/javax.annotation.processing.Processor`.

---

## Cross-Links

- [[Java/03_Advanced/02_JMM_Volatile_and_Locks]] for VarHandle vs volatile
- [[Java/03_Advanced/08_Module_System_JPMS]] for opens directives in module-info
- [[Java/01_Foundations/05_Modern_Java_Language_Features]] for records and annotations
- [[Java/03_Advanced/05_GraalVM_Native_Image_and_AOT]] for reflection configuration in native-image
- [[Java/01_Foundations/06_Build_Tools_Maven_Gradle]] for annotation processor configuration
