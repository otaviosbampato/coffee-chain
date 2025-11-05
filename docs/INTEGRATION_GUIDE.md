# Coffee Traceability Blockchain - Integration Guide

## Overview
This blockchain implementation provides an immutable ledger for coffee traceability, where fiscalizers can create entries and clients can query the data.

## What Was Implemented

### 1. **Block Class**
- Fixed bugs in the original code (missing `self` parameter, incorrect method calls)
- Each block contains:
  - `index`: Position in the blockchain
  - `timestamp`: When the block was created
  - `data`: Coffee traceability information
  - `previous_hash`: Hash of the previous block (ensures chain integrity)
  - `nonce`: Proof of work value
  - `hash`: SHA-256 hash of the block

### 2. **Blockchain Class**
Key features:
- **Genesis Block**: Automatically creates the first block when initialized
- **Proof of Work**: Simple mining algorithm (configurable difficulty)
- **Chain Validation**: Ensures the blockchain hasn't been tampered with
- **CRUD Operations**: Add entries, query by batch/origin, get all entries
- **Import/Export**: Save and load the blockchain from JSON files

### 3. **Coffee-Specific Methods**

#### For Fiscalizers (Write Operations):
```python
# Add a new coffee entry
result = coffee_chain.add_entry({
    'fiscalizer_id': 'FISC001',
    'coffee_batch': 'BATCH-2025-001',
    'origin': 'Fazenda Santa Clara',
    'harvest_date': '2025-10-15',
    'quality_grade': 'A',
    'certifications': ['Organic', 'Fair Trade'],
    'weight_kg': 1000,
    'processing_method': 'Natural',
    'notes': 'High quality arabica beans'
})
```

#### For Clients (Read-Only Operations):
```python
# Query by batch ID
batch_data = coffee_chain.get_entry_by_batch('BATCH-2025-001')

# Query by origin
origin_data = coffee_chain.get_entry_by_origin('Fazenda Santa Clara')

# Get all entries
all_entries = coffee_chain.get_all_entries()

# Check blockchain validity
is_valid = coffee_chain.is_chain_valid()
```

---

## Integration with Your Architecture (Based on Diagram)

### Architecture Components from Your Diagram:

1. **Interface Web Frontend** (Usuario/User Interface)
2. **API Gateway** (Authentication, Rate Limiting, Load Balancing)
3. **Núcleo de Integração** (Integration Core with NoSQL Database)
4. **Blockchain** (Your implemented module)
5. **Agente Sumarizador** (Summarization Agent)

### Integration Flow:

#### **Flow 1: Fiscalizer Creates Entry**
```
1. User Login Request → Frontend
2. Frontend → API Gateway (JWT Token)
3. API Gateway → Núcleo de Integração (Validate User)
4. Núcleo checks NoSQL DB for user permissions
5. If fiscalizer authorized:
   ├── Núcleo → Blockchain.add_entry()
   ├── Blockchain returns hash
   └── Núcleo saves hash reference in NoSQL DB
6. Response flows back: Núcleo → API Gateway → Frontend
```

#### **Flow 2: Client Queries Entry**
```
1. User authenticated → Frontend
2. Frontend → API Gateway
3. API Gateway → Núcleo de Integração
4. Núcleo → Blockchain.get_entry_by_batch()
5. Blockchain returns entry data
6. Núcleo → Agente Sumarizador (formats data for user)
7. Response: Núcleo → API Gateway → Frontend
```

---

## Detailed Integration Steps

### Step 1: **API Gateway Integration**

Create a REST API wrapper around the blockchain:

```python
# api_blockchain.py (To be created)
from flask import Flask, request, jsonify
from blockchain import Blockchain
import jwt
from functools import wraps

app = Flask(__name__)
coffee_chain = Blockchain()

# JWT Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Fiscalizer endpoint (write access)
@app.route('/api/entries', methods=['POST'])
@token_required
def add_entry(current_user):
    if current_user['role'] != 'fiscalizer':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    result = coffee_chain.add_entry(data)
    return jsonify(result), 201 if result['success'] else 400

# Client endpoint (read access)
@app.route('/api/entries/<batch_id>', methods=['GET'])
@token_required
def get_entry(current_user, batch_id):
    result = coffee_chain.get_entry_by_batch(batch_id)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Batch not found'}), 404

# Get all entries (read access)
@app.route('/api/entries', methods=['GET'])
@token_required
def get_all_entries(current_user):
    entries = coffee_chain.get_all_entries()
    return jsonify(entries), 200

# Blockchain validation endpoint
@app.route('/api/blockchain/validate', methods=['GET'])
@token_required
def validate_chain(current_user):
    is_valid = coffee_chain.is_chain_valid()
    info = coffee_chain.get_chain_info()
    return jsonify({'valid': is_valid, 'info': info}), 200
```

### Step 2: **NoSQL Database Integration (Núcleo de Integração)**

The blockchain stores immutable data, but you should also maintain a NoSQL database for:
- User authentication and roles
- Quick lookups and indexing
- Metadata and relationships
- References to blockchain hashes

```python
# integration_core.py (Example structure)
from pymongo import MongoClient
from blockchain import Blockchain

class IntegrationCore:
    def __init__(self):
        self.blockchain = Blockchain()
        self.db = MongoClient('mongodb://localhost:27017/')['coffee_db']
        self.users_collection = self.db['users']
        self.entries_collection = self.db['entries']
    
    def create_entry_with_reference(self, user_id, entry_data):
        """Creates blockchain entry and saves reference in NoSQL"""
        # Add to blockchain
        result = self.blockchain.add_entry(entry_data)
        
        if result['success']:
            # Save reference in NoSQL for quick lookup
            self.entries_collection.insert_one({
                'user_id': user_id,
                'batch_id': entry_data['coffee_batch'],
                'blockchain_hash': result['block']['hash'],
                'block_index': result['block']['index'],
                'created_at': result['block']['timestamp']
            })
        
        return result
    
    def query_entry(self, batch_id):
        """Query blockchain with NoSQL index"""
        # First check NoSQL for reference
        ref = self.entries_collection.find_one({'batch_id': batch_id})
        
        if ref:
            # Get full data from blockchain
            return self.blockchain.get_entry_by_batch(batch_id)
        
        return None
```

### Step 3: **Frontend Integration**

Example JavaScript/TypeScript code for the web frontend:

```javascript
// frontend/services/blockchain.service.js
class BlockchainService {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api';
        this.token = localStorage.getItem('jwt_token');
    }
    
    // Fiscalizer: Add new entry
    async addEntry(entryData) {
        const response = await fetch(`${this.apiUrl}/entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': this.token
            },
            body: JSON.stringify(entryData)
        });
        return await response.json();
    }
    
    // Client: Query entry
    async getEntry(batchId) {
        const response = await fetch(`${this.apiUrl}/entries/${batchId}`, {
            headers: {
                'Authorization': this.token
            }
        });
        return await response.json();
    }
    
    // Get all entries
    async getAllEntries() {
        const response = await fetch(`${this.apiUrl}/entries`, {
            headers: {
                'Authorization': this.token
            }
        });
        return await response.json();
    }
    
    // Validate blockchain
    async validateBlockchain() {
        const response = await fetch(`${this.apiUrl}/blockchain/validate`, {
            headers: {
                'Authorization': this.token
            }
        });
        return await response.json();
    }
}
```

### Step 4: **Agente Sumarizador (Summarization Agent)**

Create an agent to format and summarize blockchain data for users:

```python
# summarization_agent.py
class SummarizationAgent:
    def format_entry_for_client(self, blockchain_entry):
        """Format blockchain data for client consumption"""
        data = blockchain_entry['data']
        
        return {
            'coffee_batch': data['coffee_batch'],
            'origin': data['origin'],
            'harvest_date': data['harvest_date'],
            'quality': data['quality_grade'],
            'certifications': ', '.join(data['certifications']),
            'weight': f"{data['weight_kg']} kg",
            'processing': data['processing_method'],
            'verified_by': data['fiscalizer_id'],
            'blockchain_hash': blockchain_entry['hash'],
            'verified_at': blockchain_entry['timestamp']
        }
    
    def generate_traceability_report(self, batch_id, blockchain):
        """Generate complete traceability report"""
        entries = blockchain.get_entry_by_batch(batch_id)
        
        if not entries:
            return None
        
        report = {
            'batch_id': batch_id,
            'entries': [self.format_entry_for_client(e) for e in entries],
            'blockchain_valid': blockchain.is_chain_valid(),
            'total_entries': len(entries)
        }
        
        return report
```

---

## Implementation Roadmap

### Phase 1: Backend Setup (Current)
- ✅ Blockchain implementation complete
- ⬜ Create Flask/FastAPI REST API
- ⬜ Integrate with NoSQL database (MongoDB/PostgreSQL)
- ⬜ Implement JWT authentication

### Phase 2: Integration Layer
- ⬜ Build Integration Core (Núcleo de Integração)
- ⬜ Create Summarization Agent
- ⬜ Set up API Gateway with rate limiting

### Phase 3: Frontend
- ⬜ Build web interface (React/Vue/Angular)
- ⬜ Create fiscalizer dashboard (create entries)
- ⬜ Create client interface (query entries)
- ⬜ Add QR code generation for batch IDs

### Phase 4: Advanced Features
- ⬜ Multi-node blockchain (distributed)
- ⬜ Smart contracts (if needed)
- ⬜ Real-time notifications
- ⬜ Analytics dashboard

---

## Key Security Considerations

1. **Authentication**: Only fiscalizers can write to the blockchain
2. **Validation**: All blocks are validated before adding
3. **Immutability**: Once data is in the blockchain, it cannot be altered
4. **Transparency**: Clients can verify data integrity via hash validation
5. **Rate Limiting**: Prevent spam/abuse through API Gateway

---

## Testing the Blockchain

```bash
# Run the blockchain test
python3 blockchain.py

# Check the exported JSON
cat coffee_blockchain.json
```

---

## Next Steps

1. **Choose your web framework**: Flask (simple) or FastAPI (modern, async)
2. **Set up database**: MongoDB for NoSQL or PostgreSQL with JSONB
3. **Create API endpoints**: Follow the examples above
4. **Build frontend**: React/Vue for modern UI
5. **Deploy**: Docker containers, cloud services (AWS, Azure, GCP)

---

## Data Flow Summary

```
FISCALIZER FLOW:
User → Frontend → API Gateway → Integration Core → Blockchain.add_entry() → NoSQL (save reference)

CLIENT FLOW:
User → Frontend → API Gateway → Integration Core → Blockchain.get_entry_by_batch() → Summarization Agent → Response

VALIDATION FLOW:
Any User → Frontend → API Gateway → Integration Core → Blockchain.is_chain_valid() → Response
```

---

## Questions?

For additional customization:
- Add more fields to the coffee entry data
- Implement consensus algorithms for distributed nodes
- Add smart contract functionality
- Integrate with IoT devices for automated data entry
- Add geolocation tracking
- Implement QR code scanning for mobile apps
