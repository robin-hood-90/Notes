---
tags: [java, advanced, networking, http-client, websocket, nio, selector, http2]
aliases: ["Networking", "HTTP Client", "WebSocket", "ServerSocketChannel", "Selector", "NIO Networking"]
status: stable
updated: 2026-05-09
---

# Networking and HTTP Client

> [!summary] Goal
> Build network applications with Java's `java.net.http.HttpClient`, `WebSocket`, and NIO channels. Understand blocking vs non-blocking I/O, HTTP/2 support, and channel-based networking.

## Table of Contents

1. [HTTP Client](#http-client)
2. [WebSocket](#websocket)
3. [NIO Channels and Selectors](#nio-channels-and-selectors)
4. [Blocking vs Non-Blocking Comparison](#blocking-vs-non-blocking-comparison)
5. [Pitfalls](#pitfalls)

---

## HTTP Client

> [!info] HttpClient
> `java.net.http.HttpClient` (Java 11+) is a modern HTTP client supporting HTTP/1.1 and HTTP/2, both synchronous and asynchronous (via `CompletableFuture`). It replaces the legacy `HttpURLConnection` with a cleaner API, automatic connection pooling, and built-in request/response body handlers.

```java
import java.net.URI;
import java.net.http.*;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.concurrent.*;

// Create client (reuse across requests — connection pooling built-in)
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)       // Prefer HTTP/2
    .connectTimeout(Duration.ofSeconds(10))
    .build();

// Synchronous request
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Accept", "application/json")
    .GET()
    .build();

HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
System.out.println("Status: " + response.statusCode());
System.out.println("Body: " + response.body());

// POST with JSON body
String json = """
    {"name": "Alice", "email": "alice@example.com"}
    """;

HttpRequest postRequest = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(json))
    .build();

HttpResponse<String> postResponse = client.send(postRequest, BodyHandlers.ofString());

// Asynchronous request
CompletableFuture<HttpResponse<String>> future =
    client.sendAsync(request, BodyHandlers.ofString());
future.thenAccept(resp -> System.out.println(resp.body()));
```

### HTTP/2 features

```java
// HTTP/2 server push support
client.sendAsync(request, BodyHandlers.ofString())
    .thenAccept(response -> {
        response.previousResponse()  // For redirect chains
            .ifPresent(prev -> System.out.println("Redirected from: " + prev.uri()));
    });

// HTTP/2 connection detection
System.out.println("Version used: " + response.version());  // HTTP_2 or HTTP_1_1
```

### Connection pool and timeouts

```java
HttpClient client = HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(5))    // Timeout to establish connection
    .executor(Executors.newVirtualThreadPerTaskExecutor())  // With virtual threads
    .build();

// No per-request timeout is set by default!
// Use CompletableFuture or a custom HttpClient with timeout:
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .timeout(Duration.ofSeconds(30))          // Per-request timeout
    .GET()
    .build();
```

---

## WebSocket

```java
import java.net.http.WebSocket;
import java.util.concurrent.*;

WebSocket.Builder wsBuilder = client.newWebSocketBuilder();

WebSocket.Listener listener = new WebSocket.Listener() {
    @Override
    public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
        System.out.println("Received: " + data);
        webSocket.request(1);    // Request next message (flow control)
        return null;
    }

    @Override
    public void onOpen(WebSocket webSocket) {
        System.out.println("Connected");
        webSocket.sendText("Hello from Java!", true);
    }

    @Override
    public CompletionStage<?> onClose(WebSocket webSocket, int statusCode, String reason) {
        System.out.println("Closed: " + statusCode + " " + reason);
        return null;
    }

    @Override
    public void onError(WebSocket webSocket, Throwable error) {
        System.err.println("Error: " + error.getMessage());
    }
};

// Connect
CompletableFuture<WebSocket> wsFuture = wsBuilder
    .buildAsync(URI.create("wss://echo.websocket.org"), listener);
WebSocket ws = wsFuture.get();

// Send messages
ws.sendText("Hello!", true).get();
ws.sendClose(WebSocket.NORMAL_CLOSURE, "Done").get();
```

---

## NIO Channels and Selectors

> [!info] Channel and Selector
> NIO channels (`SocketChannel`, `ServerSocketChannel`) support non-blocking I/O. A `Selector` can monitor multiple channels for readability, writability, or acceptability — letting a single thread handle thousands of connections. This is the Java equivalent of `epoll`/`kqueue`/`select`.

```java
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.*;

public class NioServer {
    public static void main(String[] args) throws Exception {
        Selector selector = Selector.open();

        ServerSocketChannel serverChannel = ServerSocketChannel.open();
        serverChannel.bind(new InetSocketAddress(8080));
        serverChannel.configureBlocking(false);
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);
        
        System.out.println("Server listening on port 8080");

        while (true) {
            selector.select();                      // Block until events happen
            Set<SelectionKey> keys = selector.selectedKeys();
            Iterator<SelectionKey> iter = keys.iterator();

            while (iter.hasNext()) {
                SelectionKey key = iter.next();
                iter.remove();

                if (key.isAcceptable()) {
                    // New connection
                    ServerSocketChannel server = (ServerSocketChannel) key.channel();
                    SocketChannel client = server.accept();
                    client.configureBlocking(false);
                    client.register(selector, SelectionKey.OP_READ);
                    System.out.println("Accepted: " + client.getRemoteAddress());
                }

                if (key.isReadable()) {
                    // Data available
                    SocketChannel client = (SocketChannel) key.channel();
                    ByteBuffer buffer = ByteBuffer.allocate(1024);
                    int bytesRead = client.read(buffer);
                    
                    if (bytesRead == -1) {
                        client.close();                // Client closed connection
                    } else if (bytesRead > 0) {
                        buffer.flip();
                        byte[] data = new byte[buffer.limit()];
                        buffer.get(data);
                        String msg = new String(data);
                        System.out.println("Received: " + msg);
                        
                        // Echo back
                        ByteBuffer response = ByteBuffer.wrap(("Echo: " + msg).getBytes());
                        client.write(response);
                    }
                }
            }
        }
    }
}
```

### NIO Client

```java
SocketChannel channel = SocketChannel.open();
channel.connect(new InetSocketAddress("localhost", 8080));

ByteBuffer buffer = ByteBuffer.wrap("Hello from NIO!".getBytes());
channel.write(buffer);

buffer.clear();
channel.read(buffer);
buffer.flip();
System.out.println(new String(buffer.array(), 0, buffer.limit()));

channel.close();
```

---

## Blocking vs Non-Blocking Comparison

| Aspect | Blocking I/O (Socket, HttpClient sync) | Non-blocking (NIO Channels + Selector) |
|--------|:-------------------------------------:|:--------------------------------------:|
| **Threads per connection** | One per connection | One thread handles thousands |
| **Scalability** | Limited by threads | Limited by file descriptors |
| **Programming model** | Simple (sequential) | Complex (state machine) |
| **Latency** | Good | Good (no thread switching) |
| **Use case** | Low concurrency, simple | High concurrency, event-driven |
| **Virtual threads** | ✅ Works great (no blocking issue) | ⚠️ Less benefit (non-blocking is unnecessary) |

### When to use which

```java
// ✅ Use blocking I/O + virtual threads (simplest for most cases)
var executor = Executors.newVirtualThreadPerTaskExecutor();
for (String url : urls) {
    executor.submit(() -> {
        var resp = HttpClient.newHttpClient()
            .send(request, BodyHandlers.ofString());  // Blocks VT (fine)
        return resp.body();
    });
}

// ✅ Use NIO Selector for maximum performance (minimal threads)
// When you need thousands of simultaneous connections
// When you can't use virtual threads (older Java)
// When latency matters and you want zero-blocking threads
```

---

## Pitfalls

### Not closing HttpClient

`HttpClient` uses a connection pool with daemon threads. If you create a new `HttpClient` for every request, connections leak until GC. Create one client per application and reuse it. The client is thread-safe.

### Blocking on CompletableFuture in HttpClient

`response.get()` inside a `sendAsync` callback blocks the asynchronous thread. Use `thenAccept` / `thenApply` for non-blocking composition. `CompletableFuture` timeouts require Java 9+ `orTimeout()` or `completeOnTimeout()`.

### Selector starvation

If you spend too long handling one channel's data in a `Selector` loop, other channels starve. Offload data processing to another thread or a virtual thread. The selector should only read/write data quickly.

### HTTP/2 connection coalescing

HTTP/2 multiplexes multiple requests over one TCP connection. If a server is unreachable, all requests waiting on that connection are affected. Configure sensible timeouts.

---

> [!question]- Interview Questions
>
> **Q: How does the Java HttpClient compare to HttpURLConnection?**
> A: HttpClient (Java 11+) is a complete rewrite: supports HTTP/2, WebSocket, both sync and async APIs (CompletableFuture), automatic connection pooling, and cleaner request/response body handling with `BodyHandlers`. HttpURLConnection is the old API — blocking only, no HTTP/2, verbose. Always prefer HttpClient.
>
> **Q: How does NIO Selector work?**
> A: `Selector` monitors one or more `SelectableChannel` instances for events (connect, accept, read, write). `selector.select()` blocks until an event occurs. Each registered channel gets a `SelectionKey` indicating which operations are ready. A single thread can handle thousands of connections by looping through ready keys. Internally, it uses `epoll` on Linux, `kqueue` on macOS.
>
> **Q: When should you use non-blocking I/O vs blocking I/O with virtual threads?**
> A: With virtual threads (Java 21+), blocking I/O is cheap — each pending I/O operation unmounts the virtual thread from the carrier. For most applications, a simple blocking model with virtual threads is sufficient and far easier to program. Use NIO Selector for: (1) pre-Java 21, (2) when you need absolute minimum latency, (3) when you want to control buffering and I/O granularity explicitly.
>
> **Q: What is HTTP/2 multiplexing?**
> A: HTTP/2 allows multiple concurrent requests over a single TCP connection. The `HttpClient` maintains a connection pool and multiplexes requests automatically. This reduces connection overhead (TLS handshakes) and allows server push (the server can send resources before the client requests them). Check `response.version()` to confirm HTTP/2 was used.
>
> **Q: How do you handle WebSocket flow control in Java?**
> A: WebSocket.Listener uses reactive flow control via `onText()` returning a `CompletionStage` and `webSocket.request(1)`. After receiving a message, you must call `request(1)` to request the next message. Without this, the receiver stops reading. The number passed to `request()` controls how many pending messages are allowed.

---

## Cross-Links

- [[Java/03_Advanced/06_Virtual_Threads_and_Structured_Concurrency]] for virtual threads with HTTP
- [[Java/03_Advanced/01_CompletableFuture_and_Structured_Concurrency]] for async HTTP
- [[Java/02_Core/03_IO_NIO_and_Serialization]] for NIO buffers and channels
- [[Java/01_Foundations/04_Streams_Lambdas_and_Functional_Java]] for response body streaming
- [[C/03_Advanced/04_Socket_Programming]] for C socket-level comparison
