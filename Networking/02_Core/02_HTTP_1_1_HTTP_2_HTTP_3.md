---
tags: [networking, core, http, https, http2, http3, quic, curl, status-codes, rest]
aliases: ["HTTP", "HTTPS", "HTTP/1.1", "HTTP/2", "HTTP/3", "QUIC", "REST API"]
status: stable
updated: 2026-05-09
---

# HTTP: Versions, Methods, Status Codes, and Headers

> [!summary] Goal
> Master HTTP — the foundation protocol of the web. Understand HTTP/1.1, HTTP/2, and HTTP/3, all methods, status codes, headers, and how to debug HTTP with curl and other tools.

## Table of Contents

1. [HTTP Request/Response Structure](#http-request-response-structure)
2. [HTTP Methods](#http-methods)
3. [Status Codes](#status-codes)
4. [HTTP Headers](#http-headers)
5. [HTTP/1.1 vs HTTP/2 vs HTTP/3](#http-1-1-vs-http-2-vs-http-3)
6. [Verification Commands](#verification-commands)
7. [Pitfalls](#pitfalls)

---

## HTTP Request/Response Structure

> [!info] HTTP (Hypertext Transfer Protocol)
> HTTP is a request-response protocol. The client sends a **request** (method, path, headers, optional body). The server returns a **response** (status code, headers, body). HTTP is stateless — each request is independent. Modern HTTP/2 and HTTP/3 are fully compatible with HTTP/1.1 semantics but use different transport framing.

```text
HTTP Request:
  GET /index.html HTTP/1.1
  Host: www.example.com
  User-Agent: curl/8.0
  Accept: */*

HTTP Response:
  HTTP/1.1 200 OK
  Content-Type: text/html; charset=UTF-8
  Content-Length: 1234
  Date: Mon, 09 May 2026 12:00:00 GMT
  
  <!DOCTYPE html>
  <html>... (1234 bytes)
```

---

## HTTP Methods

> [!info] HTTP methods
> HTTP methods define the action to perform on a resource. Idempotent methods (GET, PUT, DELETE) produce the same result no matter how many times they're called. Safe methods (GET, HEAD, OPTIONS) don't modify the resource. POST and PATCH are not idempotent.

| Method | Idempotent | Safe | Has body | Purpose |
|:------:|:----------:|:----:|:--------:|---------|
| **GET** | ✅ | ✅ | ❌ | Retrieve a resource |
| **HEAD** | ✅ | ✅ | ❌ | Like GET but returns only headers |
| **POST** | ❌ | ❌ | ✅ | Create a new resource |
| **PUT** | ✅ | ❌ | ✅ | Replace a resource entirely |
| **PATCH** | ❌ | ❌ | ✅ | Partial update to a resource |
| **DELETE** | ✅ | ❌ | May have | Delete a resource |
| **OPTIONS** | ✅ | ✅ | ❌ | Discover allowed methods for a resource |
| **TRACE** | ✅ | ✅ | ❌ | Echo request (diagnostic) |
| **CONNECT** | ❌ | ❌ | ❌ | Establish a tunnel (used by HTTPS proxies) |

```bash
# Testing methods with curl
curl -I https://example.com                # HEAD request
curl -X GET https://api.example.com/items  # GET
curl -X POST -d '{"name":"Alice"}' -H "Content-Type: application/json" https://api.example.com/items
curl -X PUT -d '{"name":"Alice Updated"}' https://api.example.com/items/1
curl -X PATCH -d '{"name":"Alice"}' https://api.example.com/items/1
curl -X DELETE https://api.example.com/items/1
curl -X OPTIONS https://example.com        # Shows Allow header
```

---

## Status Codes

> [!info] HTTP status codes
> Status codes are 3-digit numbers indicating the result of the request. 1xx = informational, 2xx = success, 3xx = redirection, 4xx = client error, 5xx = server error.

### 1xx — Informational

| Code | Meaning | When |
|:----:|---------|------|
| 100 | Continue | Client should continue sending body |
| 101 | Switching Protocols | WebSocket upgrade |
| 102 | Processing | Server is processing (still going, not stuck) |

### 2xx — Success

| Code | Meaning | When |
|:----:|---------|------|
| **200** | **OK** | Request succeeded |
| 201 | Created | Resource was created (POST) |
| 202 | Accepted | Request accepted but not yet processed (async) |
| 204 | No Content | Success, no body (DELETE) |
| 206 | Partial Content | Range request (partial download, video streaming) |

### 3xx — Redirection

| Code | Meaning | When |
|:----:|---------|------|
| **301** | **Moved Permanently** | Resource moved, change bookmarks |
| **302** | **Found** | Temporary redirect, don't change bookmarks |
| 303 | See Other | Redirect to GET after POST (PRG pattern) |
| 304 | Not Modified | Cached resource is still valid (ETag/If-Modified-Since) |
| 307 | Temporary Redirect | Like 302 but preserves HTTP method |
| 308 | Permanent Redirect | Like 301 but preserves HTTP method |

### 4xx — Client Error

| Code | Meaning | When |
|:----:|---------|------|
| **400** | **Bad Request** | Malformed request syntax |
| **401** | **Unauthorized** | Authentication required |
| **403** | **Forbidden** | Authenticated but not authorized |
| **404** | **Not Found** | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 406 | Not Acceptable | Can't produce requested content type |
| 408 | Request Timeout | Client didn't send request in time |
| 409 | Conflict | Resource state conflicts (version mismatch) |
| **429** | **Too Many Requests** | Rate limited |
| 451 | Unavailable For Legal Reasons | Blocked by legal demand |

### 5xx — Server Error

| Code | Meaning | When |
|:----:|---------|------|
| **500** | **Internal Server Error** | Generic server failure |
| 501 | Not Implemented | Server doesn't support this method |
| 502 | Bad Gateway | Upstream server returned error |
| **503** | **Service Unavailable** | Server overloaded or down for maintenance |
| 504 | Gateway Timeout | Upstream server didn't respond in time |
| 505 | HTTP Version Not Supported | Server doesn't support this HTTP version |

```bash
# Test status codes
curl -I https://example.com/nonexistent    # 404
curl -I -X POST https://example.com/static  # 405 (static files can't be POSTed)
curl -w "%{http_code}" -o /dev/null -s https://example.com  # Get status code only
```

---

## HTTP Headers

> [!info] HTTP headers
> Headers carry metadata about the request or response. They control caching, authentication, content negotiation, CORS, and more. Headers are case-insensitive, `Name: Value` format.

### Request headers

| Header | Example | Purpose |
|--------|---------|---------|
| `Host` | `Host: example.com` | Target host (required in HTTP/1.1) |
| `Authorization` | `Authorization: Bearer <token>` | Authentication credentials |
| `Content-Type` | `Content-Type: application/json` | Media type of request body |
| `Accept` | `Accept: text/html, application/json` | Response formats the client can handle |
| `User-Agent` | `User-Agent: curl/8.0` | Client identification |
| `Referer` | `Referer: https://google.com` | Previous page (origin of request) |
| `Cookie` | `Cookie: session_id=abc123` | Stored session data |
| `Cache-Control` | `Cache-Control: no-cache` | Caching directives |
| `If-None-Match` | `If-None-Match: "abc123"` | Conditional request (ETag) |
| `Origin` | `Origin: https://example.com` | Origin of request (CORS) |

### Response headers

| Header | Example | Purpose |
|--------|---------|---------|
| `Content-Type` | `Content-Type: text/html; charset=utf-8` | Media type of response body |
| `Content-Length` | `Content-Length: 1234` | Body size in bytes |
| `Set-Cookie` | `Set-Cookie: session_id=abc123; HttpOnly` | Set a cookie |
| `Cache-Control` | `Cache-Control: public, max-age=3600` | Caching policy |
| `ETag` | `ETag: "abc123"` | Resource version identifier |
| `Last-Modified` | `Last-Modified: Mon, 09 May 2026 12:00:00 GMT` | Last modification time |
| `Location` | `Location: /new-path` | Redirect target URL |
| `Access-Control-Allow-Origin` | `Access-Control-Allow-Origin: *` | CORS policy |
| `WWW-Authenticate` | `WWW-Authenticate: Bearer realm="api"` | Authentication challenge |

```bash
# Inspect headers
curl -I https://example.com                       # All response headers
curl -v https://example.com                       # Request + response headers
curl -H "Authorization: Bearer mytoken" https://api.example.com  # Custom request header
curl -H "Accept: application/json" https://api.example.com       # Request JSON
```

---

## HTTP/1.1 vs HTTP/2 vs HTTP/3

> [!info] HTTP evolution
> **HTTP/1.1** (1997): Text-based, one request per connection (fixed by pipelining, partially). Headers are uncompressed. **HTTP/2** (2015): Binary framing, multiplexed streams, header compression (HPACK), server push. Still uses TCP. **HTTP/3** (2022): Uses QUIC (over UDP), solves TCP head-of-line blocking, 0-RTT connection setup, connection migration.

```mermaid
flowchart TD
    subgraph HTTP11["HTTP/1.1 — Sequential"]
        T1_1["Request 1"] -->|"wait"| T1_1R["Response 1"]
        T1_1R -->|"then"| T1_2["Request 2"]
        T1_2 -->|"wait"| T1_2R["Response 2"]
    end
    subgraph HTTP2["HTTP/2 — Multiplexed"]
        T2_1["Request 1"]
        T2_2["Request 2"]
        T2_3["Request 3"]
        note right of T2_1: All in one TCP connection
        T2_1R["Response 1"]
        T2_2R["Response 2"]
        T2_3R["Response 3"]
        T2_1 --> T2_1R
        T2_2 --> T2_2R
        T2_3 --> T2_3R
    end
```

### Version comparison

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---------|:--------:|:------:|:------:|
| **Transport** | TCP | TCP | QUIC (UDP) |
| **Framing** | Text | Binary | Binary |
| **Multiplexing** | ❌ (pipelining is broken) | ✅ (multiple streams per connection) | ✅ |
| **Header compression** | ❌ | ✅ (HPACK) | ✅ (QPACK) |
| **Server push** | ❌ | ✅ | ✅ |
| **Head-of-line blocking** | Yes (request-level) | Yes (TCP-level) | No |
| **Connection setup** | 2 RTT (TCP + TLS) | 2 RTT | 0-1 RTT |
| **Connection migration** | ❌ | ❌ | ✅ |
| **Encryption** | Optional (TLS or plain) | De facto mandatory | ✅ Mandatory |

```bash
# Test HTTP version support
curl -v --http1.1 https://example.com    # Force HTTP/1.1
curl -v --http2 https://example.com      # Force HTTP/2 via upgrade
curl -v --http2-prior-knowledge https://example.com  # HTTP/2 without upgrade
curl --http3 https://example.com         # HTTP/3 (if curl supports it)
nghttp -u https://example.com            # HTTP/2 with detailed frame output
h2load -n 1000 -c 10 https://example.com # HTTP/2 load testing

# Check which version was used
curl -v https://example.com 2>&1 | grep "ALPN"
# * ALPN: server accepted h2 (HTTP/2 was negotiated)
# * ALPN: server accepted http/1.1 (HTTP/1.1 was negotiated)
```

---

## Verification Commands

```bash
# Basic
curl -I https://example.com                    # Headers only
curl -v https://example.com                   # Full request/response details
curl -w "\n%{http_code}\n" -o /dev/null -s https://example.com  # Status code only

# Timing breakdown (-w format)
curl -w "
  time_namelookup:  %{time_namelookup}s
  time_connect:     %{time_connect}s
  time_appconnect:  %{time_appconnect}s (TLS)
  time_starttransfer: %{time_starttransfer}s
  time_total:       %{time_total}s
  speed_download:   %{speed_download}B/s
" -o /dev/null -s https://example.com

# Check HTTP/2 frames
nghttp -su https://nghttp2.org               # HTTP/2 frame details
nghttp -an https://nghttp2.org               # HTTP/2 without download

# Check HTTP/3
curl --http3 -I https://cloudflare.com        # HTTP/3 if available

# Server info
curl -I https://example.com | grep -i server  # Server software
curl -I https://example.com | grep -i x-powered-by  # Framework info

# Redirect chain
curl -IL https://example.com                 # Follow redirects, show each step

# Windows
Invoke-WebRequest -Uri https://example.com -Method GET
Invoke-RestMethod -Uri https://api.example.com
```

---

## Pitfalls

### Assuming HTTP/2 or HTTP/3 is always faster

HTTP/2 multiplexing helps when loading many resources (typical web page). For a single API call, HTTP/1.1 with connection reuse is comparable. HTTP/3 helps most on lossy networks (mobile, cellular) where head-of-line blocking on TCP hurts. On a clean datacenter link, HTTP/1.1+keepalive may be fastest.

### Not checking for redirect chains

A single `curl -I` may show a 301. The redirect may point to another host that 301s again. Multiple redirects add latency. Use `curl -IL` to follow the full chain. Browsers limit redirects to 20. If you're adding a redirect, make sure it's a single hop.

### Ignoring the Host header

In HTTP/1.1, the `Host` header is mandatory. Virtual hosting (multiple domains on one server) relies on it. Without `Host: example.com`, the server may return the wrong site or a 400 Bad Request. curl adds it automatically; custom code must include it.

### Content-Length vs Transfer-Encoding: chunked

If both are present, `Transfer-Encoding: chunked` takes precedence. Chunked encoding is used when the content length isn't known in advance (dynamic responses). `curl -v` shows both. The final chunk is zero-length, followed by optional trailers.

---

> [!question]- Interview Questions
>
> **Q: What's the difference between HTTP/1.1 and HTTP/2?**
> A: HTTP/2 is binary (not text), supports multiplexing (multiple requests share one TCP connection), compresses headers (HPACK), and allows server push. HTTP/1.1 processes one request at a time per connection (pipelining was broken). HTTP/2 multiplexing solves head-of-line blocking at the application layer.
>
> **Q: What does HTTP 429 mean and how should you handle it?**
> A: 429 Too Many Requests means you've exceeded the rate limit. The response includes a `Retry-After` header with the wait time. The client should stop making requests and wait. For bulk operations, implement exponential backoff with jitter.
>
> **Q: What's the difference between 301 and 302 redirects?**
> A: 301 Moved Permanently — the resource has permanently moved; browsers cache this and change bookmarks. 302 Found — temporary redirect; browsers use the original URL for future requests. With 301, POST may become GET; 307/308 preserve the method.
>
> **Q: How does HTTP/3 (QUIC) improve on HTTP/2?**
> A: HTTP/3 replaces TCP with QUIC over UDP. This eliminates TCP head-of-line blocking (one lost packet blocks all HTTP/2 streams). QUIC has 0-RTT handshake with session resumption, built-in encryption, connection migration (survives IP changes), and faster loss recovery.
>
> **Q: What is a CORS preflight request?**
> A: For cross-origin requests with non-simple methods or custom headers, the browser sends an OPTIONS preflight first. The server must respond with `Access-Control-Allow-Origin` and `Access-Control-Allow-Methods`. Without this, the browser blocks the actual request.

---

## Cross-Links

- [[Networking/01_Foundations/04_TCP_Deep_Dive]] for TCP transport of HTTP/1.1 and HTTP/2
- [[Networking/01_Foundations/05_UDP_and_QUIC]] for QUIC transport of HTTP/3
- [[Networking/02_Core/03_TLS_and_Certificates]] for HTTPS encryption
- [[Networking/02_Core/06_CDN_Caching_and_Web_Performance]] for caching headers
- [[Networking/04_Playbooks/03_Debug_HTTP_Timeouts_and_Retries]] for HTTP troubleshooting
