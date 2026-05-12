---
tags: [kafka, messaging, moc]
aliases: ["Kafka MOC"]
status: stable
updated: 2026-05-11
---

# Kafka

> [!summary] Scope
> 23 files covering Kafka architecture, delivery semantics, partitioning, consumer groups, serialization, storage internals, Connect, Streams, security, monitoring, KRaft, K8s operations, and exactly-once pipelines.

## Foundations

1. [[CICD/Kafka/01_Foundations/01_Kafka_Architecture_and_Core_Concepts]] — brokers, topics, partitions, ZooKeeper vs KRaft, throughput model
2. [[CICD/Kafka/01_Foundations/02_Topics_Partitions_Offsets]] — segments, index files, timeindex, LEO, HW, ISR, offset types
3. [[CICD/Kafka/01_Foundations/03_Producers_Deep_Dive]] — send path, RecordAccumulator, batching, compression, acks, idempotence
4. [[CICD/Kafka/01_Foundations/04_Consumers_Deep_Dive]] — poll loop, offset commit, rebalance protocol, cooperative rebalance, static membership
5. [[CICD/Kafka/01_Foundations/05_Messages_Serialization_and_Schema_Registry]] — Avro/Protobuf/JSON, Schema Registry, compatibility modes

## Core

1. [[CICD/Kafka/02_Core/01_Delivery_Semantics_and_Exactly_Once]] — at-most/at-least/exactly-once, idempotent producer, transactions, exactly-once consumer
2. [[CICD/Kafka/02_Core/02_Partitioning_Strategies]] — sticky/round-robin/custom partitioner, hot-spot avoidance, ordering vs parallelism
3. [[CICD/Kafka/02_Core/03_Consumer_Group_Rebalancing]] — eager vs cooperative, assignment strategies, static membership, minimizing impact
4. [[CICD/Kafka/02_Core/04_Performance_Tuning]] — broker/producer/consumer tuning, OS/network tuning, benchmarking

## Advanced

1. [[CICD/Kafka/03_Advanced/A00_Storage_and_Replication_Internals]] — log segments, index/timeindex, ISR, HW, LSO, leader epoch, compaction, zero-copy
2. [[CICD/Kafka/03_Advanced/A01_Kafka_Connect]] — source/sink connectors, converters, SMT, REST API, distributed mode, fault tolerance
3. [[CICD/Kafka/03_Advanced/A02_Kafka_Streams]] — KStream/KTable/GlobalKTable, state stores, windowing, joins, EOS, Processor API
4. [[CICD/Kafka/03_Advanced/A03_Security]] — SSL/TLS, SASL (PLAIN/SCRAM/GSSAPI/OAUTH), ACLs, mTLS, secrets management
5. [[CICD/Kafka/03_Advanced/A04_Monitoring_and_Observability]] — JMX metrics, Prometheus/Grafana stack, lag monitoring, OpenTelemetry
6. [[CICD/Kafka/03_Advanced/A05_Migration_and_Upgrades]] — rolling upgrades, protocol version, cluster expansion, partition reassignment
7. [[CICD/Kafka/03_Advanced/A06_KRaft_and_ZooKeeper_Removal]] — Raft metadata quorum, combined vs dedicated controllers, ZK-to-KRaft migration
8. [[CICD/Kafka/03_Advanced/A07_Kafka_on_Kubernetes]] — Strimzi operator, StatefulSets, persistent storage, Cruise Control, networking

## Playbooks

1. [[CICD/Kafka/04_Playbooks/01_Troubleshoot_Consumer_Lag]] — diagnose and fix lag spikes, connectivity, OOM, disk full, LEADER_NOT_AVAILABLE
2. [[CICD/Kafka/04_Playbooks/02_Production_Hardening]] — OS/JVM tuning, broker config, security checklist, backup and DR, MirrorMaker 2
3. [[CICD/Kafka/04_Playbooks/03_Performance_Optimization_Playbook]] — benchmarking, producer/consumer/broker optimization, bottleneck analysis
4. [[CICD/Kafka/04_Playbooks/04_Migration_Playbook]] — ZK-to-KRaft, cluster-to-cluster, topic migration, consumer re-pointing

## Projects

1. [[CICD/Kafka/05_Projects/01_Exactly_Once_Pipeline_With_Idempotent_Consumers]] — Kafka Streams EOS pipeline with dedup transformer, idempotent consumer with PostgreSQL dedup table

## Cross-Links

- [[SystemDesign/00_MOC/00_SystemDesign_MOC]] — system design fundamentals
- [[CICD/Kubernetes/00_MOC/00_Kubernetes_MOC]] — K8s fundamentals for Kafka-on-K8s
- [[CICD/Kafka/00_MOC/../02_Core/01_Delivery_Semantics_and_Exactly_Once]] — Spring Boot Kafka integration

## References

- https://kafka.apache.org/documentation/
- https://strimzi.io/documentation/
- https://docs.confluent.io/platform/current/schema-registry/index.html
