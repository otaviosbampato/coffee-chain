"""
Test script for Coffee Traceability Blockchain API
Demonstrates how to interact with the API
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """Helper function to print formatted responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_api():
    """Test the complete API flow"""
    
    print("\n🚀 Testing Coffee Traceability Blockchain API\n")
    
    # 1. Login as fiscalizer
    print("\n1️⃣ Testing Fiscalizer Login...")
    login_data = {
        "username": "fiscalizer1",
        "password": "fisc123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Fiscalizer Login", response)
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
    
    fiscalizer_token = response.json()['token']
    fiscalizer_headers = {"Authorization": f"Bearer {fiscalizer_token}"}
    
    # 2. Login as client
    print("\n2️⃣ Testing Client Login...")
    client_login_data = {
        "username": "client1",
        "password": "client123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=client_login_data)
    print_response("Client Login", response)
    
    client_token = response.json()['token']
    client_headers = {"Authorization": f"Bearer {client_token}"}
    
    # 3. Fiscalizer creates first entry
    print("\n3️⃣ Testing Create Entry (Fiscalizer)...")
    entry1 = {
        "coffee_batch": "BATCH-2025-TEST-001",
        "origin": "Fazenda São José",
        "harvest_date": "2025-11-01",
        "quality_grade": "AA",
        "certifications": ["Organic", "Fair Trade", "Rainforest Alliance"],
        "weight_kg": 1500,
        "processing_method": "Washed",
        "notes": "Premium specialty coffee from high altitude region"
    }
    response = requests.post(f"{BASE_URL}/entries", json=entry1, headers=fiscalizer_headers)
    print_response("Create Entry 1", response)
    
    # 4. Fiscalizer creates second entry
    print("\n4️⃣ Testing Create Second Entry...")
    entry2 = {
        "coffee_batch": "BATCH-2025-TEST-002",
        "origin": "Fazenda Boa Vista",
        "harvest_date": "2025-11-03",
        "quality_grade": "A",
        "certifications": ["Organic"],
        "weight_kg": 2000,
        "processing_method": "Natural",
        "notes": "Natural process, fruity notes"
    }
    response = requests.post(f"{BASE_URL}/entries", json=entry2, headers=fiscalizer_headers)
    print_response("Create Entry 2", response)
    
    # 5. Client tries to create entry (should fail)
    print("\n5️⃣ Testing Client Create Entry (Should Fail)...")
    entry3 = {
        "coffee_batch": "BATCH-2025-TEST-003",
        "origin": "Test Farm",
        "harvest_date": "2025-11-04",
        "quality_grade": "B",
        "weight_kg": 500,
        "processing_method": "Honey"
    }
    response = requests.post(f"{BASE_URL}/entries", json=entry3, headers=client_headers)
    print_response("Client Create Entry (Forbidden)", response)
    
    # 6. Get all entries
    print("\n6️⃣ Testing Get All Entries...")
    response = requests.get(f"{BASE_URL}/entries", headers=client_headers)
    print_response("All Entries", response)
    
    # 7. Query specific batch
    print("\n7️⃣ Testing Query by Batch ID...")
    response = requests.get(f"{BASE_URL}/entries/batch/BATCH-2025-TEST-001", headers=client_headers)
    print_response("Query Batch BATCH-2025-TEST-001", response)
    
    # 8. Query by origin
    print("\n8️⃣ Testing Query by Origin...")
    response = requests.get(f"{BASE_URL}/entries/origin/Fazenda São José", headers=client_headers)
    print_response("Query Origin 'Fazenda São José'", response)
    
    # 9. Get blockchain info
    print("\n9️⃣ Testing Get Blockchain Info...")
    response = requests.get(f"{BASE_URL}/blockchain/info", headers=client_headers)
    print_response("Blockchain Info", response)
    
    # 10. Validate blockchain
    print("\n🔟 Testing Blockchain Validation...")
    response = requests.get(f"{BASE_URL}/blockchain/validate", headers=client_headers)
    print_response("Blockchain Validation", response)
    
    # 11. Health check
    print("\n1️⃣1️⃣ Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    print("\n\n✅ API Testing Complete!\n")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server!")
        print("Make sure the API server is running:")
        print("  python3 api_blockchain.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
