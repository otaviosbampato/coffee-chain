# Coffee Traceability Blockchain System# Coffeechain



A complete blockchain-based system for coffee traceability with role-based access control, allowing fiscalizers to create entries and clients to verify coffee origins.O projeto Coffeechain propõe uma solução tecnológica para rastrear e gerenciar informações da produção de café desde a origem até o comprador final. Ele utiliza uma arquitetura em camadas que integra blockchain, responsável por armazenar dados de safra de forma segura e imutável, e uma IA Sumarizadora, que gera relatórios automáticos e históricos acessíveis aos compradores.

A camada de RAG (Retrieval-Augmented Generation) atua como intermediária, filtrando e estruturando as informações antes de chegarem à IA, o que permite consultas mais rápidas, precisas e contextualizadas sobre os registros do sistema.

---

## Justificativa

## 🏗️ Project Structure

A rastreabilidade do café tornou-se uma necessidade diante das novas exigências do mercado europeu por origem comprovada e transparência nas cadeias produtivas. Nesse contexto, o uso de blockchain surge como meio de registrar dados de forma imutável e auditável, enquanto IA e RAG possibilitam análises mais ágeis e inteligentes sobre as informações da safra, conectando tecnologia, confiança e sustentabilidade no setor cafeeiro.

```

blockchain/## Arquitetura

├── backend/                    # Backend services

│   ├── blockchain/             # Blockchain implementationO tipo arquitetural escolhido foi a arquitetura em camadas.

│   │   ├── __init__.py

│   │   └── blockchain.py       # Core blockchain with persistent storage#### Camada de Usuários e Interface

│   ├── database/               # Database layer - Usuários: Fiscais / Produtores, Compradores.

│   │   ├── __init__.py - Interface: Frontend.

│   │   └── database.py         # User management & indexing (SQLite/MongoDB) - Função: Inserir dados, consultar rastreabilidade, visualizar relatórios.

│   ├── api/                    # REST API

│   │   ├── __init__.py#### Camada de Serviços Distribuídos

│   │   └── app.py              # Flask API with JWT authentication - Componentes: API Gateway, sincronização de dados, autenticação/autorização.

│   └── __init__.py - Função: Roteamento de requisições, controle de acesso, comunicação entre microserviços, sincronização entre os nós da blockchain.

│

├── frontend/                   # Web interface#### Camada de Inteligência Artificial

│   ├── index.html              # Main UI (HTML5) - IA Sumarizadora

│   ├── styles.css              # Coffee-themed styling    - Atua como ponte convertendo a entrada do usuário em uma query na blockchain.

│   └── app.js                  # Frontend logic (vanilla JS)

│#### Camada de Blockchain e Dados

├── data/                       # Persistent storage - Blockchain:

│   ├── blockchain.json         # Blockchain data (auto-saved)    - Registra blocos de dados da safra, garantindo imutabilidade.

│   ├── coffeechain.db          # SQLite database (users & indexes)    - Rede de nós distribuídos em containers backend.

│   └── *.json                  # Blockchain exports    - Bancos de dados auxiliares: SQL / NoSQL, banco vetorial para consultas RAG.

│

├── docs/                       # Documentation#### Camada de Filtragem e Sumarização (RAG)

│   ├── DATABASE_STRATEGY.md    # Storage architecture explained - Filtra, resume e formata dados do usúario para alimentar a IA.

│   ├── ARCHITECTURE.md         # System design

│   ├── QUICK_START.md          # Getting started guide#### Diagrama Arquitetural

│   └── INTEGRATION_GUIDE.md    # Integration instructions

│![Image](./assets/Arquitetura.jpg)

├── venv/                       # Python virtual environment

├── start.sh                    # Startup script## Autores

├── requirements.txt            # Python dependencies

└── README.md                   # This file[Otávio Sbampato Andrade](https://github.com/otaviosbampato)

```[Isac Gonçalves Cunha](https://github.com/isaccunha)

[Gabriel Coelho Costa](https://github.com/gabrielzinCoelho)

---[Paulo Henrique Ribeiro Alves](https://github.com/paulohenrique64)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Start the System

```bash
# Easy way: use the startup script
./start.sh

# Manual way:
source venv/bin/activate
cd backend/api
python app.py
```

### 3. Access the System

- **API**: http://localhost:5000
- **Frontend**: Open `frontend/index.html` in your browser
- **API Health Check**: http://localhost:5000/api/health

---

## 🔐 Test Credentials

### Fiscalizers (can create entries)
- Username: `fiscalizer1` | Password: `fisc123`
- Username: `fiscalizer2` | Password: `fisc456`

### Clients (can only view entries)
- Username: `client1` | Password: `client123`
- Username: `client2` | Password: `client456`

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - User login (get JWT token)
- `GET /api/auth/verify` - Verify token validity

### Coffee Entries
- `POST /api/entries` - Create new entry (fiscalizers only)
- `GET /api/entries` - Get all entries
- `GET /api/entries/batch/<id>` - Get entry by coffee batch ID
- `GET /api/entries/origin/<name>` - Get entries by origin/farm

### Blockchain
- `GET /api/blockchain/info` - Get blockchain information
- `GET /api/blockchain/validate` - Validate entire chain
- `POST /api/blockchain/backup` - Create blockchain backup (fiscalizers only)

### Database
- `GET /api/database/stats` - Get database statistics

### System
- `GET /api/health` - Health check

---

## 💾 Storage Strategy

### Blockchain (Immutable Data)
- **Where**: `data/blockchain.json`
- **What**: All coffee traceability entries (batches, origins, dates, etc.)
- **Why**: Blockchain provides immutability and tamper-proof audit trail
- **Auto-saved**: After every new block

### Database (Metadata & Indexes)
- **Where**: `data/coffeechain.db` (SQLite) or MongoDB
- **What**: 
  - User accounts (fiscalizers & clients)
  - Fast lookup indexes (batch_id → block_index)
  - Analytics and statistics
- **Why**: Fast queries without scanning entire blockchain

See `docs/DATABASE_STRATEGY.md` for complete explanation.

---

## 🏗️ Architecture

### Backend
- **Language**: Python 3.12+
- **Framework**: Flask 3.0
- **Authentication**: JWT tokens (24h expiration)
- **Blockchain**: SHA-256 hashing, Proof-of-Work (difficulty=2)
- **Database**: SQLite (default) or MongoDB (optional)

### Frontend
- **No frameworks**: Pure HTML5, CSS3, JavaScript ES6+
- **Design**: Coffee-themed (#6F4E37), responsive, animated
- **Features**: Login modal, tabbed search, real-time validation

---

## 📖 Documentation

1. **DATABASE_STRATEGY.md** - Explains why blockchain is in JSON and what goes in the database
2. **ARCHITECTURE.md** - System design and component interactions
3. **QUICK_START.md** - Step-by-step getting started guide
4. **INTEGRATION_GUIDE.md** - How to integrate with external systems

---

## 🔧 Development

### Running Tests
```bash
source venv/bin/activate
python backend/tests/test_blockchain.py
```

### Using MongoDB Instead of SQLite
```bash
# Install MongoDB driver
pip install pymongo

# Update backend/api/app.py line 23:
db = get_database(db_type='mongodb', db_uri='mongodb://localhost:27017/')
```

### Creating New Users
```python
from backend.database.database import get_database

db = get_database()
db.create_user(
    username='newuser',
    password='password123',
    role='fiscalizer',  # or 'client'
    name='User Name',
    email='user@example.com'
)
```

---

## 🛡️ Security Notes

⚠️ **For Production Use**:
1. Change `SECRET_KEY` in `backend/api/app.py` (line 14)
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Add rate limiting
5. Implement proper password hashing (use bcrypt)
6. Set up proper MongoDB authentication

---

## 📝 Creating a Coffee Entry

### Via API (cURL)
```bash
# 1. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"fiscalizer1","password":"fisc123"}'

# 2. Create entry (use token from login)
curl -X POST http://localhost:5000/api/auth/entries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "coffee_batch": "BATCH-2024-001",
    "origin": "Fazenda Santa Clara",
    "harvest_date": "2024-01-15",
    "quality_grade": "A",
    "weight_kg": 1500,
    "processing_method": "Washed",
    "notes": "Exceptional quality, citrus notes"
  }'
```

### Via Frontend
1. Open `frontend/index.html`
2. Click "Login" → use fiscalizer credentials
3. Fill the "Create Entry" form
4. Submit → entry is added to blockchain

---

## 🔍 Searching Entries

### By Batch ID
```bash
curl http://localhost:5000/api/entries/batch/BATCH-2024-001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### By Origin
```bash
curl http://localhost:5000/api/entries/origin/Fazenda%20Santa%20Clara \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🤝 Contributing

This is a demonstration project for coffee traceability using blockchain technology. Feel free to extend it with:
- Additional validation rules
- More detailed coffee properties
- Certificate generation
- Mobile app integration
- IoT sensor data integration

---

## 📄 License

Educational project - use as you wish.

---

## 📞 Support

For questions about the architecture:
- Read `docs/DATABASE_STRATEGY.md` for storage decisions
- Read `docs/ARCHITECTURE.md` for system design
- Check `docs/INTEGRATION_GUIDE.md` for integration patterns

---

## 🎯 Key Features

✅ **Immutable blockchain** for coffee traceability  
✅ **Role-based access** (fiscalizers vs clients)  
✅ **JWT authentication** with 24h tokens  
✅ **Persistent storage** (auto-save blockchain)  
✅ **Fast lookups** via database indexing  
✅ **Beautiful UI** with coffee theme  
✅ **Complete API** with 11 endpoints  
✅ **Proof-of-work** mining algorithm  
✅ **Chain validation** to detect tampering  
✅ **Backup system** for blockchain data  

---

**Built with ☕ for coffee traceability**
