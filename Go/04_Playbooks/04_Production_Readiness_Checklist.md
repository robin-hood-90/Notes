---
tags: [go, playbook, production, slog, expvar, health-check, graceful-shutdown, observability]
aliases: ["Production Readiness", "slog", "expvar", "Health Checks", "Go Production Checklist"]
status: stable
updated: 2026-05-11
---

# Playbook: Production Readiness Checklist

> [!summary] Goal
> Ensure Go services are production-ready: structured logging with `slog`, runtime metrics with `expvar`, HTTP health endpoints, graceful shutdown, observability, and a comprehensive deployment checklist.

## Structured Logging with `slog`

```go
import "log/slog"

// slog (Go 1.21+) provides structured, leveled logging with attribute pairs.
// It's the standard library replacement for logrus, zap, and zerolog.

// Production setup:
slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level:     slog.LevelInfo,
    AddSource: true,  // Include file:line
})))

// Usage:
slog.Info("server starting",
    "port", 8080,
    "env", "production",
    "version", version,
)
slog.Error("request failed",
    "error", err,
    "request_id", reqID,
    "path", r.URL.Path,
)

// Log levels: Debug (-4), Info (0), Warn (4), Error (8)
// Custom levels:
const LevelSecurity = slog.Level(12) // Higher than Error

// Handler customization — replace attribute keys:
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        if a.Key == slog.TimeKey {
            a.Key = "timestamp"
        }
        if a.Key == slog.MessageKey {
            a.Key = "message"
        }
        return a
    },
})

// Logging with context:
slog.LogAttrs(ctx, slog.LevelInfo, "request processed",
    slog.Group("request",
        slog.String("method", r.Method),
        slog.String("path", r.URL.Path),
        slog.Int("status", 200),
    ),
    slog.Duration("duration", time.Since(start)),
)
```

## Runtime Metrics with `expvar`

```go
import "expvar"

// expvar publishes metrics as JSON at GET /debug/vars.

var (
    requestsTotal   = expvar.NewInt("requests_total")
    activeRequests  = expvar.NewInt("active_requests")
    responseTime    = expvar.NewFloat("response_time_avg_ms")
    errorCount      = expvar.NewInt("errors_total")
    requestSize     = expvar.NewInt("request_bytes_total")
)

// Update in HTTP handler:
func handler(w http.ResponseWriter, r *http.Request) {
    requestsTotal.Add(1)
    activeRequests.Add(1)
    start := time.Now()
    defer func() {
        activeRequests.Add(-1)
        ms := float64(time.Since(start).Microseconds()) / 1000.0
        // Exponential moving average (simplified):
        prev := responseTime.Value()
        responseTime.Set(prev*0.95 + ms*0.05)
    }()
    // ... handler logic ...
}

// Custom metrics (e.g., HTTP status code breakdown):
expvar.Publish("http_codes", expvar.Func(func() any {
    return map[string]int64{
        "200": status200.Value(),
        "404": status404.Value(),
        "500": status500.Value(),
    }
}))
```

## Health and Readiness Endpoints

```go
mux := http.NewServeMux()

// Liveness: is the process alive?
mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"alive"}`))
})

// Readiness: can we serve traffic?
mux.HandleFunc("GET /readyz", func(w http.ResponseWriter, r *http.Request) {
    // Check critical dependencies:
    if err := db.PingContext(r.Context()); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{
            "status": "not ready",
            "error":  err.Error(),
        })
        return
    }
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{"status": "ready"})
})
```

## Production Deployment Checklist

```text
[ ] Graceful shutdown (SIGTERM → Shutdown(ctx))
[ ] slog JSON handler configured (AddSource=true)
[ ] Request timeout (server.ReadTimeout, WriteTimeout)
[ ] Client timeouts (http.Client.Timeout, transport timeouts)
[ ] Connection pool limits (MaxIdleConns, MaxIdleConnsPerHost)
[ ] Rate limiting / throttling (semaphore.Weighted)
[ ] Health endpoint (GET /healthz) and readiness (GET /readyz)
[ ] pprof endpoint registered (net/http/pprof)
[ ] Metrics endpoint (/debug/vars or Prometheus)
[ ] GODEBUG sanity checks (gctrace=1 for debugging)
[ ] Race-free code verified (-go vet -race in CI)
[ ] goleak in tests to catch goroutine leaks
[ ] Error handling: all errors wrapped (%w) and logged
[ ] Context propagated through all layers
[ ] Timeouts from env vars, not hardcoded
[ ] Version endpoint (/debug/version or similar)
[ ] CORS, XSS, CSP headers configured
[ ] TLS config: MinVersion=1.2, secure ciphers
```

---

## Cross-Links

- [[Go/02_Core/04_NetHTTP_Server_Middleware_and_Clients]] for shutdown, server config, TLS
- [[Go/03_Advanced/04_Profiling_pprof_and_Tracing]] for pprof endpoint
- [[Go/02_Core/06_Database_SQL_and_Migrations]] for DB health checks
- [[Go/02_Core/01_Context_Cancellation_and_Timeouts]] for context patterns
- [[Go/03_Advanced/02_GC_Escape_Analysis_and_Performance]] for GC tuning flags
