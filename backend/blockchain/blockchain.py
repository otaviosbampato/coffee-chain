"""
Blockchain Core Module
Improved version with persistent storage
"""

import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Block:
    """Block class for coffee traceability"""
    
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.get_hash()
    
    def get_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary for JSON serialization"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class Blockchain:
    """
    Blockchain with persistent storage
    Automatically saves to disk after each block
    """
    
    def __init__(self, storage_path: str = 'data/blockchain.json'):
        self.storage_path = storage_path
        self.chain: List[Block] = []
        self.difficulty = 2
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Load existing blockchain or create genesis
        if os.path.exists(storage_path):
            self.load_from_file()
            print(f"✓ Loaded blockchain from {storage_path}")
            print(f"  Blocks: {len(self.chain)}")
        else:
            self.create_genesis_block()
            self.save_to_file()
            print(f"✓ Created new blockchain at {storage_path}")
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            data={'type': 'genesis', 'message': 'Coffee Traceability Blockchain Genesis Block'},
            previous_hash='0',
            nonce=0
        )
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_entry(self, entry_data: Dict) -> Dict:
        """
        Add a new coffee traceability entry
        Automatically saves to disk after adding
        """
        latest_block = self.get_latest_block()
        
        # Add metadata
        entry_data['entry_timestamp'] = datetime.now().isoformat()
        entry_data['entry_type'] = 'coffee_entry'
        
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=datetime.now().isoformat(),
            data=entry_data,
            previous_hash=latest_block.hash,
            nonce=0
        )
        
        # Proof of work
        new_block = self.proof_of_work(new_block)
        
        # Validate
        if self.is_valid_new_block(new_block, latest_block):
            self.chain.append(new_block)
            
            # Auto-save to disk
            self.save_to_file()
            
            return {
                'success': True,
                'block': new_block.to_dict(),
                'message': 'Entry added successfully to blockchain'
            }
        else:
            return {
                'success': False,
                'message': 'Invalid block, entry not added'
            }
    
    def proof_of_work(self, block: Block) -> Block:
        """Simple proof of work algorithm"""
        block.nonce = 0
        computed_hash = block.get_hash()
        
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.get_hash()
        
        block.hash = computed_hash
        return block
    
    def is_valid_new_block(self, new_block: Block, previous_block: Block) -> bool:
        """Validate a new block"""
        if previous_block.index + 1 != new_block.index:
            return False
        if previous_block.hash != new_block.previous_hash:
            return False
        if new_block.get_hash() != new_block.hash:
            return False
        if not new_block.hash.startswith('0' * self.difficulty):
            return False
        return True
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.get_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
        
        return True
    
    def get_entry_by_batch(self, batch_id: str) -> Optional[List[Dict]]:
        """Get all entries for a specific coffee batch"""
        results = []
        for block in self.chain[1:]:  # Skip genesis
            if block.data.get('coffee_batch') == batch_id:
                results.append(block.to_dict())
        
        return results if results else None
    
    def get_entry_by_origin(self, origin: str) -> Optional[List[Dict]]:
        """Get all entries from a specific origin"""
        results = []
        for block in self.chain[1:]:
            if block.data.get('origin', '').lower() == origin.lower():
                results.append(block.to_dict())
        
        return results if results else None
    
    def get_all_entries(self) -> List[Dict]:
        """Get all entries in the blockchain"""
        return [block.to_dict() for block in self.chain[1:]]
    
    def get_chain_info(self) -> Dict:
        """Get information about the blockchain"""
        return {
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'is_valid': self.is_chain_valid(),
            'latest_block': self.get_latest_block().to_dict(),
            'storage_path': self.storage_path
        }
    
    def save_to_file(self):
        """Save blockchain to JSON file"""
        try:
            chain_data = {
                'chain': [block.to_dict() for block in self.chain],
                'length': len(self.chain),
                'difficulty': self.difficulty,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(chain_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving blockchain: {str(e)}")
            return False
    
    def load_from_file(self):
        """Load blockchain from JSON file"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)
            
            self.chain = []
            for block_data in chain_data['chain']:
                block = Block(
                    index=block_data['index'],
                    timestamp=block_data['timestamp'],
                    data=block_data['data'],
                    previous_hash=block_data['previous_hash'],
                    nonce=block_data['nonce']
                )
                self.chain.append(block)
            
            if 'difficulty' in chain_data:
                self.difficulty = chain_data['difficulty']
            
            return True
        except Exception as e:
            print(f"Error loading blockchain: {str(e)}")
            return False
    
    def create_backup(self, backup_dir: str = 'data/backups'):
        """Create a timestamped backup of the blockchain"""
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'blockchain_backup_{timestamp}.json')
        
        chain_data = {
            'chain': [block.to_dict() for block in self.chain],
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'backup_created': datetime.now().isoformat()
        }
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2, ensure_ascii=False)
        
        return backup_path


# For backwards compatibility
__all__ = ['Block', 'Blockchain']
