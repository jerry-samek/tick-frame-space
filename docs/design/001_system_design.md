### Overview

This document specifies a formal system design for an event‑driven, ledger‑centric universe platform.  
**Goal:** provide a single, uniform API and behavior across optional hierarchical layers (atomic, planetary, solar, galactic, universal) while allowing each layer to use different storage backends and scale independently.  
**Key principles:** append‑only commits as causal checkpoints; entities publish tick events with a single unified scalar **activity**; layers are adapters that implement the same contract; upper layers consume only committed logs from lower layers.

---

### Architecture

#### Logical components

- **Entity Microservice**
    - Simulates entity tick evolution in tick time.
    - Emits `entity.ticks` and accepts control commands.
    - Maintains local ephemeral state and optional local storage.

- **Event Bus**
    - Kafka topics for `entity.ticks`, `entity.commands`, `commit.entries`.
    - Partitioned by spatial shard id for local ordering.

- **Commit Engine**
    - Accumulates tick events per region/shard.
    - Decides commit cadence using pluggable strategies.
    - Persists commits via Storage Adapter and publishes `commit.entries`.

- **Storage Adapter**
    - Abstract interface for commit persistence and query.
    - Implementations: RocksDB/SQLite, Postgres, Scylla/Cassandra, ClickHouse, object store archive.

- **Reconstruction Service**
    - Builds gamma projections from committed entries on demand.
    - Caches region tiles and serves `/gamma` queries.

- **Admin and Orchestration**
    - Control commit policies, replays, forks, and monitoring.

#### Layer model

- **Layer as Adapter**
    - Each layer runs the same services and exposes the same API.
    - Only the Storage Adapter and resource sizing differ.
    - Layers are optional and added when scale or semantics require them.

- **Interlayer contract**
    - Lower layers publish `commit.entries`.
    - Upper layers consume lower layer `commit.entries` as input events.
    - Upper layers never read raw lower layer ticks.

---

### Data Model and Events

#### Unified event schemas

- **entity.ticks** (Key = `entityId`)
  ```json
  {
    "entityId":"E123",
    "tickId":12345,
    "x":42,
    "y":19,
    "activity":0.12,
    "jitter":0.007,
    "meta":{},
    "timestamp":"2026-01-29T19:21:00Z"
  }
  ```

- **entity.commands**
  ```json
  { "entityId":"E123", "cmd":"setActivity", "params":{"value":0.0,"rampTicks":100}, "timestamp":"..." }
  ```

- **commit.entries**
  ```json
  {
    "commitId":"C-0001",
    "layer":"planetary",
    "epochStart":1000,
    "epochEnd":1020,
    "entries":[
      {"region":"r1","weight":12.3,"activity_mean":0.45,"activity_var":0.02}
    ],
    "metadata":{}
  }
  ```

#### Database schema pattern

- **commits**
    - `commit_id UUID PK`, `layer TEXT`, `epoch_start BIGINT`, `epoch_end BIGINT`, `created_at TIMESTAMPTZ`, `summary JSONB`

- **commit_entries**
    - `id BIGSERIAL PK`, `commit_id UUID FK`, `region_id TEXT`, `weight DOUBLE PRECISION`, `activity_mean DOUBLE PRECISION`, `activity_var DOUBLE PRECISION`, `entity_refs JSONB`, `created_at TIMESTAMPTZ`

- **entity_state**
    - `entity_id TEXT PK`, `last_tick BIGINT`, `activity DOUBLE PRECISION`, `activity_history JSONB`, `metadata JSONB`

**Storage strategy**
- Keep recent commits hot in DB; archive older commits to object store as compressed batches.
- Use spatial region ids and Kafka partitioning keyed by region for ordering and locality.

---

### APIs and Contracts

#### Uniform API surface

All layers implement the same API and semantics.

| Endpoint | Method | Purpose |
|---|---:|---|
| `/entity/{id}/command` | POST | Control entity activity and lifecycle |
| `/entity/{id}/state` | GET | Read last known local state |
| `/commit/force` | POST | Force immediate commit for shard or region |
| `/commit/{commitId}` | GET | Fetch commit payload |
| `/gamma/current` | GET | Projection for region at current commit |
| `/gamma/commit/{commitId}` | GET | Historical projection slice |

#### API semantics

- **Activity semantics**: `activity` is the single scalar controlling coupling to substrate. `activity = 0` means decoupled; higher values increase contribution.
- **Commit semantics**: commits are atomic, append‑only, idempotent. `commit_id` is canonical.
- **Eventual consistency**: entities act on the last committed gamma for their layer. Upper layers may lag.
- **Error model**: 4xx for client errors, 5xx for transient server errors. Retryable semantics documented for idempotent operations.

#### Storage Adapter interface

Methods every adapter must implement:

- `persistCommit(commitId, layer, epochStart, epochEnd, entries, metadata)`
- `queryCommit(commitId)`
- `queryCommitsByRegion(regionId, range)`
- `readProjectionTile(regionId, commitId?)`
- `archiveCommits(range)`
- `restoreCommits(archivePointer)`

Adapters must guarantee idempotent upserts keyed by `commit_id`.

---

### Commit Engine and Algorithms

#### Accumulator model

- **Accumulator** keyed by `region` or spatial shard.
- Each tick contributes `contribution = baseWeight * f(activity)` to accumulator.
- Track `activity_mean` and `activity_var` per region.

#### Weight functions

- **Linear:** `f(activity) = activity`
- **Nonlinear:** `f(activity) = α·activity + β·activity^2`
- **Soft floor:** `f(activity) = max(activity, ε)` for slow leaks

#### Commit decision strategies

- **Fixed interval:** commit every `COMMIT_INTERVAL` ticks.
- **Adaptive threshold:** commit when `accumulator.size > N` or `activity_mean > T_threshold` or `variance > V_threshold`.
- **Hybrid:** minimum interval plus event thresholds.

#### Atomic commit flow

```ts
// Commit Engine pseudocode
onIncomingTicks(events):
  for ev of events:
    let w = BASE_WEIGHT * weightFn(ev.activity)
    accumulator.add(ev.region, w)
    accumulator.recordActivity(ev.region, ev.activity)

if shouldCommit(tickCount):
  commitId = uuid()
  entries = accumulator.aggregateRegions()
  storageAdapter.persistCommit(commitId, layer, epochStart, epochEnd, entries, metadata)
  publishKafka("commit.entries", {commitId, layer, entries, metadata})
  accumulator.clear()
```

#### Idempotency and atomicity

- Use `commit_id` unique constraint in DB.
- Use Kafka transactions when publishing `commit.entries` and writing DB records.
- Use leader election for active commit engine per shard to avoid double commits.

#### Activity dynamics and thermal exchange

- Optionally compute region activity exchange at commit time: regionActivity ← weighted average of entity activities.
- Apply diffusion to neighbor regions or to entity activity on next tick to model heat flow.
- Provide API hooks for custom thermal plugins while preserving identical external behavior.

---

### Operations Deployment and Observability

#### Deployment model

- **Single codebase, multiple configs**: same binaries for all layers; configure storage adapter and resource sizing via environment.
- **Shard placement**: partition by spatial shard id; co‑locate entity microservices with local storage for atomic scale.
- **Leader election**: use Kafka consumer groups or distributed lock for commit engine leadership per shard.

#### Scaling and hotspots

- **Scale horizontally** by adding shard instances.
- **Hotspot mitigation**: dynamic re‑sharding, region splitting, backpressure to entity producers, accumulator spill to RocksDB.
- **Layer addition**: add planetary/solar/galactic layers by deploying same service configured with appropriate storage adapter and Kafka subscriptions.

#### Retention and archival

- Keep recent commits hot; archive older commits to object store with compressed batches and index pointers.
- Archive policy configurable by `activity` and age: low activity commits archived aggressively.

#### Observability and SLOs

- **Metrics**: commit latency, accumulator size, tick throughput, Kafka consumer lag, activity histogram, commit size.
- **Tracing**: trace event → commit → projection update across services.
- **Alerts**: accumulator growth, commit failures, Kafka lag thresholds.
- **SLO examples**: commit latency p95 < X ms for atomic layer; reconstruction latency p95 < Y ms for planetary layer.

#### Security and governance

- **Authentication**: mTLS between services; OAuth for admin APIs.
- **Authorization**: RBAC for control commands and fork operations.
- **Encryption**: at rest for DB and archives; in transit for Kafka and service calls.
- **Audit**: append‑only admin audit log; immutable commit index for forensic replay.

---

### Appendix A DDL Example

```sql
CREATE TABLE commits (
  commit_id UUID PRIMARY KEY,
  layer TEXT NOT NULL,
  epoch_start BIGINT NOT NULL,
  epoch_end BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  summary JSONB
);

CREATE TABLE commit_entries (
  id BIGSERIAL PRIMARY KEY,
  commit_id UUID REFERENCES commits(commit_id),
  region_id TEXT NOT NULL,
  weight DOUBLE PRECISION NOT NULL,
  activity_mean DOUBLE PRECISION,
  activity_var DOUBLE PRECISION,
  entity_refs JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE entity_state (
  entity_id TEXT PRIMARY KEY,
  last_tick BIGINT,
  activity DOUBLE PRECISION DEFAULT 0,
  activity_history JSONB,
  metadata JSONB
);

CREATE INDEX idx_commits_created_at ON commits(created_at);
CREATE INDEX idx_commit_entries_commit_id ON commit_entries(commit_id);
CREATE INDEX idx_commit_entries_region ON commit_entries(region_id);
```

---

### Appendix B Next Deliverables

Choose one to generate next and it will be produced in copy‑ready form:

- **OpenAPI spec** implementing the uniform API contract.
- **TypeScript commit engine sketch** implementing accumulator, weighting, commit strategies, Kafka publishing, and Storage Adapter interface.
- **Storage Adapter interface plus Postgres and RocksDB reference adapters** with usage examples and configuration templates.
