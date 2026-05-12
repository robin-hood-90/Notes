---
tags: [kubernetes, k8s, advanced, service-mesh, istio, linkerd, cilium, consul, gateway-api, ingress, mTLS]
aliases: ["Service Mesh", "Istio", "Linkerd", "Cilium Service Mesh", "Consul", "Gateway API", "Envoy"]
status: stable
updated: 2026-05-11
---

# Service Mesh and Gateway API

> [!summary] Goal
> Master service mesh: Istio (Envoy sidecar, VirtualService, DestinationRule, mTLS, canary, telemetry), Linkerd (linkerd-proxy, zero-config mTLS, ServiceProfile), Cilium Service Mesh (eBPF-based, no sidecar, Hubble), Consul (intentions, partitions). Understand Gateway API (GatewayClass, Gateway, HTTPRoute, TCPRoute, GRPCRoute) and how it compares to Ingress v1 and service mesh.

## Table of Contents

1. [Service Mesh Comparison](#service-mesh-comparison)
2. [Istio Deep Dive](#istio-deep-dive)
3. [Linkerd, Cilium, and Consul](#linkerd-cilium-and-consul)
4. [Gateway API](#gateway-api)

---

## Service Mesh Comparison

> [!info] Service mesh
> A service mesh manages service-to-service communication at the infrastructure layer. It provides: mTLS (encrypted, authenticated service-to-service), traffic routing (canary, blue/green, mirroring), observability (metrics, traces, logs), and policy (rate limiting, circuit breaking, access control).

| Feature | Istio | Linkerd | Cilium | Consul |
|:--------|:-----:|:-------:|:------:|:------:|
| **Sidecar** | Envoy (Go/C++) | linkerd-proxy (Rust) | No sidecar (eBPF) | Envoy |
| **Architecture** | Control plane (Pilot, Citadel, Galley) + sidecar | Control plane (destination, identity, proxy-injector) + sidecar | eBPF on each node | Control plane (server, client) + sidecar |
| **mTLS** | Auto (mutual TLS) | Auto (zero-conf) | Auto (eBPF) | Auto (intentions) |
| **Performance** | Moderate (Envoy) | Fast (Rust proxy) | Fastest (no sidecar) | Moderate (Envoy) |
| **Observability** | Prometheus, Grafana, Kiali, Jaeger | Prometheus, Grafana, Jaeger | Hubble (flow-based) | Prometheus, Grafana, HCP |
| **eBPF** | No | No | Yes (native) | No |
| **Complexity** | High | Medium | Medium | High |
| **Multi-cluster** | Yes (primary-remote) | Yes (multi-cluster) | Yes (cluster mesh) | Yes (admin partitions) |

---

## Istio Deep Dive

> [!info] Istio components
> **Pilot** — manages Envoy configuration (listeners, clusters, routes, endpoints). **Citadel** — manages certificates and mTLS. **Galley** — validates and distributes configuration. **Envoy sidecar** — intercepts all inbound/outbound traffic for the pod.

```yaml
# VirtualService: traffic routing rules
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
spec:
  hosts:
    - payment-service
  http:
    - match:
        - headers:
            version:
              exact: v2
      route:
        - destination:
            host: payment-service
            subset: v2
    - route:
        - destination:
            host: payment-service
            subset: v1

# DestinationRule: traffic policies per version
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service-dest
spec:
  host: payment-service
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL       # Require mTLS for all traffic
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
    outlierDetection:           # Circuit breaker
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 60s
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2

# Gateway: ingress traffic (unlike Ingress, Istio Gateway operates at L4/L5)
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: payment-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: payment-tls-cert
      hosts:
        - api.example.com
```

### Istio canary

```bash
# Canary deployment with Istio:
# 1. Deploy v2 (version: v2, replicas: 1)
# 2. VirtualService sends 10% to v2:
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  hosts:
    - payment-service
  http:
    - match:
        - headers:
            version:
              exact: v2
      route:
        - destination:
            host: payment-service
            subset: v2
      weight: 10                 # Only 10% of traffic
    - route:
        - destination:
            host: payment-service
            subset: v1
      weight: 90
EOF
```

---

## Linkerd, Cilium, and Consul

### Linkerd

```yaml
# Linkerd — the "simplest" service mesh
# Install: linkerd install | kubectl apply -f -
# Data plane: linkerd-proxy (Rust-based Envoy alternative)
# Control plane: destination, identity, proxy-injector

# ServiceProfile: per-route metrics (similar to VirtualService)
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: payment-service.default.svc.cluster.local
spec:
  routes:
    - condition:
        method: POST
        pathRegex: /api/payments
      name: POST /api/payments
      isRetryable: true
      timeout: 2s
```

### Cilium Service Mesh

```yaml
# Cilium uses eBPF — no sidecar, no Envoy.
# Each node runs Cilium agent (eBPF programs loaded into kernel)
# Hubble provides flow visibility
# CiliumNetworkPolicy — L7-aware policies without sidecar

apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: payment-service-policy
spec:
  endpointSelector:
    matchLabels:
      app: payment-service
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: api-gateway
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: POST
                path: "/api/payments"
```

---

## Gateway API

> [!info] Gateway API
> Gateway API is the evolution of Ingress. It separates concerns: **Infrastructure provider** creates GatewayClass → **Platform operator** creates Gateway → **Application developer** creates HTTPRoute. Supports TCP, TLS, gRPC, and cross-namespace routing.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: eg
spec:
  controllerName: gateway.envoyproxy.io/gatewayclass-controller
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  gatewayClassName: eg
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      tls:
        mode: Terminate
        certificateRefs:
          - name: my-tls-cert
      allowedRoutes:
        namespaces:
          from: All
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: payment-route
spec:
  parentRefs:
    - name: my-gateway
  hostnames:
    - api.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api/
      backendRefs:
        - name: payment-service
          port: 8080
          weight: 90
        - name: payment-service-canary
          port: 8080
          weight: 10
```

### Gateway API vs Ingress vs Service Mesh

```text
Feature                Ingress v1     Gateway API     Istio / Linkerd
──────────────────────────────────────────────────────────────────────
L7 routing             Yes            Yes             Yes
TLS termination        Yes            Yes             Yes
Path-based routing     Yes            Yes             Yes
Header-based routing   No             Yes             Yes
TCP/UDP routing        No (use nginx) Yes (TCPRoute)  Yes
Cross-namespace        No             Yes (RefGrant)  Yes
mTLS                   No             No              Yes
Circuit breaking       No             No              Yes
Traffic mirroring      No             No              Yes
```

---

## Cross-Links

- [[CICD/Kubernetes/02_Core/02_Ingress_and_Service_Types]] for Ingress baseline
- [[CICD/Kubernetes/03_Advanced/04_NetworkPolicies_and_Pod_Security]] for network security
- [[CICD/Kubernetes/04_Playbooks/03_GitOps_with_ArgoCD_and_Flux]] for GitOps with service mesh
- [[CICD/Kubernetes/03_Advanced/06_CRDs_and_Operators]] for Istio operator install
