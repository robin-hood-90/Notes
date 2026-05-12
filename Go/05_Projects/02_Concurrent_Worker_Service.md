---
tags: [go, projects, worker, concurrency, errgroup, queue]
aliases: ["Concurrent Worker Project", "Worker Pool", "Error Group"]
status: stable
updated: 2026-05-03
---

# Project: Concurrent Worker Service

> [!summary] Goal
> Build a concurrent worker pool with `errgroup`, bounded queue, retry with backoff, and Prometheus metrics.

## Project Structure

```
worker/
├── cmd/worker/main.go
├── internal/
│   ├── worker/pool.go
│   ├── worker/job.go
│   └── worker/metrics.go
├── go.mod
└── Dockerfile
```

## main.go

```go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "worker/internal/worker"
)

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    pool := worker.NewPool(ctx, worker.Config{
        NumWorkers: 5,
        QueueSize:  100,
        MaxRetries: 3,
    })

    go func() {
        slog.Info("starting worker pool", "workers", 5)
        if err := pool.Start(); err != nil {
            slog.Error("pool error", "error", err)
            cancel()
        }
    }()

    // Metrics endpoint
    go func() {
        http.Handle("/metrics", pool.MetricsHandler())
        slog.Info("metrics on :9090")
        http.ListenAndServe(":9090", nil)
    }()

    // Signal handling
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    slog.Info("shutting down...")
    pool.Stop()
}
```

## worker/job.go

```go
package worker

import "context"

type Job struct {
    ID      string
    Payload string
}

type Result struct {
    JobID string
    Error error
}
```

## worker/pool.go

```go
package worker

import (
    "context"
    "fmt"
    "log/slog"
    "net/http"
    "sync/atomic"
    "time"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "golang.org/x/sync/errgroup"
)

type Config struct {
    NumWorkers int
    QueueSize  int
    MaxRetries int
}

type Pool struct {
    ctx      context.Context
    cfg      Config
    jobs     chan Job
    results  chan Result
    running  atomic.Bool
    processed atomic.Int64
    failed    atomic.Int64
}

func NewPool(ctx context.Context, cfg Config) *Pool {
    return &Pool{
        ctx:     ctx,
        cfg:     cfg,
        jobs:    make(chan Job, cfg.QueueSize),
        results: make(chan Result, cfg.QueueSize),
    }
}

func (p *Pool) Start() error {
    p.running.Store(true)
    defer p.running.Store(false)

    g, ctx := errgroup.WithContext(p.ctx)

    for i := 0; i < p.cfg.NumWorkers; i++ {
        g.Go(func() error {
            return p.worker(ctx)
        })
    }

    // Collect results
    go func() {
        for r := range p.results {
            if r.Error != nil {
                slog.Error("job failed", "job_id", r.JobID, "error", r.Error)
            }
        }
    }()

    return g.Wait()
}

func (p *Pool) worker(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case job, ok := <-p.jobs:
            if !ok {
                return nil
            }
            p.processWithRetry(ctx, job)
        }
    }
}

func (p *Pool) processWithRetry(ctx context.Context, job Job) {
    var lastErr error
    for attempt := 0; attempt <= p.cfg.MaxRetries; attempt++ {
        if attempt > 0 {
            backoff := time.Duration(attempt*attempt) * 100 * time.Millisecond
            select {
            case <-ctx.Done():
                return
            case <-time.After(backoff):
            }
        }
        if err := p.process(ctx, job); err != nil {
            lastErr = err
            slog.Warn("retrying", "job_id", job.ID, "attempt", attempt+1)
            continue
        }
        p.processed.Add(1)
        p.results <- Result{JobID: job.ID}
        return
    }
    p.failed.Add(1)
    p.results <- Result{JobID: job.ID, Error: fmt.Errorf("all retries failed: %w", lastErr)}
}

func (p *Pool) process(ctx context.Context, job Job) error {
    // Simulate work
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(100 * time.Millisecond):
        return nil
    }
}

func (p *Pool) Submit(job Job) {
    p.jobs <- job
}

func (p *Pool) Stop() {
    close(p.jobs)
}

func (p *Pool) MetricsHandler() http.Handler {
    return promhttp.Handler()
}
```

---

## Cross-Links

- [[Go/02_Core/02_Concurrency_Patterns_WorkerPools_FanInOut]] for concurrency patterns
- [[Go/02_Core/01_Context_Cancellation_and_Timeouts]] for context patterns
- [[Go/04_Playbooks/04_Production_Readiness_Checklist]] for metrics and shutdown
