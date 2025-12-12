import requests
import sys

def check_server():
    url = "http://127.0.0.1:8000/api/monitoring/student-contingent/"
    print(f"Testing connectivity to: {url}")
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Server is reachable and returning 200 OK.")
            print("Data preview:", str(response.json())[:100])
        else:
            print(f"FAILURE: Server returned {response.status_code}")
            print(response.text[:200])
    except requests.exceptions.ConnectionError:
        print("CRITICAL FAILURE: Connection Refused. The server is likely NOT running.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_server()
