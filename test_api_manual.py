#!/usr/bin/env python3
"""
Simple test script to verify the API is working with MySQL
"""

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_endpoints():
    """Test basic API endpoints"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("=== API Test Results ===\n")
    
    # Test 1: Get all imoveis
    try:
        response = requests.get(f"{base_url}/imoveis", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f" GET /imoveis - {data['total']} records found")
        else:
            print(f" GET /imoveis failed with status {response.status_code}")
    except Exception as e:
        print(f" GET /imoveis failed: {e}")
    
    # Test 2: Get specific imovel
    try:
        response = requests.get(f"{base_url}/imoveis/1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f" GET /imoveis/1 - Found: {data['data']['logradouro']}")
        else:
            print(f" GET /imoveis/1 failed with status {response.status_code}")
    except Exception as e:
        print(f"GET /imoveis/1 failed: {e}")
    
    # Test 3: Create new imovel
    try:
        new_imovel = {
            "logradouro": "Rua Teste API",
            "tipo_logradouro": "Rua",
            "bairro": "Bairro Teste",
            "cidade": "Cidade Teste",
            "cep": "12345-678",
            "tipo": "apartamento",
            "valor": 350000.00,
            "data_aquisicao": "2024-01-15"
        }
        
        response = requests.post(f"{base_url}/imoveis", 
                               json=new_imovel, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        
        if response.status_code == 201:
            data = response.json()
            print(f" POST /imoveis - Created ID: {data['data']['id']}")
            created_id = data['data']['id']
            
            # Test 4: Update the created imovel
            update_data = {"valor": 375000.00}
            response = requests.put(f"{base_url}/imoveis/{created_id}", 
                                  json=update_data,
                                  headers={'Content-Type': 'application/json'},
                                  timeout=5)
            
            if response.status_code == 200:
                print(f" PUT /imoveis/{created_id} - Updated successfully")
            else:
                print(f" PUT /imoveis/{created_id} failed with status {response.status_code}")
            
            # Test 5: Delete the created imovel
            response = requests.delete(f"{base_url}/imoveis/{created_id}", timeout=5)
            
            if response.status_code == 200:
                print(f" DELETE /imoveis/{created_id} - Deleted successfully")
            else:
                print(f" DELETE /imoveis/{created_id} failed with status {response.status_code}")
                
        else:
            print(f" POST /imoveis failed with status {response.status_code}")
    except Exception as e:
        print(f" API operations failed: {e}")

if __name__ == "__main__":
    print("To test the API, first start the Flask app in another terminal:")
    print("python app.py")
    print("\nThen run this script to test the endpoints.")
    print("\nNote: This script expects the Flask app to be running on http://127.0.0.1:5000")
    
    # Optionally run tests if Flask app is already running
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:5000", timeout=1)
        print("\n🔍 Flask app detected running, running tests...\n")
        test_api_endpoints()
    except:
        print("\n  Flask app not running. Start it first with: python app.py")
