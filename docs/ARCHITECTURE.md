# Architecture Diagram - Coffee Traceability Blockchain

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO / USER                              │
│                    (Fiscalizer or Client)                           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 1. Login/Request
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERFACE WEB FRONTEND                           │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │  Fiscalizer Dashboard    │  │    Client Interface          │   │
│  │  - Create Entries        │  │    - Query Batches           │   │
│  │  - View Blockchain       │  │    - Verify Authenticity     │   │
│  └──────────────────────────┘  └──────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 2. JWT Token
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  • JWT Authentication (Bearer Token)                         │  │
│  │  • Role Validation (fiscalizer vs client)                    │  │
│  │  • Rate Limiting (prevent abuse)                             │  │
│  │  • Load Balancing (distribute requests)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 3. Validated Request
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NÚCLEO DE INTEGRAÇÃO                             │
│                    (Integration Core)                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Business Logic Layer                                        │  │
│  │  • Validate user permissions                                 │  │
│  │  • Format data for blockchain                                │  │
│  │  • Coordinate between components                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌────────────────────┐              ┌────────────────────────┐   │
│  │                    │              │                        │   │
│  │  4. Query Users    │              │  9. Save Reference     │   │
│  │                    │              │                        │   │
│  ▼                    │              │                        ▼   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              BANCO DE DADOS NoSQL                           │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Collections:                                         │  │  │
│  │  │  • users (id, username, password_hash, role, name)   │  │  │
│  │  │  • entry_refs (batch_id, blockchain_hash, index)     │  │  │
│  │  │  • metadata (timestamps, relationships)              │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  5. User Validated ──┐                                             │
└─────────────────────┼─────────────────────────────────────────────┘
                      │
                      │ 6. Create/Query Entry
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BLOCKCHAIN (blockchain.py)                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Blockchain Class                                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │  │
│  │  │  Block 0   │→ │  Block 1   │→ │  Block 2   │→  ...      │  │
│  │  │  (Genesis) │  │            │  │            │            │  │
│  │  └────────────┘  └────────────┘  └────────────┘            │  │
│  │                                                              │  │
│  │  Methods:                                                    │  │
│  │  • add_entry(data)           [Fiscalizers]                  │  │
│  │  • get_entry_by_batch(id)    [Clients]                      │  │
│  │  • get_entry_by_origin(name) [Clients]                      │  │
│  │  • is_chain_valid()          [Both]                         │  │
│  │  • export_chain()            [Fiscalizers]                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Each Block Contains:                                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  {                                                           │  │
│  │    index: 1,                                                 │  │
│  │    timestamp: "2025-11-05T...",                              │  │
│  │    data: {                                                   │  │
│  │      coffee_batch: "BATCH-2025-001",                         │  │
│  │      origin: "Fazenda Santa Clara",                          │  │
│  │      fiscalizer_id: "FISC001",                               │  │
│  │      quality_grade: "AA",                                    │  │
│  │      ...                                                     │  │
│  │    },                                                        │  │
│  │    previous_hash: "000abc123...",                            │  │
│  │    nonce: 42,                                                │  │
│  │    hash: "00def456..."                                       │  │
│  │  }                                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 7. Return Data
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   AGENTE SUMARIZADOR                                │
│                   (AI/RAG Summarization Agent)                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  • Format blockchain data for humans                         │  │
│  │  • Generate traceability reports                             │  │
│  │  • Answer natural language queries                           │  │
│  │  • Provide insights and analytics                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Example Queries:                                                   │
│  • "Show me all organic coffee from Minas Gerais"                   │
│  • "What's the complete history of BATCH-2025-001?"                 │
│  • "Which fiscalizer verified the most entries this month?"         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 8. Formatted Response
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Response flows back to user                          │
│  Integration Core → API Gateway → Frontend → User                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Fiscalizer Creates Entry

```
1. Fiscalizer logs in
   User → Frontend → API Gateway → Auth (JWT token issued)

2. Fiscalizer creates coffee entry
   Frontend → API Gateway (with JWT) → Integration Core

3. Integration Core validates
   • Check JWT token
   • Verify fiscalizer role
   • Check user exists in NoSQL

4. Add to blockchain
   Integration Core → Blockchain.add_entry(data)
   • Creates new block
   • Runs proof of work
   • Validates chain
   • Returns block hash

5. Save reference in NoSQL
   Integration Core → NoSQL
   • Save batch_id → blockchain_hash mapping
   • Save for quick lookups

6. Return success
   Integration Core → API Gateway → Frontend → User
   • Show confirmation
   • Display block hash
```

## Data Flow: Client Queries Entry

```
1. Client logs in
   User → Frontend → API Gateway → Auth (JWT token issued)

2. Client queries batch
   Frontend → API Gateway (with JWT) → Integration Core

3. Check NoSQL for quick lookup (optional)
   Integration Core → NoSQL
   • Find blockchain reference by batch_id

4. Query blockchain
   Integration Core → Blockchain.get_entry_by_batch(batch_id)
   • Search blockchain for matching entries
   • Return all blocks with that batch

5. Format with AI (optional)
   Integration Core → Agente Sumarizador
   • Format technical data for user
   • Add context and explanations
   • Generate summary

6. Return data
   Integration Core → API Gateway → Frontend → User
   • Show coffee details
   • Display verification status
   • Show blockchain hash (proof of authenticity)
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Authentication (API Gateway)                       │
│ • JWT tokens with expiration                                │
│ • User login required for all operations                    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Authorization (API Gateway + Integration Core)     │
│ • Role-based access control                                 │
│ • Fiscalizers: CREATE + READ                                │
│ • Clients: READ only                                        │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Data Integrity (Blockchain)                        │
│ • SHA-256 cryptographic hashing                             │
│ • Chain validation (detect tampering)                       │
│ • Immutable records                                         │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Proof of Work (Blockchain)                         │
│ • Computational difficulty                                  │
│ • Makes tampering expensive                                 │
│ • Configurable difficulty level                             │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints Map

```
Authentication:
POST   /api/auth/login          → Returns JWT token
GET    /api/auth/verify         → Validates token

Entries (CRUD):
POST   /api/entries             → Create entry (fiscalizers only)
GET    /api/entries             → Get all entries
GET    /api/entries/batch/:id   → Get specific batch
GET    /api/entries/origin/:name → Get by origin

Blockchain Info:
GET    /api/blockchain/info     → Get chain statistics
GET    /api/blockchain/validate → Validate integrity
GET    /api/blockchain/export   → Export to JSON (fiscalizers only)

Health:
GET    /api/health              → System health check
```

## Technology Stack

```
Frontend Layer:
├── React / Vue / Angular (choose one)
├── JavaScript / TypeScript
└── HTTP Client (fetch / axios)

API Layer:
├── Flask (Python web framework)
├── Flask-CORS (cross-origin requests)
├── PyJWT (JSON Web Tokens)
└── RESTful API design

Business Logic:
├── Integration Core (Python)
├── Custom business rules
└── Data validation

Data Layer:
├── Blockchain (blockchain.py)
│   └── Python standard library (hashlib, json)
├── NoSQL Database
│   └── MongoDB / PostgreSQL
└── File System (exports)

AI Layer:
├── Agente Sumarizador (to be implemented)
├── RAG (Retrieval-Augmented Generation)
└── Natural Language Processing
```

## Deployment Architecture

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  API Server  │ │  API Server  │ │  API Server  │
    │   Instance 1 │ │   Instance 2 │ │   Instance 3 │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │   Blockchain │        │   NoSQL DB   │
        │   Service    │        │   Cluster    │
        └──────────────┘        └──────────────┘
```

---

*This architecture provides scalability, security, and immutability for coffee traceability.*
