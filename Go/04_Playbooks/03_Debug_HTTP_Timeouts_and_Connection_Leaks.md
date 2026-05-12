---
tags: [go, playbook, http, timeouts, connection-leaks, httptrace, transport, h2]
aliases: ["Debug HTTP Timeouts", "Connection Leaks", "httptrace", "HTTP Debugging", "HTTP/2 Leaks"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug HTTP Timeouts and Connection Leaks

> [!summary] Goal
> Diagnose HTTP client/server timeouts and connection leaks: use `httptrace.ClientTrace` for connection lifecycle events, monitor `http.Transport` connection pool, handle HTTP/2 connection stalls, and identify common leak patterns.

## httptrace.ClientTrace — Full Event Sequence

```go
import "net/http/httptrace"

// The event sequence for a single HTTP/1.1 request:
//   GetConn → DNSStart → DNSDone → ConnectStart → ConnectDone
//     → TLSHandshakeStart → TLSHandshakeDone → WroteHeaders
//     → WroteRequest → GotFirstResponseByte → Body read

// Missing events indicate where the request is stuck:
//   Stuck at DNS → DNS server issue
//   Stuck at Connect → firewall, no route, port closed
//   Stuck at TLS → cert validation, TLS version mismatch
//   Stuck at WroteHeaders → server not reading
//   Stuck at GotFirstResponseByte → server processing request

trace := &httptrace.ClientTrace{
    GetConn: func(hostPort string) {
        log.Printf("connecting to %s", hostPort)
    },
    GotConn: func(info httptrace.GotConnInfo) {
        log.Printf("got conn (reused=%v, wasIdle=%v, idleTime=%v)",
            info.Reused, info.WasIdle, info.IdleTime)
        // If Reused=false frequently → connection pool is too small
        // If WasIdle=false → connections aren't being kept alive
    },
    ConnectStart: func(network, addr string) {
        log.Printf("dialing %s %s", network, addr)
    },
    ConnectDone: func(network, addr string, err error) {
        if err != nil { log.Printf("dial failed: %v", err) }
    },
    TLSHandshakeDone: func(state tls.ConnectionState, err error) {
        log.Printf("TLS done (version=%d)", state.Version)
        // tls.VersionTLS12 = 772, tls.VersionTLS13 = 772
    },
    WroteRequest: func(info httptrace.WroteRequestInfo) {
        if info.Err != nil { log.Printf("write error: %v", info.Err) }
    },
    GotFirstResponseByte: func() {
        log.Printf("first byte received")
    },
}
```

## Connection Pool Monitoring

```go
// The http.Transport manages a pool of idle connections.
// Leak: when resp.Body is not closed, the connection is NOT returned to the pool.

// Monitor the transport:
type TransportMetrics struct {
    Idle            int32 // runtime.ReadMemStats doesn't expose this
    InFlight        int32 // Not directly accessible from Transport
}

// To count in-flight requests, wrap the transport:
var activeRequests int32

countingTransport := &http.Transport{
    MaxIdleConns:    100,
    IdleConnTimeout: 90 * time.Second,
}

wrapped := roundTripperFunc(func(req *http.Request) (*http.Response, error) {
    atomic.AddInt32(&activeRequests, 1)
    resp, err := countingTransport.RoundTrip(req)
    atomic.AddInt32(&activeRequests, -1)
    // Also track connections: CountingConn for tracking open connections
    return resp, err
})

// GODEBUG=http2debug=2 enables HTTP/2 frame logging:
// GODEUBG=http2debug=2 ./program
// Shows: SETTINGS, HEADERS, DATA, RST_STREAM frames.
```

## Common Leak Patterns

```go
// Pattern 1: Response body not closed
resp, _ := http.Get("https://example.com")
// defer resp.Body.Close() is MISSING
// → connection not returned to pool → eventually exhausted

// Pattern 2: Response body not fully drained
resp, _ := http.Get("https://example.com")
defer resp.Body.Close()
_, _ = io.Copy(io.Discard, resp.Body) // Must drain before closing!
// Or: io.CopyN(ioutil.Discard, resp.Body, resp.ContentLength)

// Pattern 3: Not using a transport with MaxIdleConnsPerHost
client := &http.Client{
    Transport: &http.Transport{
        MaxIdleConnsPerHost: 10, // Default is 2! Very low for high-traffic services.
        MaxIdleConns:        100,
    },
}
```

---

## Cross-Links

- [[Go/02_Core/04_NetHTTP_Server_Middleware_and_Clients]] for HTTP client/server config
- [[Go/02_Core/01_Context_Cancellation_and_Timeouts]] for request context timeouts
- [[Go/04_Playbooks/04_Production_Readiness_Checklist]] for production config
- [[Go/04_Playbooks/01_Debug_Goroutine_Leaks_and_Deadlocks]] for goroutine leaks
