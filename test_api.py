#!/usr/bin/env python
"""
Automated unit verification script for TBite Backend API.
Uses only built-in urllib.request and threading to test the server locally on port 5001.
"""

import json
import threading
import time
import urllib.request
import urllib.error
from app import HTTPServer, TBiteRequestHandler

SERVER_PORT = 5001
BASE_URL = f"http://localhost:{SERVER_PORT}"

def run_test_server():
  """Starts server on a distinct port for testing."""
  server_address = ("", SERVER_PORT)
  httpd = HTTPServer(server_address, TBiteRequestHandler)
  httpd.serve_forever()

def make_request(path, method="GET", data=None):
  """Helper to perform requests and return status code, body, and headers."""
  url = f"{BASE_URL}{path}"
  req_data = json.dumps(data).encode("utf-8") if data else None
  req = urllib.request.Request(url, data=req_data, method=method)
  if data:
    req.add_header("Content-Type", "application/json")
  
  try:
    with urllib.request.urlopen(req, timeout=3) as response:
      body = response.read().decode("utf-8")
      return response.status, json.loads(body), response.headers
  except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    try:
      parsed_body = json.loads(body)
    except Exception:
      parsed_body = body
    return e.code, parsed_body, e.headers
  except Exception as e:
    print(f"Network error on request {url}: {e}")
    return 0, str(e), {}

def run_tests():
  print("Starting Automated API verification tests...")
  
  # 1. Test Root Info
  status, body, headers = make_request("/")
  assert status == 200, f"Root failed: status {status}"
  assert "TBite Cafe API Server" in body.get("app", ""), "Root name missing"
  print("  - Root info check passed.")

  # 2. Test GET /api/menu
  status, body, headers = make_request("/api/menu")
  assert status == 200, f"Menu failed: status {status}"
  assert isinstance(body, list), "Menu response should be a list"
  assert len(body) == 7, f"Expected 7 menu items, got {len(body)}"
  # Check CORS
  assert headers.get("Access-Control-Allow-Origin") == "*", "CORS header missing on GET /api/menu"
  print("  - GET /api/menu (length, CORS) passed.")

  # 3. Test GET /api/menu/item-1
  status, body, headers = make_request("/api/menu/item-1")
  assert status == 200, f"Item-1 retrieval failed: status {status}"
  assert body.get("name") == "Artisan Cappuccino", f"Unexpected item name: {body.get('name')}"
  assert len(body["recipe"]["ingredients"]) == 3, "Cappuccino recipe ingredient count mismatch"
  print("  - GET /api/menu/item-1 detail retrieval passed.")

  # 4. Test GET /api/menu/invalid-id (404)
  status, body, headers = make_request("/api/menu/invalid-id")
  assert status == 404, f"Expected 404 for invalid item, got {status}"
  assert "not found" in body.get("error", "").lower(), "Expected not found error message"
  print("  - GET /api/menu/invalid-id (404) passed.")

  # 5. Test GET /api/inventory
  status, body, headers = make_request("/api/inventory")
  assert status == 200, f"Inventory failed: status {status}"
  assert isinstance(body, list), "Inventory should be a list"
  low_stock_items = [i for i in body if i["lowStock"]]
  assert len(low_stock_items) == 3, f"Expected 3 low stock ingredients (Cocoa, Butter, Avocado), got {len(low_stock_items)}"
  print("  - GET /api/inventory (aggregations, low stock checks) passed.")

  # 6. Test POST /api/orders (Valid payload)
  order_payload = {
    "customer_name": "Alice Developer",
    "items": [
      {"item_id": "item-1", "quantity": 2},  # Cappuccino: 4.75 * 2 = 9.50
      {"item_id": "item-4", "quantity": 1}   # Butter Croissant: 3.75 * 1 = 3.75
    ]
  }
  # Total: 13.25, Tax: 1.06, Grand: 14.31
  status, body, headers = make_request("/api/orders", method="POST", data=order_payload)
  assert status == 201, f"Order placement failed: status {status}"
  assert body.get("customer_name") == "Alice Developer", "Customer name mismatch"
  assert body.get("subtotal") == 13.25, f"Subtotal math mismatch: {body.get('subtotal')}"
  assert body.get("tax") == 1.06, f"Tax math mismatch: {body.get('tax')}"
  assert body.get("grand_total") == 14.31, f"Grand total math mismatch: {body.get('grand_total')}"
  assert len(body.get("warnings", [])) == 2, "Expected 2 low stock warnings (Cocoa, Butter)"
  assert headers.get("Access-Control-Allow-Origin") == "*", "CORS header missing on POST"
  print("  - POST /api/orders (valid calculations, warnings, CORS) passed.")

  # 7. Test POST /api/orders (Invalid inputs validation)
  bad_payloads = [
    # Empty customer name
    {
      "customer_name": "   ",
      "items": [{"item_id": "item-1", "quantity": 1}]
    },
    # Missing items list
    {
      "customer_name": "Bob"
    },
    # Empty items list
    {
      "customer_name": "Bob",
      "items": []
    },
    # Negative quantity & nonexistent item
    {
      "customer_name": "Bob",
      "items": [
        {"item_id": "nonexistent", "quantity": 5},
        {"item_id": "item-1", "quantity": -3}
      ]
    }
  ]

  for idx, bad_payload in enumerate(bad_payloads):
    status, body, headers = make_request("/api/orders", method="POST", data=bad_payload)
    assert status == 400, f"Expected 400 for bad payload index {idx}, got {status}"
    assert isinstance(body.get("errors"), list), f"Expected validation error list for payload {idx}"
    assert len(body["errors"]) > 0, f"Expected at least one error message for payload {idx}"
  
  print("  - POST /api/orders (validation checks) passed.")
  print("\nAll automated checks completed successfully!")

if __name__ == "__main__":
  # Run server thread in background
  server_thread = threading.Thread(target=run_test_server, daemon=True)
  server_thread.start()
  
  # Allow server to startup
  time.sleep(1)
  
  try:
    run_tests()
  except AssertionError as err:
    print(f"\nValidation Failure: {err}")
    exit(1)
  except Exception as e:
    print(f"\nUnexpected Error during test execution: {e}")
    exit(1)
  
  print("Stopping verification process...")
  exit(0)
