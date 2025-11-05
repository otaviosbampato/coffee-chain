"""
Coffee Traceability API - Reorganized
Integrates Blockchain + Database
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain.blockchain import Blockchain
from database.database import get_database
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Initialize blockchain with persistent storage
coffee_chain = Blockchain(storage_path='data/blockchain.json')

# Initialize database (SQLite by default, can use MongoDB)
db = get_database(db_type='sqlite', db_path='data/coffeechain.db')


# ============== DECORATORS ==============

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = {
                'username': data['username'],
                'role': data['role'],
                'name': data['name']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def fiscalizer_required(f):
    """Decorator to require fiscalizer role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'fiscalizer':
            return jsonify({'error': 'Fiscalizer access required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated


# ============== AUTHENTICATION ==============

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    # Validate with database
    user = db.validate_user(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'username': user['username'],
        'role': user['role'],
        'name': user['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': user
    }), 200


@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if token is still valid"""
    return jsonify({'valid': True, 'user': current_user}), 200


# ============== BLOCKCHAIN ENTRIES ==============

@app.route('/api/entries', methods=['POST'])
@token_required
@fiscalizer_required
def create_entry(current_user):
    """Create a new coffee entry (fiscalizers only)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    # Add fiscalizer info
    data['fiscalizer_id'] = current_user['username']
    data['fiscalizer_name'] = current_user['name']
    
    # Validate required fields
    required_fields = ['coffee_batch', 'origin', 'harvest_date', 'quality_grade', 'weight_kg']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    # Add to blockchain
    result = coffee_chain.add_entry(data)
    
    if result['success']:
        # Index in database for fast lookup
        db.index_blockchain_entry(
            batch_id=data['coffee_batch'],
            block_index=result['block']['index'],
            block_hash=result['block']['hash'],
            fiscalizer_id=current_user['username'],
            data=data
        )
        
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/entries', methods=['GET'])
@token_required
def get_all_entries(current_user):
    """Get all coffee entries"""
    entries = coffee_chain.get_all_entries()
    
    return jsonify({
        'entries': entries,
        'total': len(entries)
    }), 200


@app.route('/api/entries/batch/<batch_id>', methods=['GET'])
@token_required
def get_entry_by_batch(current_user, batch_id):
    """Get entries by coffee batch ID"""
    # Try database index first for faster lookup
    db_entry = db.find_by_batch(batch_id)
    
    # Get full data from blockchain
    entries = coffee_chain.get_entry_by_batch(batch_id)
    
    if entries:
        return jsonify({
            'batch_id': batch_id,
            'entries': entries,
            'total': len(entries),
            'indexed': db_entry is not None
        }), 200
    else:
        return jsonify({'error': f'No entries found for batch {batch_id}'}), 404


@app.route('/api/entries/origin/<origin>', methods=['GET'])
@token_required
def get_entry_by_origin(current_user, origin):
    """Get entries by origin/farm name"""
    entries = coffee_chain.get_entry_by_origin(origin)
    
    if entries:
        return jsonify({
            'origin': origin,
            'entries': entries,
            'total': len(entries)
        }), 200
    else:
        return jsonify({'error': f'No entries found for origin {origin}'}), 404


# ============== BLOCKCHAIN INFO ==============

@app.route('/api/blockchain/info', methods=['GET'])
@token_required
def get_blockchain_info(current_user):
    """Get blockchain information"""
    info = coffee_chain.get_chain_info()
    info['database_stats'] = db.get_stats()
    return jsonify(info), 200


@app.route('/api/blockchain/validate', methods=['GET'])
@token_required
def validate_blockchain(current_user):
    """Validate the entire blockchain"""
    is_valid = coffee_chain.is_chain_valid()
    info = coffee_chain.get_chain_info()
    
    return jsonify({
        'valid': is_valid,
        'info': info,
        'message': 'Blockchain is valid' if is_valid else 'Blockchain has been compromised'
    }), 200


@app.route('/api/blockchain/backup', methods=['POST'])
@token_required
@fiscalizer_required
def create_backup(current_user):
    """Create blockchain backup (fiscalizers only)"""
    try:
        backup_path = coffee_chain.create_backup()
        return jsonify({
            'success': True,
            'backup_path': backup_path,
            'message': 'Backup created successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== DATABASE INFO ==============

@app.route('/api/database/stats', methods=['GET'])
@token_required
def get_database_stats(current_user):
    """Get database statistics"""
    stats = db.get_stats()
    return jsonify(stats), 200


# ============== HEALTH CHECK ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'blockchain_length': len(coffee_chain.chain),
        'blockchain_valid': coffee_chain.is_chain_valid(),
        'blockchain_storage': coffee_chain.storage_path,
        'database_type': db.db_type,
        'database_stats': db.get_stats(),
        'timestamp': datetime.datetime.now().isoformat()
    }), 200


# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============== RUN SERVER ==============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Coffee Traceability Blockchain API - Reorganized")
    print("="*60)
    print("\n📊 System Status:")
    print(f"  • Blockchain: {len(coffee_chain.chain)} blocks")
    print(f"  • Storage: {coffee_chain.storage_path}")
    print(f"  • Database: {db.db_type}")
    
    stats = db.get_stats()
    print(f"\n👥 Database Users:")
    print(f"  • Total: {stats['total_users']}")
    print(f"  • Fiscalizers: {stats['total_fiscalizers']}")
    print(f"  • Clients: {stats['total_clients']}")
    
    print("\n🔐 Test Credentials:")
    print("  Fiscalizers:")
    print("    • fiscalizer1 / fisc123")
    print("    • fiscalizer2 / fisc456")
    print("  Clients:")
    print("    • client1 / client123")
    print("    • client2 / client456")
    
    print("\n📡 API Endpoints:")
    print("  POST   /api/auth/login")
    print("  GET    /api/auth/verify")
    print("  POST   /api/entries (fiscalizers)")
    print("  GET    /api/entries")
    print("  GET    /api/entries/batch/<id>")
    print("  GET    /api/entries/origin/<name>")
    print("  GET    /api/blockchain/info")
    print("  GET    /api/blockchain/validate")
    print("  POST   /api/blockchain/backup (fiscalizers)")
    print("  GET    /api/database/stats")
    print("  GET    /api/health")
    
    print("\n🚀 Starting server on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
