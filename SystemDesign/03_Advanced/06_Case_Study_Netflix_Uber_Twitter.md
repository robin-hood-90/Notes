---
tags: [system-design, advanced, case-study, netflix, uber, twitter, architecture]
aliases: ["Case Studies: Netflix, Uber, Twitter", "Netflix Architecture", "Uber Architecture", "Twitter Architecture"]
status: stable
updated: 2026-05-09
---

# Case Study: Netflix, Uber, Twitter

> [!summary] Goal
> Learn from real-world system designs — Netflix's microservice evolution and resilience engineering, Uber's dispatch and geo-spatial indexing, and Twitter's timeline fan-out and snowflake ID generation.

## Table of Contents

1. [Netflix](#netflix)
2. [Uber](#uber)
3. [Twitter](#twitter)
4. [Common Patterns Across All Three](#common-patterns-across-all-three)

---

## Netflix

### Evolution: Monolith → SOA → Microservices

```mermaid
flowchart LR
    A["2007: Monolithic DVD-by-mail"] -->|"2009: Cloud migration"| B["Monolith + Cloud"]
    B -->|"2011: SOA extraction"| C["~100 services"]
    C -->|"2015: Full microservices"| D["~700+ services"]
    D -->|"Current"| E["~1000+ services, 3+ AWS regions"]
```

### Key architectural decisions

| Decision | What they chose | Why |
|----------|---------------|-----|
| **API Gateway** | Zuul (now Zuul 2.0) — Netty-based, non-blocking | Routes requests to correct services, handles auth, rate limiting |
| **Service Mesh** | Eureka (service discovery), Ribbon (client-side load balancing), Hystrix (circuit breaker) | Evolved into their own OSS stack before Istio/Linkerd existed |
| **Resilience** | Hystrix Circuit Breaker, Bulkhead, Timeout per service | Prevents cascading failures; each dependency has its own thread pool |
| **Data** | Cassandra (AP, eventual consistency), EVCache (Memcached-based distributed cache) | High availability over strong consistency |
| **Multi-region** | Active-Active (3+ AWS regions) | All regions serve traffic; no idle capacity |
| **Observability** | Atlas (metrics), Spinnaker (CD), Chaos Monkey | "If it hurts, do it more often" — Netflix Engineering Culture |

### Netflix's Chaos Engineering

```mermaid
flowchart LR
    A["Chaos Monkey"] --> B["Randomly kills instances"]
    B --> C["Teams must build resilient services"]
    C --> D["Chaos Kong <br/>(simulates region failure)"]
    D --> E["Failure Injection Testing (FIT)"]
    E --> F["Game Days: scheduled chaos"]
    F --> B
```

| Tool | What it does | Lesson |
|------|-------------|--------|
| **Chaos Monkey** | Randomly terminates EC2 instances | Build systems that survive instance failure |
| **Chaos Kong** | Simulates an entire AWS region failure | Multi-region must be tested, not just documented |
| **FIT** | Injects latency/failures into service-to-service calls | Test resilience of each dependency independently |
| **Game Days** | Scheduled failure exercises with the on-call team | Practice makes incident response faster |

### Netflix's microservice architecture

```mermaid
flowchart TD
    C["Client (Smart TV, Mobile, Web)"] --> Z["Zuul API Gateway"]
    Z --> A["Authentication"]
    Z --> R["Recommendations"]
    Z --> S["Search"]
    Z --> N["Navigation"]
    Z --> M["Member Experience"]
    N --> N1["Catalog Service"]
    N --> N2["Rating Service"]
    N --> N3["History Service"]
    M --> M1["User Profile"]
    M --> M2["Billing"]
    M --> M3["Device Management"]
    R --> R1["Personalization Engine"]
    R --> R2["A/B Testing"]
    S --> S1["Elasticsearch"]
    S --> S2["Indexing Pipeline"]
```

---

## Uber

### Dispatch system architecture

```mermaid
flowchart TD
    R["Rider App"] --> D["Dispatch Service"]
    D --> G["Geospatial Index<br/>(QuadTree + H3 Grid)"]
    D --> P["Pricing Engine<br/>(Surge, Route)"]
    D --> M["Matching Engine"]
    D --> E["ETA Service<br/>(Routing + ML)"]
    G --> G1["Filter drivers near rider"]
    G --> G2["Score and rank"]
    P --> P1["Supply/Demand ratio"]
    P --> P2["Multiplier calculation"]
    E --> E1["Traffic prediction"]
    E --> E2["Driver routing"]
    M --> M1["Dispatch to top driver"]
    D --> Dr["Driver App"]
```

### Geospatial indexing

```text
Problem: Find nearby drivers efficiently in a city with millions of drivers.

Solution: Uber uses a combination of:
  1. H3 Hexagonal Grid — divides the world into hexagons of adjustable resolution
  2. Drivers are assigned to the hex cell they're in
  3. Query: find all occupied hex cells within a radius
  4. Retrieve drivers from those cells

Why H3 over QuadTree?
  - Hexagons have uniform distance between centers
  - No ambiguity at cell boundaries (all neighbors are equidistant)
  - Better for spatial queries and price regions

Previous approach: QuadTree with geohash
  - Drivers send location every 4 seconds via gRPC
  - Geohash reduces 2D → 1D for DB indexing
  - Redis sorted sets for real-time driver location per geohash
```

### Surge pricing mechanics

```mermaid
flowchart TD
    A["Real-time supply (available drivers)"] --> C["Supply/Demand ratio"]
    B["Real-time demand (ride requests)"] --> C
    C --> D{ratio < threshold?}
    D -->|"Yes"| E["Surge multiplier > 1.0"]
    D -->|"No"| F["Normal pricing (< 1.0)"]
    E --> G["Drivers incentivized to move to area"]
    G --> A
    E --> H["Riders may wait or pay more"]
    H --> B
```

### Microservice decomposition

| Service | Responsibility | Data store |
|---------|---------------|------------|
| **Dispatch** | Match rider with driver | Cassandra (trip state) |
| **Geospatial Index** | Track driver locations | Redis + H3 |
| **Pricing** | Surge calculation, fare estimation | Redis (counters) |
| **ETA** | Route computation, arrival time | Postgres + ML models |
| **Payment** | Process charges, payouts | Postgres (ledger) |
| **User** | Riders and drivers profiles | Schemaless (MySQL-based) |
| **Trip** | Ride history and state machine | Cassandra |

---

## Twitter

### Timeline generation: Fan-out on write (for regular users)

```mermaid
sequenceDiagram
    participant U as User
    participant TS as Tweet Service
    participant F as Fan-Out Service
    participant TL as Timeline Cache (Redis)
    participant DB as User Graph

    U->>TS: Post tweet
    TS->>TS: Store tweet
    TS->>F: New tweet event (userId, tweetId)
    F->>DB: Get followers of userId
    DB-->>F: [follower_1, follower_2, ..., follower_N]
    
    Note over F: If followers < 10,000: fan-out on write
    F->>TL: Insert tweetId into timeline of follower_1
    F->>TL: Insert tweetId into timeline of follower_2
    Note over F: ...for all followers
    
    F-->>TS: Fan-out complete
    TS-->>U: Tweet posted
```

### Timeline generation: Fan-out on read (for celebrities)

```mermaid
sequenceDiagram
    participant U as User
    participant TL as Timeline Service
    participant C as Celebrity Timeline (read)
    participant M as Merge Service
    participant T as Tweet Store

    U->>TL: GET /timeline
    TL->>C: Get own timeline (regular follows)
    TL->>M: Get celebrity tweets (fan-out on read)
    M->>T: Fetch recent tweets from celebrities user follows
    T-->>M: Celebrity tweets (recent, sorted)
    M-->>TL: Merged timeline (regular + celebrity)
    TL-->>U: Timeline response
```

### Snowflake ID generation

```mermaid
flowchart LR
    subgraph Snowflake["64-bit Snowflake ID"]
        SIGN["1 bit<br/>0 (unused)"]
        TS["41 bits<br/>Timestamp (ms)"]
        WID["10 bits<br/>Worker ID"]
        SEQ["12 bits<br/>Sequence"]
    end
```

| Field | Bits | Max value | Notes |
|-------|:----:|:---------:|-------|
| **Sign** | 1 | — | Always 0 (positive integer) |
| **Timestamp** | 41 | ~69 years | Milliseconds since custom epoch |
| **Worker ID** | 10 | 1024 | Datacenter (5 bits) + Server (5 bits) |
| **Sequence** | 12 | 4096 | Per-worker counter, resets every ms |

```text
Unique, time-ordered, 64-bit IDs without a central coordinator.
Each server generates 4096 IDs per millisecond = ~4M IDs/sec per server.

Twitter's custom epoch: 2010-11-04 (first tweet)

Other ID systems inspired by Snowflake:
  - Instagram: similar but uses logical shard ID instead of worker
  - Discord: 64-bit Snowflake variant
  - Sonyflake: 39-bit timestamp, 8-bit worker
```

---

## Common Patterns Across All Three

| Pattern | Netflix | Uber | Twitter |
|---------|---------|------|---------|
| **API Gateway** | Zuul | API Gateway | — |
| **Service discovery** | Eureka | Internal DNS | Finagle |
| **Circuit breaker** | Hystrix | Internal library | — |
| **Distributed caching** | EVCache (Memcached) | Redis | Twemcache, Redis |
| **Async event processing** | Kafka | Kafka | Kafka (event bus) |
| **Polyglot persistence** | Cassandra + EVCache + S3 | Cassandra + Redis + Postgres | MySQL + Redis + Manhattan |
| **Active-active multi-region** | 3+ AWS regions | Multiple regions | Multiple datacenters |
| **Canary / A/B testing** | Zuul + Spinnaker | Internal platform | Experimentation platform |

---

## Cross-Links

- [[SystemDesign/02_Core/06_Microservice_Architecture]] for service decomposition patterns
- [[SystemDesign/03_Advanced/03_Resilience_Patterns]] for circuit breaker and bulkhead patterns
- [[SystemDesign/03_Advanced/05_Distributed_Transactions_and_Consensus]] for consensus and leader election
- [[SystemDesign/02_Core/01_Caching_Strategies]] for timeline cache design
- [[SystemDesign/03_Advanced/01_Multi_Region_Architecture]] for active-active multi-region
