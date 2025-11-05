"""
Example: Using the Blockchain Programmatically
This demonstrates how to use the blockchain directly in Python code
"""

from blockchain import Blockchain
from datetime import datetime

def example_fiscalizer_workflow():
    """Example workflow for a fiscalizer adding entries"""
    
    print("=" * 70)
    print("FISCALIZER WORKFLOW - Adding Coffee Entries to Blockchain")
    print("=" * 70)
    
    # Initialize blockchain
    coffee_chain = Blockchain()
    print(f"\n✓ Blockchain initialized")
    print(f"  Genesis block hash: {coffee_chain.get_latest_block().hash[:16]}...")
    
    # Entry 1: High-quality organic coffee
    print("\n" + "-" * 70)
    print("Adding Entry 1: Organic Coffee from Fazenda Santa Clara")
    print("-" * 70)
    
    entry1 = {
        'fiscalizer_id': 'FISC001',
        'coffee_batch': 'BATCH-2025-SC-001',
        'origin': 'Fazenda Santa Clara',
        'location': 'Minas Gerais, Brazil',
        'harvest_date': '2025-10-15',
        'quality_grade': 'AA',
        'certifications': ['Organic', 'Fair Trade', 'Rainforest Alliance'],
        'weight_kg': 1500,
        'processing_method': 'Washed',
        'variety': 'Arabica - Bourbon',
        'altitude_meters': 1200,
        'notes': 'High quality arabica beans from high altitude region. Excellent cup profile.'
    }
    
    result1 = coffee_chain.add_entry(entry1)
    
    if result1['success']:
        print(f"✓ Entry added successfully")
        print(f"  Block Index: {result1['block']['index']}")
        print(f"  Block Hash: {result1['block']['hash'][:32]}...")
        print(f"  Nonce: {result1['block']['nonce']}")
        print(f"  Timestamp: {result1['block']['timestamp']}")
    
    # Entry 2: Natural processed coffee
    print("\n" + "-" * 70)
    print("Adding Entry 2: Natural Coffee from Fazenda Boa Vista")
    print("-" * 70)
    
    entry2 = {
        'fiscalizer_id': 'FISC002',
        'coffee_batch': 'BATCH-2025-BV-001',
        'origin': 'Fazenda Boa Vista',
        'location': 'São Paulo, Brazil',
        'harvest_date': '2025-10-20',
        'quality_grade': 'A',
        'certifications': ['Organic'],
        'weight_kg': 2000,
        'processing_method': 'Natural',
        'variety': 'Arabica - Catuai',
        'altitude_meters': 1000,
        'notes': 'Natural process creates fruity, wine-like notes. Specialty grade.'
    }
    
    result2 = coffee_chain.add_entry(entry2)
    
    if result2['success']:
        print(f"✓ Entry added successfully")
        print(f"  Block Index: {result2['block']['index']}")
        print(f"  Block Hash: {result2['block']['hash'][:32]}...")
        print(f"  Nonce: {result2['block']['nonce']}")
    
    # Entry 3: Honey processed coffee
    print("\n" + "-" * 70)
    print("Adding Entry 3: Honey Coffee from Fazenda Sol Nascente")
    print("-" * 70)
    
    entry3 = {
        'fiscalizer_id': 'FISC001',
        'coffee_batch': 'BATCH-2025-SN-001',
        'origin': 'Fazenda Sol Nascente',
        'location': 'Espírito Santo, Brazil',
        'harvest_date': '2025-10-25',
        'quality_grade': 'AA',
        'certifications': ['Organic', 'UTZ Certified'],
        'weight_kg': 1800,
        'processing_method': 'Honey',
        'variety': 'Arabica - Acaiá',
        'altitude_meters': 1100,
        'notes': 'Honey process provides balanced sweetness and body.'
    }
    
    result3 = coffee_chain.add_entry(entry3)
    
    if result3['success']:
        print(f"✓ Entry added successfully")
        print(f"  Block Index: {result3['block']['index']}")
        print(f"  Block Hash: {result3['block']['hash'][:32]}...")
    
    return coffee_chain


def example_client_workflow(coffee_chain):
    """Example workflow for a client querying entries"""
    
    print("\n\n" + "=" * 70)
    print("CLIENT WORKFLOW - Querying Coffee Traceability Data")
    print("=" * 70)
    
    # Query 1: Get specific batch
    print("\n" + "-" * 70)
    print("Query 1: Check specific batch (BATCH-2025-SC-001)")
    print("-" * 70)
    
    batch_data = coffee_chain.get_entry_by_batch('BATCH-2025-SC-001')
    
    if batch_data:
        for entry in batch_data:
            data = entry['data']
            print(f"\n✓ Batch Found: {data['coffee_batch']}")
            print(f"  Origin: {data['origin']}")
            print(f"  Location: {data['location']}")
            print(f"  Quality Grade: {data['quality_grade']}")
            print(f"  Weight: {data['weight_kg']} kg")
            print(f"  Processing: {data['processing_method']}")
            print(f"  Variety: {data['variety']}")
            print(f"  Certifications: {', '.join(data['certifications'])}")
            print(f"  Verified by: {data['fiscalizer_id']}")
            print(f"  Blockchain Hash: {entry['hash'][:32]}...")
    else:
        print("✗ Batch not found")
    
    # Query 2: Get all entries from specific origin
    print("\n" + "-" * 70)
    print("Query 2: Get all coffee from 'Fazenda Boa Vista'")
    print("-" * 70)
    
    origin_data = coffee_chain.get_entry_by_origin('Fazenda Boa Vista')
    
    if origin_data:
        print(f"\n✓ Found {len(origin_data)} batch(es) from this origin:")
        for entry in origin_data:
            data = entry['data']
            print(f"\n  Batch: {data['coffee_batch']}")
            print(f"  Harvest Date: {data['harvest_date']}")
            print(f"  Weight: {data['weight_kg']} kg")
            print(f"  Quality: {data['quality_grade']}")
    else:
        print("✗ No entries found from this origin")
    
    # Query 3: Get all entries
    print("\n" + "-" * 70)
    print("Query 3: Get all coffee entries in blockchain")
    print("-" * 70)
    
    all_entries = coffee_chain.get_all_entries()
    print(f"\n✓ Total entries in blockchain: {len(all_entries)}")
    
    print("\nSummary of all batches:")
    for entry in all_entries:
        data = entry['data']
        print(f"  • {data['coffee_batch']:20} | {data['origin']:30} | {data['quality_grade']:3} | {data['weight_kg']:5} kg")
    
    # Query 4: Validate blockchain integrity
    print("\n" + "-" * 70)
    print("Query 4: Validate Blockchain Integrity")
    print("-" * 70)
    
    is_valid = coffee_chain.is_chain_valid()
    info = coffee_chain.get_chain_info()
    
    if is_valid:
        print(f"\n✓ Blockchain is VALID and secure")
    else:
        print(f"\n✗ WARNING: Blockchain has been tampered with!")
    
    print(f"  Total blocks: {info['length']}")
    print(f"  Difficulty level: {info['difficulty']}")
    print(f"  Latest block hash: {info['latest_block']['hash'][:32]}...")


def example_blockchain_export(coffee_chain):
    """Example of exporting blockchain to JSON"""
    
    print("\n\n" + "=" * 70)
    print("EXPORT - Saving Blockchain to File")
    print("=" * 70)
    
    filename = f"coffee_blockchain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    exported_file = coffee_chain.export_chain(filename)
    
    print(f"\n✓ Blockchain exported successfully")
    print(f"  Filename: {exported_file}")
    print(f"  Total blocks: {len(coffee_chain.chain)}")
    print(f"  File can be imported later to restore the blockchain")


def example_tamper_detection():
    """Example showing how the blockchain detects tampering"""
    
    print("\n\n" + "=" * 70)
    print("SECURITY DEMO - Tamper Detection")
    print("=" * 70)
    
    # Create a new blockchain with an entry
    demo_chain = Blockchain()
    
    entry = {
        'fiscalizer_id': 'FISC001',
        'coffee_batch': 'BATCH-TEST-001',
        'origin': 'Test Farm',
        'harvest_date': '2025-11-01',
        'quality_grade': 'A',
        'weight_kg': 1000,
        'processing_method': 'Washed'
    }
    
    demo_chain.add_entry(entry)
    
    print("\n1. Original blockchain state:")
    print(f"   ✓ Blockchain is valid: {demo_chain.is_chain_valid()}")
    print(f"   Block 1 hash: {demo_chain.chain[1].hash[:32]}...")
    
    # Attempt to tamper with the data
    print("\n2. Attempting to tamper with data...")
    print("   (Changing quality grade from 'A' to 'AA')")
    demo_chain.chain[1].data['quality_grade'] = 'AA'
    
    print("\n3. After tampering:")
    print(f"   ✗ Blockchain is valid: {demo_chain.is_chain_valid()}")
    print("   ⚠️  Tamper detected! Hash no longer matches.")
    print("   This demonstrates blockchain's security - any change is detected!")


if __name__ == "__main__":
    # Run the complete example
    
    # 1. Fiscalizer adds entries
    blockchain = example_fiscalizer_workflow()
    
    # 2. Client queries entries
    example_client_workflow(blockchain)
    
    # 3. Export blockchain
    example_blockchain_export(blockchain)
    
    # 4. Demonstrate tamper detection
    example_tamper_detection()
    
    print("\n\n" + "=" * 70)
    print("EXAMPLE COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run 'python3 api_blockchain.py' to start the REST API")
    print("  2. Run 'python3 test_api.py' to test the API endpoints")
    print("  3. See INTEGRATION_GUIDE.md for full integration details")
    print("=" * 70 + "\n")
