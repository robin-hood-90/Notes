---
tags: [networking, project, http-proxy, tunnel, curl, python, connection-pooling]
aliases: ["HTTP Proxy", "Forward Proxy", "CONNECT Tunnel", "Proxy Server"]
status: stable
updated: 2026-05-09
---

# Project: Build a Simple HTTP Forward Proxy

> [!summary] Goal
> Build an HTTP forward proxy that handles both plain HTTP and HTTPS (CONNECT) tunneling. Understand how proxies work, how connection pooling improves performance, and how to verify with `curl -x`.

## Table of Contents

1. [How an HTTP Proxy Works](#how-an-http-proxy-works)
2. [Python Implementation](#python-implementation)
3. [Testing with curl](#testing-with-curl)
4. [Pitfalls](#pitfalls)

---

## How an HTTP Proxy Works

```mermaid
sequenceDiagram
    participant C as curl -x proxy:8080
    participant P as Proxy
    participant S as Target Server

    Note over C,P,S: HTTP request
    C->>P: GET http://example.com/ HTTP/1.1
    P->>S: GET / HTTP/1.1 (forwarded)
    S-->>P: HTTP response
    P-->>C: HTTP response

    Note over C,P,S: HTTPS request (CONNECT)
    C->>P: CONNECT example.com:443 HTTP/1.1
    Note over P: Proxy establishes TCP to example.com:443
    P-->>C: 200 Connection Established
    Note over P: Proxy blind-relays bytes between C and S
    C-->>P: TLS handshake data (encrypted)
    P-->>S: TLS handshake data (forwarded)
    P-->>C: TLS response (forwarded)
    Note over C,S: Tunnel established — proxy can't inspect
```

---

## Python Implementation

```python
import socket
import threading
import sys
import select

BUFFER_SIZE = 8192
PROXY_PORT = 8888


def handle_client(client_sock):
    """Handle one client connection."""
    # Read the initial request line and headers
    request = b""
    while b"\r\n\r\n" not in request:
        chunk = client_sock.recv(BUFFER_SIZE)
        if not chunk:
            client_sock.close()
            return
        request += chunk

    first_line = request.split(b"\r\n")[0].decode()
    parts = first_line.split()

    if len(parts) < 3:
        client_sock.close()
        return

    method, url = parts[0], parts[1]

    if method == "CONNECT":
        # HTTPS tunnel
        host, port = url.split(":")
        port = int(port)
        handle_connect(client_sock, host, port)
    else:
        # Plain HTTP
        # Extract host from URL or Host header
        if url.startswith("http://"):
            rest = url[7:]
            host = rest.split("/")[0]
            path = "/" + "/".join(rest.split("/")[1:])
            port = 80
        else:
            client_sock.close()
            return

        handle_http(client_sock, host, port, method, path, request)


def handle_http(client_sock, host, port, method, path, request):
    """Forward plain HTTP request."""
    try:
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect((host, port))

        # Rewrite request: change path and remove proxy headers
        request = request.replace(
            f"http://{host}:{port}{path}".encode(),
            path.encode(), 1
        )

        # Remove Proxy-* headers
        lines = request.split(b"\r\n")
        filtered = []
        for line in lines:
            if not line.lower().startswith(b"proxy-"):
                filtered.append(line)
        request = b"\r\n".join(filtered)

        target.sendall(request)

        # Forward response back
        while True:
            data = target.recv(BUFFER_SIZE)
            if not data:
                break
            client_sock.sendall(data)

        target.close()
    except Exception as e:
        print(f"HTTP error: {e}")
    finally:
        client_sock.close()


def handle_connect(client_sock, host, port):
    """Handle CONNECT tunnel (HTTPS)."""
    try:
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect((host, port))
        client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        # Bidirectional forwarding
        sockets = [client_sock, target]
        while True:
            r, _, _ = select.select(sockets, [], [], 60)
            if not r:
                break
            for sock in r:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    client_sock.close()
                    target.close()
                    return
                if sock is client_sock:
                    target.sendall(data)
                else:
                    client_sock.sendall(data)
    except Exception as e:
        print(f"CONNECT error: {e}")
    finally:
        client_sock.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PROXY_PORT))
    server.listen(100)
    print(f"Proxy server listening on port {PROXY_PORT}")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
```

---

## Testing with curl

```bash
# Start the proxy
python3 proxy.py

# Test plain HTTP
curl -x http://localhost:8888 -v http://example.com

# Test HTTPS (CONNECT tunnel)
curl -x http://localhost:8888 -v https://example.com

# Verify the proxy is being used
# If the proxy is working, curl outputs:
# * Uses proxy env variable no_proxy
# * Connected to localhost (::1) port 8888

# Without proxy:
curl -v https://example.com   # Direct connection

# With proxy header inspection
curl -x http://localhost:8888 -v http://httpbin.org/headers

# Performance test through proxy
time curl -x http://localhost:8888 http://example.com
time curl http://example.com                    # Direct comparison
```

---

## Pitfalls

### CONNECT without 200 response

The client sends `CONNECT example.com:443 HTTP/1.1`. The proxy MUST respond with `200 Connection Established` before starting to relay. If the proxy sends a different response (or doesn't respond), the client drops the connection.

### Forgetting Proxy-* headers

HTTP forward proxies should strip `Proxy-*` headers (Proxy-Authorization, Proxy-Connection) before forwarding the request to the target. These headers are meant for the proxy, not the target server.

### Thread-per-connection model

The threaded model works for hundreds of concurrent connections but doesn't scale to thousands. For higher performance, use an event loop (asyncio in Python, epoll in C) with non-blocking I/O and connection pooling.

---

## Cross-Links

- [[Networking/02_Core/04_Proxies_NAT_and_Firewalls]] for proxy types and CONNECT method
- [[Networking/02_Core/02_HTTP_1_1_HTTP_2_HTTP_3]] for HTTP request/response structure
- [[Networking/03_Advanced/06_Troubleshooting_Toolkit]] for curl -x testing
- [[Networking/01_Foundations/04_TCP_Deep_Dive]] for TCP stream handling
- [[C/05_Projects/02_HTTP_Server_Minimal]] for HTTP server in C
