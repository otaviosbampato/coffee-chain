import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional

# Block class for coffee traceability
class Block:
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.get_hash()
    
    # Creates a sha256 hash, encodes it as utf-8
    def get_hash(self) -> str:
        # json.dumps(..., sort_keys=True) secures consistent alphabetical ordering in keys
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
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_entries: List[Dict] = []
        self.difficulty = 2  # Number of leading zeros required in hash
        self.create_genesis_block()
    
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
        Add a new coffee traceability entry (used by fiscalizers)
        
        Args:
            entry_data: Dictionary containing coffee traceability information
                Example: {
                    'fiscalizer_id': 'FISC001',
                    'coffee_batch': 'BATCH-2025-001',
                    'origin': 'Fazenda Santa Clara',
                    'harvest_date': '2025-10-15',
                    'quality_grade': 'A',
                    'certifications': ['Organic', 'Fair Trade'],
                    'weight_kg': 1000,
                    'processing_method': 'Natural',
                    'notes': 'High quality arabica beans'
                }
        
        Returns:
            Dictionary with the created block information
        """
        latest_block = self.get_latest_block()
        
        # Add timestamp and entry type to data
        entry_data['entry_timestamp'] = datetime.now().isoformat()
        entry_data['entry_type'] = 'coffee_entry'
        
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=datetime.now().isoformat(),
            data=entry_data,
            previous_hash=latest_block.hash,
            nonce=0
        )
        
        # Proof of work (simple implementation)
        new_block = self.proof_of_work(new_block)
        
        # Validate before adding
        if self.is_valid_new_block(new_block, latest_block):
            self.chain.append(new_block)
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
        """
        Simple proof of work algorithm
        Find a nonce value that produces a hash with required difficulty
        """
        block.nonce = 0
        computed_hash = block.get_hash()
        
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.get_hash()
        
        block.hash = computed_hash
        return block
    
    def is_valid_new_block(self, new_block: Block, previous_block: Block) -> bool:
        """Validate a new block before adding it to the chain"""
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
        """
        Validate the entire blockchain
        Returns True if the chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if the hash is correct
            if current_block.hash != current_block.get_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Check proof of work
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
        
        return True
    
    def get_entry_by_batch(self, batch_id: str) -> Optional[List[Dict]]:
        """
        Get all entries for a specific coffee batch (used by clients to check)
        
        Args:
            batch_id: The coffee batch identifier
        
        Returns:
            List of all blocks containing data for the specified batch
        """
        results = []
        for block in self.chain[1:]:  # Skip genesis block
            if block.data.get('coffee_batch') == batch_id:
                results.append(block.to_dict())
        
        return results if results else None
    
    def get_entry_by_origin(self, origin: str) -> Optional[List[Dict]]:
        """
        Get all entries from a specific origin
        
        Args:
            origin: The farm or origin name
        
        Returns:
            List of all blocks from the specified origin
        """
        results = []
        for block in self.chain[1:]:  # Skip genesis block
            if block.data.get('origin', '').lower() == origin.lower():
                results.append(block.to_dict())
        
        return results if results else None
    
    def get_all_entries(self) -> List[Dict]:
        """
        Get all entries in the blockchain (excluding genesis block)
        Used by clients to view all coffee traceability records
        """
        return [block.to_dict() for block in self.chain[1:]]
    
    def get_chain_info(self) -> Dict:
        """Get information about the blockchain"""
        return {
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'is_valid': self.is_chain_valid(),
            'latest_block': self.get_latest_block().to_dict()
        }
    
    def export_chain(self, filename: str = 'blockchain_export.json'):
        """Export the entire blockchain to a JSON file"""
        chain_data = {
            'chain': [block.to_dict() for block in self.chain],
            'length': len(self.chain),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def import_chain(self, filename: str) -> bool:
        """
        Import a blockchain from a JSON file
        Only imports if the chain is valid
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)
            
            # Reconstruct the chain
            imported_chain = []
            for block_data in chain_data['chain']:
                block = Block(
                    index=block_data['index'],
                    timestamp=block_data['timestamp'],
                    data=block_data['data'],
                    previous_hash=block_data['previous_hash'],
                    nonce=block_data['nonce']
                )
                imported_chain.append(block)
            
            # Temporarily replace chain for validation
            original_chain = self.chain
            self.chain = imported_chain
            
            if self.is_chain_valid():
                return True
            else:
                self.chain = original_chain
                return False
                
        except Exception as e:
            print(f"Error importing chain: {str(e)}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Initialize blockchain
    coffee_chain = Blockchain()
    
    print("=== Coffee Traceability Blockchain ===\n")
    print(f"Genesis block created: {coffee_chain.get_latest_block().hash}\n")
    
    # Example: Fiscalizer adds a new coffee entry
    entry1 = {
        'fiscalizer_id': 'FISC001',
        'coffee_batch': 'BATCH-2025-001',
        'origin': 'Fazenda Santa Clara',
        'harvest_date': '2025-10-15',
        'quality_grade': 'A',
        'certifications': ['Organic', 'Fair Trade'],
        'weight_kg': 1000,
        'processing_method': 'Natural',
        'notes': 'High quality arabica beans from high altitude'
    }
    
    result = coffee_chain.add_entry(entry1)
    print(f"Entry 1 added: {result['success']}")
    print(f"Block hash: {result['block']['hash']}\n")
    
    # Add another entry
    entry2 = {
        'fiscalizer_id': 'FISC002',
        'coffee_batch': 'BATCH-2025-002',
        'origin': 'Fazenda Boa Vista',
        'harvest_date': '2025-10-20',
        'quality_grade': 'AA',
        'certifications': ['Organic'],
        'weight_kg': 1500,
        'processing_method': 'Washed',
        'notes': 'Premium quality, specialty grade'
    }
    
    result = coffee_chain.add_entry(entry2)
    print(f"Entry 2 added: {result['success']}")
    print(f"Block hash: {result['block']['hash']}\n")
    
    # Client checks a specific batch
    print("=== Client Query: Check Batch BATCH-2025-001 ===")
    batch_info = coffee_chain.get_entry_by_batch('BATCH-2025-001')
    if batch_info:
        for entry in batch_info:
            print(f"Batch: {entry['data']['coffee_batch']}")
            print(f"Origin: {entry['data']['origin']}")
            print(f"Quality: {entry['data']['quality_grade']}")
            print(f"Hash: {entry['hash']}")
    print()
    
    # Validate blockchain
    print(f"Blockchain is valid: {coffee_chain.is_chain_valid()}")
    print(f"Total blocks: {len(coffee_chain.chain)}")
    
    # Get chain info
    print("\n=== Blockchain Info ===")
    info = coffee_chain.get_chain_info()
    print(f"Length: {info['length']}")
    print(f"Difficulty: {info['difficulty']}")
    print(f"Valid: {info['is_valid']}")
    
    # Export blockchain
    print("\n=== Exporting Blockchain ===")
    export_file = coffee_chain.export_chain('coffee_blockchain.json')
    print(f"Blockchain exported to: {export_file}")