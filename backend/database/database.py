"""
Database Module
Supports both MongoDB and SQLite
"""

import os
import sqlite3
import hashlib
from typing import Optional, Dict, List
from datetime import datetime

    
class Database:
    """
    Abstract database class that can use MongoDB or SQLite
    """
    
    def __init__(self, db_type='sqlite', **kwargs):
        self.db_type = db_type
        
        if db_type == 'mongodb':
            self._init_mongodb(**kwargs)
        else:
            self._init_sqlite(**kwargs)
    
    def _init_sqlite(self, db_path='data/coffeechain.db'):
        """Initialize SQLite database"""
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_sqlite_tables()
        print(f"✓ SQLite database initialized at {db_path}")
    
    def _init_mongodb(self, host='localhost', port=27017, db_name='coffeechain'):
        """Initialize MongoDB connection"""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(host, port)
            self.db = self.client[db_name]
            self._create_mongodb_collections()
            print(f"✓ MongoDB connected: {host}:{port}/{db_name}")
        except ImportError:
            print("⚠️  pymongo not installed. Run: pip install pymongo")
            print("   Falling back to SQLite...")
            self._init_sqlite()
            self.db_type = 'sqlite'
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("   Falling back to SQLite...")
            self._init_sqlite()
            self.db_type = 'sqlite'
    
    def _create_sqlite_tables(self):
        """Create SQLite tables"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Blockchain index table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT UNIQUE NOT NULL,
                block_index INTEGER NOT NULL,
                block_hash TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                fiscalizer_id TEXT,
                origin TEXT,
                quality_grade TEXT,
                weight_kg INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_id ON blockchain_index(batch_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_origin ON blockchain_index(origin)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_fiscalizer ON blockchain_index(fiscalizer_id)')
        
        self.conn.commit()
        
        # Create default users if table is empty
        self._create_default_users_sqlite()
    
    def _create_mongodb_collections(self):
        """Create MongoDB collections and indexes"""
        # Create indexes
        self.db.users.create_index('username', unique=True)
        self.db.blockchain_index.create_index('batch_id', unique=True)
        self.db.blockchain_index.create_index('origin')
        self.db.blockchain_index.create_index('fiscalizer_id')
        
        # Create default users if collection is empty
        self._create_default_users_mongodb()
    
    def _create_default_users_sqlite(self):
        """Create default test users in SQLite"""
        default_users = [
            ('fiscalizer1', 'fisc123', 'fiscalizer', 'João Silva'),
            ('fiscalizer2', 'fisc456', 'fiscalizer', 'Maria Santos'),
            ('client1', 'client123', 'client', 'Carlos Souza'),
            ('client2', 'client456', 'client', 'Ana Costa'),
        ]
        
        for username, password, role, name in default_users:
            try:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                self.cursor.execute('''
                    INSERT OR IGNORE INTO users (username, password_hash, role, name)
                    VALUES (?, ?, ?, ?)
                ''', (username, password_hash, role, name))
            except:
                pass
        
        self.conn.commit()
    
    def _create_default_users_mongodb(self):
        """Create default test users in MongoDB"""
        if self.db.users.count_documents({}) == 0:
            default_users = [
                {'username': 'fiscalizer1', 'password': 'fisc123', 'role': 'fiscalizer', 'name': 'João Silva'},
                {'username': 'fiscalizer2', 'password': 'fisc456', 'role': 'fiscalizer', 'name': 'Maria Santos'},
                {'username': 'client1', 'password': 'client123', 'role': 'client', 'name': 'Carlos Souza'},
                {'username': 'client2', 'password': 'client456', 'role': 'client', 'name': 'Ana Costa'},
            ]
            
            for user in default_users:
                user['password_hash'] = hashlib.sha256(user['password'].encode()).hexdigest()
                del user['password']
                user['created_at'] = datetime.now()
                self.db.users.insert_one(user)
    
    # User Management
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        if self.db_type == 'mongodb':
            user = self.db.users.find_one({'username': username})
            if user:
                user['_id'] = str(user['_id'])
            return user
        else:
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
    
    def create_user(self, username: str, password: str, role: str, name: str) -> bool:
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            if self.db_type == 'mongodb':
                self.db.users.insert_one({
                    'username': username,
                    'password_hash': password_hash,
                    'role': role,
                    'name': name,
                    'created_at': datetime.now()
                })
            else:
                self.cursor.execute('''
                    INSERT INTO users (username, password_hash, role, name)
                    VALUES (?, ?, ?, ?)
                ''', (username, password_hash, role, name))
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def validate_user(self, username: str, password: str) -> Optional[Dict]:
        """Validate user credentials"""
        user = self.get_user(username)
        if user:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash:
                # Update last login
                self.update_last_login(username)
                return {
                    'username': user['username'],
                    'role': user['role'],
                    'name': user['name']
                }
        return None
    
    def update_last_login(self, username: str):
        """Update user's last login timestamp"""
        if self.db_type == 'mongodb':
            self.db.users.update_one(
                {'username': username},
                {'$set': {'last_login': datetime.now()}}
            )
        else:
            self.cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            ''', (username,))
            self.conn.commit()
    
    # Blockchain Index Management
    
    def index_blockchain_entry(self, batch_id: str, block_index: int, block_hash: str, 
                                fiscalizer_id: str, data: Dict):
        """Create an index entry for fast blockchain lookup"""
        try:
            if self.db_type == 'mongodb':
                self.db.blockchain_index.insert_one({
                    'batch_id': batch_id,
                    'block_index': block_index,
                    'block_hash': block_hash,
                    'timestamp': datetime.now(),
                    'fiscalizer_id': fiscalizer_id,
                    'origin': data.get('origin'),
                    'quality_grade': data.get('quality_grade'),
                    'weight_kg': data.get('weight_kg'),
                    'created_at': datetime.now()
                })
            else:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO blockchain_index 
                    (batch_id, block_index, block_hash, timestamp, fiscalizer_id, origin, quality_grade, weight_kg)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (batch_id, block_index, block_hash, datetime.now(), fiscalizer_id, 
                      data.get('origin'), data.get('quality_grade'), data.get('weight_kg')))
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error indexing entry: {e}")
            return False
    
    def find_by_batch(self, batch_id: str) -> Optional[Dict]:
        """Find blockchain entry by batch ID"""
        if self.db_type == 'mongodb':
            result = self.db.blockchain_index.find_one({'batch_id': batch_id})
            if result:
                result['_id'] = str(result['_id'])
            return result
        else:
            self.cursor.execute('SELECT * FROM blockchain_index WHERE batch_id = ?', (batch_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
    
    def find_by_origin(self, origin: str) -> List[Dict]:
        """Find all entries from a specific origin"""
        if self.db_type == 'mongodb':
            results = self.db.blockchain_index.find({'origin': {'$regex': origin, '$options': 'i'}})
            return [dict(r) for r in results]
        else:
            self.cursor.execute('SELECT * FROM blockchain_index WHERE origin LIKE ?', (f'%{origin}%',))
            return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_indexes(self) -> List[Dict]:
        """Get all blockchain index entries"""
        if self.db_type == 'mongodb':
            return [dict(r) for r in self.db.blockchain_index.find()]
        else:
            self.cursor.execute('SELECT * FROM blockchain_index ORDER BY block_index')
            return [dict(row) for row in self.cursor.fetchall()]
    
    # Analytics
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        if self.db_type == 'mongodb':
            return {
                'total_users': self.db.users.count_documents({}),
                'total_fiscalizers': self.db.users.count_documents({'role': 'fiscalizer'}),
                'total_clients': self.db.users.count_documents({'role': 'client'}),
                'total_indexed_entries': self.db.blockchain_index.count_documents({})
            }
        else:
            stats = {}
            self.cursor.execute('SELECT COUNT(*) as count FROM users')
            stats['total_users'] = self.cursor.fetchone()['count']
            
            self.cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'fiscalizer'")
            stats['total_fiscalizers'] = self.cursor.fetchone()['count']
            
            self.cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'client'")
            stats['total_clients'] = self.cursor.fetchone()['count']
            
            self.cursor.execute('SELECT COUNT(*) as count FROM blockchain_index')
            stats['total_indexed_entries'] = self.cursor.fetchone()['count']
            
            return stats
    
    def close(self):
        """Close database connection"""
        if self.db_type == 'mongodb':
            self.client.close()
        else:
            self.conn.close()


# Singleton instance
_db_instance = None

def get_database(db_type='sqlite', **kwargs) -> Database:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_type, **kwargs)
    return _db_instance
