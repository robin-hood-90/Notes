---
tags: [rust, projects, async, worker, kafka, messaging, rdkafka, tokio]
aliases: ["Async Worker", "Kafka Consumer", "Rust Kafka"]
status: stable
updated: 2026-05-11
---

# Project: Async Worker with Kafka

> [!summary] Goal
> Build a resilient async Kafka consumer in Rust: message processing, graceful shutdown, error handling, consumer group management, and production observability.

## Architecture

```
my-worker/
├── Cargo.toml
├── src/
│   ├── main.rs              # Entry point, runtime setup, graceful shutdown
│   ├── config.rs            # Worker configuration from environment
│   ├── consumer.rs          # Kafka consumer loop with rebalance handling
│   ├── processor.rs         # Business logic for each message
│   ├── db.rs                # Database operations (sqlx)
│   ├── error.rs             # Worker error type
│   └── metrics.rs           # Metrics collection
└── tests/
    ├── integration.rs
    └── fixtures/
```

## Dependencies

```toml
[package]
name = "my-worker"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
rdkafka = { version = "0.37", features = ["cmake-build"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
thiserror = "2"
anyhow = "1"
uuid = { version = "1", features = ["v4", "serde"] }
metrics = "0.24"
metrics-exporter-prometheus = "0.16"
chrono = { version = "0.4", features = ["serde"] }
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres"] }
```

## Step 1: Configuration

```rust
// src/config.rs
pub struct Config {
    pub kafka_brokers: String,
    pub kafka_group_id: String,
    pub kafka_input_topic: String,
    pub kafka_output_topic: String,
    pub consumer_poll_interval_ms: u64,
    pub max_processing_retries: u32,
    pub database_url: String,
    pub metrics_port: u16,
}

impl Config {
    pub fn from_env() -> anyhow::Result<Self> {
        Ok(Self {
            kafka_brokers: std::env::var("KAFKA_BROKERS")
                .unwrap_or_else(|_| "localhost:9092".into()),
            kafka_group_id: std::env::var("KAFKA_GROUP_ID")
                .unwrap_or_else(|_| "my-worker".into()),
            kafka_input_topic: std::env::var("KAFKA_INPUT_TOPIC")
                .unwrap_or_else(|_| "input-events".into()),
            kafka_output_topic: std::env::var("KAFKA_OUTPUT_TOPIC")
                .unwrap_or_else(|_| "output-events".into()),
            consumer_poll_interval_ms: std::env::var("POLL_INTERVAL_MS")
                .ok().and_then(|s| s.parse().ok()).unwrap_or(100),
            max_processing_retries: std::env::var("MAX_RETRIES")
                .ok().and_then(|s| s.parse().ok()).unwrap_or(3),
            database_url: std::env::var("DATABASE_URL")
                .unwrap_or_else(|_| "postgres://postgres:postgres@localhost:5432/worker".into()),
            metrics_port: std::env::var("METRICS_PORT")
                .ok().and_then(|s| s.parse().ok()).unwrap_or(9000),
        })
    }
}
```

## Step 2: Error Types

```rust
// src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum WorkerError {
    #[error("Kafka error: {0}")]
    Kafka(#[from] rdkafka::error::KafkaError),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Processing error: {0}")]
    Processing(String),

    #[error("Max retries exceeded for message {key}")]
    MaxRetriesExceeded { key: String, reason: String },
}
```

## Step 3: Kafka Consumer with Graceful Shutdown

```rust
// src/consumer.rs
use rdkafka::{
    consumer::{Consumer, StreamConsumer},
    ClientConfig, Message,
};
use tokio::sync::watch;

use crate::{config::Config, error::WorkerError, processor};

pub async fn run_consumer(
    config: &Config,
    mut shutdown_rx: watch::Receiver<bool>,
) -> Result<(), WorkerError> {
    let consumer: StreamConsumer = ClientConfig::new()
        .set("bootstrap.servers", &config.kafka_brokers)
        .set("group.id", &config.kafka_group_id)
        .set("enable.auto.commit", "true")
        .set("auto.offset.reset", "earliest")
        .set("session.timeout.ms", "60000")
        .set("max.poll.interval.ms", "300000")
        .create()?;

    consumer.subscribe(&[&config.kafka_input_topic])?;

    tracing::info!("Kafka consumer started, subscribed to {}", config.kafka_input_topic);

    loop {
        tokio::select! {
            // Check for shutdown signal
            _ = shutdown_rx.changed() => {
                if *shutdown_rx.borrow() {
                    tracing::info!("Shutdown signal received, stopping consumer");
                    break;
                }
            }

            // Poll for messages
            msg = consumer.recv() => {
                match msg {
                    Ok(m) => {
                        let payload = m.payload().unwrap_or(&[]);
                        let key = m.key().unwrap_or(&[]);
                        let key_str = String::from_utf8_lossy(key).to_string();

                        tracing::debug!(key = %key_str, partition = m.partition(), offset = m.offset(), "Received message");

                        if let Err(e) = processor::process_message(payload).await {
                            tracing::error!(error = %e, key = %key_str, "Failed to process message");
                            metrics::counter!("worker.messages.failed", "reason" => format!("{e}")).increment(1);
                        } else {
                            metrics::counter!("worker.messages.processed").increment(1);
                        }
                    }
                    Err(e) => {
                        tracing::error!(error = %e, "Kafka receive error");
                        metrics::counter!("worker.consumer.errors").increment(1);
                    }
                }
            }
        }
    }

    tracing::info!("Consumer stopped gracefully");
    Ok(())
}
```

## Step 4: Message Processing

```rust
// src/processor.rs
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Deserialize)]
pub struct InputEvent {
    pub id: Uuid,
    pub event_type: String,
    pub payload: serde_json::Value,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize)]
pub struct OutputEvent {
    pub id: Uuid,
    pub original_id: Uuid,
    pub status: String,
    pub processed_at: chrono::DateTime<chrono::Utc>,
    pub result: serde_json::Value,
}

pub async fn process_message(payload: &[u8]) -> Result<(), crate::WorkerError> {
    let event: InputEvent = serde_json::from_slice(payload)?;

    if event.event_type.is_empty() {
        return Err(crate::WorkerError::Processing("Empty event type".into()));
    }

    // Simulate processing — replace with actual business logic
    let result = serde_json::json!({
        "processed": true,
        "original_event_type": event.event_type,
    });

    let output = OutputEvent {
        id: Uuid::new_v4(),
        original_id: event.id,
        status: "completed".into(),
        processed_at: chrono::Utc::now(),
        result,
    };

    tracing::info!(
        event_id = %event.id,
        event_type = %event.event_type,
        output_id = %output.id,
        "Message processed successfully"
    );

    // Write to database
    // db::insert_output(&output).await?;

    // Could also produce to output topic here
    // producer::send(&config.kafka_output_topic, &output).await?;

    Ok(())
}
```

## Step 5: Graceful Shutdown

```rust
// src/main.rs
use tokio::signal;
use tokio::sync::watch;

mod config;
mod consumer;
mod db;
mod error;
mod metrics;
mod processor;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("my_worker=info".parse()?),
        )
        .init();

    let config = config::Config::from_env()?;

    // Metrics server
    let metrics_handle = tokio::spawn(async move {
        metrics::serve_metrics(config::Config::from_env().unwrap().metrics_port).await;
    });

    // Shutdown channel
    let (shutdown_tx, shutdown_rx) = watch::channel(false);

    // Handle OS signals
    let shutdown_signal = async {
        signal::ctrl_c().await.expect("Failed to install SIGINT handler");
        tracing::info!("SIGINT received, starting graceful shutdown");
        shutdown_tx.send(true).ok();
    };

    // Run consumer
    tokio::select! {
        result = consumer::run_consumer(&config, shutdown_rx) => {
            if let Err(e) = result {
                tracing::error!(error = %e, "Consumer exited with error");
            }
        }
        _ = shutdown_signal => {}
    }

    tracing::info!("Worker shut down gracefully");
    Ok(())
}
```

## Step 6: Metrics

```rust
// src/metrics.rs
use metrics_exporter_prometheus::PrometheusBuilder;

pub async fn serve_metrics(port: u16) {
    let builder = PrometheusBuilder::new();
    builder
        .with_http_listener(([0, 0, 0, 0], port))
        .install()
        .expect("Failed to install metrics exporter");

    tracing::info!("Metrics server listening on port {port}");
    // Run forever — the http listener runs in the background
    std::future::pending::<()>().await;
}

// In consumer/processor, use:
// metrics::counter!("worker.messages.processed").increment(1);
// metrics::histogram!("worker.processing_time_ms", elapsed.as_millis() as f64);
```

## Step 7: Database Layer

```rust
// src/db.rs
use sqlx::PgPool;
use crate::processor::OutputEvent;

pub async fn insert_output(pool: &PgPool, event: &OutputEvent) -> Result<(), sqlx::Error> {
    sqlx::query(
        "INSERT INTO processed_events (id, original_id, status, processed_at, result) VALUES ($1, $2, $3, $4, $5)"
    )
    .bind(event.id)
    .bind(event.original_id)
    .bind(&event.status)
    .bind(event.processed_at)
    .bind(&event.result)
    .execute(pool)
    .await?;

    Ok(())
}
```

## Extension Ideas

- Add dead letter queue for failed messages
- Add batch processing for higher throughput
- Add transactional exactly-once processing
- Add consumer rebalance hooks for state management
- Add distributed tracing with OpenTelemetry
- Add health check endpoint for Kubernetes probes
- Add rate limiting per partition

---

## Cross-Links

- [[Rust/02_Core/04_Async_Await_Tokio_Basics]] for async primitives
- [[Rust/03_Advanced/17_Tracing_Logging_and_Observability]] for observability patterns
- [[Rust/04_Playbooks/03_Debug_Async_Deadlocks_and_Blocking]] for async debugging
- [[CICD/Kafka/01_Foundations/03_Producers_Deep_Dive]] for Kafka producers/consumers
