"""
Coffee Traceability API
RESTful API for the coffee blockchain system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain import Blockchain
import jwt
import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)  # Enable CORS for frontend integration

# Initialize blockchain
coffee_chain = Blockchain()

# Mock user database (replace with real database in production)
USERS = {
    'fiscalizer1': {'password': 'fisc123', 'role': 'fiscalizer', 'name': 'João Silva'},
    'fiscalizer2': {'password': 'fisc456', 'role': 'fiscalizer', 'name': 'Maria Santos'},
    'client1': {'password': 'client123', 'role': 'client', 'name': 'Carlos Souza'},
    'client2': {'password': 'client456', 'role': 'client', 'name': 'Ana Costa'}
}


def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
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


# ============== AUTHENTICATION ENDPOINTS ==============

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    Returns JWT token for authenticated users
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    # Validate credentials (replace with real database query)
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'username': username,
        'role': user['role'],
        'name': user['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': {
            'username': username,
            'role': user['role'],
            'name': user['name']
        }
    }), 200


@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if token is still valid"""
    return jsonify({'valid': True, 'user': current_user}), 200


# ============== BLOCKCHAIN ENTRY ENDPOINTS ==============

@app.route('/api/entries', methods=['POST'])
@token_required
@fiscalizer_required
def create_entry(current_user):
    """
    Create a new coffee entry (fiscalizers only)
    
    Request body example:
    {
        "coffee_batch": "BATCH-2025-001",
        "origin": "Fazenda Santa Clara",
        "harvest_date": "2025-10-15",
        "quality_grade": "A",
        "certifications": ["Organic", "Fair Trade"],
        "weight_kg": 1000,
        "processing_method": "Natural",
        "notes": "High quality arabica beans"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    # Add fiscalizer info to entry
    data['fiscalizer_id'] = current_user['username']
    data['fiscalizer_name'] = current_user['name']
    
    # Validate required fields
    required_fields = ['coffee_batch', 'origin', 'harvest_date', 'quality_grade', 'weight_kg']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    # Add entry to blockchain
    result = coffee_chain.add_entry(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/entries', methods=['GET'])
@token_required
def get_all_entries(current_user):
    """
    Get all coffee entries
    Accessible by both fiscalizers and clients
    """
    entries = coffee_chain.get_all_entries()
    
    return jsonify({
        'entries': entries,
        'total': len(entries)
    }), 200


@app.route('/api/entries/batch/<batch_id>', methods=['GET'])
@token_required
def get_entry_by_batch(current_user, batch_id):
    """
    Get entries by coffee batch ID
    Accessible by both fiscalizers and clients
    """
    entries = coffee_chain.get_entry_by_batch(batch_id)
    
    if entries:
        return jsonify({
            'batch_id': batch_id,
            'entries': entries,
            'total': len(entries)
        }), 200
    else:
        return jsonify({'error': f'No entries found for batch {batch_id}'}), 404


@app.route('/api/entries/origin/<origin>', methods=['GET'])
@token_required
def get_entry_by_origin(current_user, origin):
    """
    Get entries by origin/farm name
    Accessible by both fiscalizers and clients
    """
    entries = coffee_chain.get_entry_by_origin(origin)
    
    if entries:
        return jsonify({
            'origin': origin,
            'entries': entries,
            'total': len(entries)
        }), 200
    else:
        return jsonify({'error': f'No entries found for origin {origin}'}), 404


# ============== BLOCKCHAIN INFO ENDPOINTS ==============

@app.route('/api/blockchain/info', methods=['GET'])
@token_required
def get_blockchain_info(current_user):
    """Get blockchain information"""
    info = coffee_chain.get_chain_info()
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


@app.route('/api/blockchain/export', methods=['GET'])
@token_required
@fiscalizer_required
def export_blockchain(current_user):
    """Export blockchain to JSON file (fiscalizers only)"""
    try:
        filename = coffee_chain.export_chain(f'exports/blockchain_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Blockchain exported successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== HEALTH CHECK ENDPOINT ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'blockchain_length': len(coffee_chain.chain),
        'blockchain_valid': coffee_chain.is_chain_valid(),
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
    # Create exports directory if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    
    print("\n=== Coffee Traceability Blockchain API ===")
    print("\nTest Users:")
    print("Fiscalizers:")
    print("  - Username: fiscalizer1, Password: fisc123")
    print("  - Username: fiscalizer2, Password: fisc456")
    print("Clients:")
    print("  - Username: client1, Password: client123")
    print("  - Username: client2, Password: client456")
    print("\nAPI Endpoints:")
    print("  POST   /api/auth/login")
    print("  GET    /api/auth/verify")
    print("  POST   /api/entries (fiscalizers only)")
    print("  GET    /api/entries")
    print("  GET    /api/entries/batch/<batch_id>")
    print("  GET    /api/entries/origin/<origin>")
    print("  GET    /api/blockchain/info")
    print("  GET    /api/blockchain/validate")
    print("  GET    /api/blockchain/export (fiscalizers only)")
    print("  GET    /api/health")
    print("\nStarting server on http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
