---
tags: [python, core, networking, http, sockets, requests, httpx, websockets, grpc]
aliases: ["Network Programming", "HTTP", "sockets", "requests", "httpx", "websockets", "gRPC"]
status: stable
updated: 2026-05-29
---

# Network Programming and HTTP

> [!summary] Goal
> Master Python's networking stack — low-level `socket` programming, the `requests` library for HTTP, `httpx` for async clients, `websockets`, and a gRPC overview.

## Table of Contents

1. [Socket Programming](#socket-programming)
2. [requests](#requests)
3. [httpx](#httpx)
4. [websockets](#websockets)
5. [gRPC Overview](#grpc-overview)
6. [Pitfalls](#pitfalls)

---

## Socket Programming

> [!info] Sockets are the lowest-level networking API
> Python's `socket` module wraps the OS socket API (BSD sockets). You rarely use this directly in application code, but it's essential for understanding how higher-level libraries work.

```python
import socket

# TCP Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 8080))
server.listen(5)
server.setblocking(False)       # Non-blocking mode

# TCP Client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 8080))
client.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
response = client.recv(4096)
client.close()

# UDP — connectionless
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.sendto(b"data", ("localhost", 8081))
data, addr = udp_sock.recvfrom(1024)
```

### selectors — multiplexing I/O

```python
import selectors
import socket

sel = selectors.DefaultSelector()

def accept(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn):
    data = conn.recv(1024)
    if data:
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\nOK")
    else:
        sel.unregister(conn)
        conn.close()

server = socket.socket()
server.bind(("localhost", 8080))
server.listen(5)
server.setblocking(False)
sel.register(server, selectors.EVENT_READ, accept)

while True:
    for key, _ in sel.select():
        callback = key.data
        callback(key.fileobj)
```

---

## requests

> [!info] The de-facto standard HTTP client for Python
> `requests` provides a clean, human-readable API. Use it for sync HTTP calls.

```python
import requests

# GET
response = requests.get(
    "https://api.github.com/users/alice",
    headers={"Accept": "application/json"},
    params={"page": 1, "per_page": 10},
    timeout=10,
)
response.status_code          # 200
response.json()               # Parsed JSON dict
response.text                 # Raw text
response.headers              # Response headers

# POST
response = requests.post(
    "https://api.example.com/users",
    json={"name": "Alice", "email": "alice@example.com"},
    headers={"Authorization": "Bearer token123"},
    timeout=10,
)

# Session — connection pooling, cookie persistence
session = requests.Session()
session.headers.update({"User-Agent": "myapp/1.0"})

# Retry adapter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    backoff_factor=1,          # 1s, 2s, 4s
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# File upload
with open("photo.jpg", "rb") as f:
    response = requests.post("https://api.example.com/upload",
                             files={"file": f})

# Streaming response
response = requests.get("https://api.example.com/large-stream", stream=True)
for chunk in response.iter_content(chunk_size=8192):
    process(chunk)
```

> [!tip] Always use `Session()` for multiple requests
> Sessions reuse TCP connections (connection pooling), avoid renegotiating TLS, and let you set default headers.

---

## httpx

> [!info] `httpx` supports both sync and async, plus HTTP/2
> It has a similar API to `requests` but adds async, HTTP/2, and better connection management.

```python
import httpx

# Sync
with httpx.Client() as client:
    response = client.get("https://api.example.com", timeout=30)
    response.json()

# Async
async def fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()

# HTTP/2
client = httpx.Client(http2=True)

# Connection pooling
limits = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
)
client = httpx.Client(limits=limits)

# Timeout configuration
timeout = httpx.Timeout(30.0, connect=5.0, read=10.0, write=10.0)
client = httpx.Client(timeout=timeout)

# Async with gather
async def fetch_many(urls):
    async with httpx.AsyncClient() as client:
        async def get(url):
            resp = await client.get(url)
            return resp.json()
        return await asyncio.gather(*[get(u) for u in urls])
```

### httpx vs requests

```python
# requests
session = requests.Session()
resp = session.get("https://api.example.com", timeout=10)

# httpx sync
client = httpx.Client()
resp = client.get("https://api.example.com", timeout=10)

# httpx async
async with httpx.AsyncClient() as client:
    resp = await client.get("https://api.example.com", timeout=10)
```

| Feature | `requests` | `httpx` |
|---------|:----------:|:-------:|
| Sync/Async | Sync only | Both |
| HTTP/2 | No | ✅ Yes |
| Connection pooling | ✅ (Session) | ✅ (Client) |
| Type hints | Limited | ✅ Full |
| Performance | Good | Better (HTTP/2, keepalive) |

---

## websockets

```python
import asyncio
import websockets

# Server
async def handler(websocket):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()     # Run forever

# Client
async def client():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send("Hello!")
        response = await ws.recv()
        print(response)            # "Echo: Hello!"
```

> [!tip] WebSocket vs HTTP
> WebSocket maintains a persistent TCP connection for full-duplex communication. Use it for real-time apps (chat, live updates, gaming). HTTP is request-response; WebSocket is message-oriented and bidirectional.

---

## gRPC Overview

> [!info] gRPC is a high-performance RPC framework using Protocol Buffers
> It's language-agnostic, supports streaming, and uses HTTP/2. In Python, use `grpcio`.

```protobuf
# proto/user_service.proto
service UserService {
    rpc GetUser (UserRequest) returns (UserResponse);
    rpc ListUsers (Empty) returns (stream UserResponse);
}

message UserRequest { int32 id = 1; }
message UserResponse { int32 id = 1; string name = 2; string email = 3; }
```

```python
# Server
import grpc
from concurrent import futures

class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_service_pb2.UserResponse(id=request.id, name="Alice")

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
user_service_pb2_grpc.add_UserServiceServicer_to_server(
    UserServiceServicer(), server
)
server.add_insecure_port("[::]:50051")
server.start()
server.wait_for_termination()

# Client
channel = grpc.insecure_channel("localhost:50051")
stub = user_service_pb2_grpc.UserServiceStub(channel)
response = stub.GetUser(user_service_pb2.UserRequest(id=42))
print(response.name)           # "Alice"
```

> [!tip] When to use gRPC
> - Microservice-to-microservice communication
> - Streaming data (logs, events, real-time feeds)
> - Polyglot environments (different languages)
> - When you need strict API contracts (protobuf)

---

## Pitfalls

### Not setting timeouts

```python
# ❌ Can hang forever
response = requests.get("https://slow.example.com")
requests.get("https://slow.example.com", timeout=10)  # ✅ 10s total
requests.get("https://slow.example.com", timeout=(5, 10))  # connect=5s, read=10s
```

### Not closing sessions/client

```python
# ❌ Resource leak (unclosed connections)
session = requests.Session()
response = session.get("https://api.example.com")

# ✅ Context manager
with requests.Session() as session:
    response = session.get("https://api.example.com")
```

### Connection pool exhaustion

```python
# Creating a new connection for every request is slow and leaks
# Always reuse sessions/clients
```

### Ignoring HTTP error codes

```python
response = requests.get("https://api.example.com/user/999")
if response.status_code == 404:        # Always check!
    handle_not_found()
response.raise_for_status()             # Or raise on 4xx/5xx
```

### Socket blocking without timeout

```python
sock = socket.socket()
sock.settimeout(5)                      # ✅ Always set a timeout
sock.connect(("example.com", 80))
```

---

> [!question]- Interview Questions
>
> **Q: What's the difference between `requests` and `httpx`?**
> A: `requests` is the mature, stable HTTP client — sync only, HTTP/1.1. `httpx` is newer, supports both sync and async, HTTP/2, and has better type hints. For new projects, consider `httpx` if you need async or HTTP/2. For sync-only and maximum ecosystem compatibility, use `requests`.
>
> **Q: How do you handle retries in HTTP clients?**
> A: With `requests`, use `HTTPAdapter` + `Retry` to configure backoff, status codes to retry on, and total attempts. With `httpx`, use `Transport` with `retries`. Always use exponential backoff and jitter to avoid thundering herd.
>
> **Q: When would you use WebSockets over HTTP?**
> A: WebSockets maintain a persistent, bidirectional connection. Use them for real-time apps (chat, live stock tickers, collaborative editing, gaming). HTTP is request-response; WebSocket is pub-sub. For most API calls, HTTP is simpler and more appropriate.

---

## Cross-Links

- [[Python/02_Core/04_Web_Scraping]] for HTTP-based data extraction
- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for HTTP server-side
- [[Python/01_Foundations/11_Async_Python_Basics]] for async fundamentals
- [[Python/02_Core/02_Concurrency_Parallelism]] for threading and connection pools
