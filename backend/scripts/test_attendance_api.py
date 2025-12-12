import requests
import sys

def test_api():
    base = "http://127.0.0.1:8000/api/attendance"
    
    print("1. Testing Group List (No filters)...")
    try:
        r = requests.get(f"{base}/groups/")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Count: {len(data)}")
            if len(data) > 0:
                print(f"Sample: {data[0]}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

    print("\n2. Testing Stats (Missing Params)...")
    try:
        r = requests.get(f"{base}/stats/")
        print(f"Status: {r.status_code} (Expected 400)")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api()
