# TBite Cafe Backend API

This is a lightweight, zero-dependency REST API for **TBite** (Artisan Café & Recipe Dashboard) written in Python using only standard library components (`http.server`). 

It is completely offline-compatible and requires no external packages to be installed, ensuring reliable, sandboxed operation.

---

## 🚀 Getting Started

Simply run the API server using your local Python installation.

### Run the Server
1. Navigate to the backend directory:
   ```bash
   cd C:\Users\user\.gemini\antigravity\scratch\tbite-api
   ```
2. Start the API server:
   ```bash
   python app.py
   ```
   The server will start listening at `http://localhost:5000`.

---

## 📡 REST API Specifications

All endpoints return JSON and natively support **CORS** headers, allowing connection from frontend single-page web applications.

### 1. GET /api/menu
Retrieves all items available on the café menu.
* **Response `200 OK`**:
  ```json
  [
    {
      "id": "item-1",
      "name": "Artisan Cappuccino",
      "category": "coffee",
      "price": 4.75,
      "tags": ["Hot", "Classic", "Strong Espresso"],
      "description": "...",
      "recipe": { ... }
    }
  ]
  ```

### 2. GET /api/menu/<item_id>
Retrieves detailed information for a single menu item.
* **Success Response `200 OK`**:
  ```json
  {
    "id": "item-1",
    "name": "Artisan Cappuccino",
    "price": 4.75,
    "recipe": { ... }
  }
  ```
* **Error Response `404 Not Found`**:
  ```json
  {
    "error": "Menu item 'invalid-id' not found."
  }
  ```

### 3. GET /api/inventory
Aggregates and exposes the current stock status of unique ingredients across all recipes.
* **Response `200 OK`**:
  ```json
  [
    {
      "name": "Cocoa Dusting",
      "unit": "g",
      "status": "Low Stock",
      "lowStock": true,
      "used_in": ["Artisan Cappuccino"]
    }
  ]
  ```

### 4. POST /api/orders
Places a new order, calculates receipt totals (including 8% tax), and alerts of low-stock ingredients.
* **Request Payload**:
  ```json
  {
    "customer_name": "John Doe",
    "items": [
      {
        "item_id": "item-1",
        "quantity": 2
      },
      {
        "item_id": "item-4",
        "quantity": 1
      }
    ]
  }
  ```
* **Success Response `201 Created`**:
  ```json
  {
    "order_id": "ORD-584729",
    "customer_name": "John Doe",
    "items": [
      {
        "item_id": "item-1",
        "name": "Artisan Cappuccino",
        "price_per_unit": 4.75,
        "quantity": 2,
        "total_price": 9.5
      },
      {
        "item_id": "item-4",
        "name": "Butter Croissant",
        "price_per_unit": 3.75,
        "quantity": 1,
        "total_price": 3.75
      }
    ],
    "subtotal": 13.25,
    "tax": 1.06,
    "grand_total": 14.31,
    "warnings": [
      "Low stock warning: Ingredient 'Cocoa Dusting' in item 'Artisan Cappuccino' is running low.",
      "Low stock warning: Ingredient 'European Butter' in item 'Butter Croissant' is running low."
    ],
    "status": "Confirmed"
  }
  ```
* **Error Response `400 Bad Request`**:
  Returned when input validation fails. Contains a detailed list of syntax and validation errors.
  ```json
  {
    "errors": [
      "Field 'customer_name' cannot be empty or blank spaces.",
      "Item 'quantity' at index 1 must be a positive integer greater than or equal to 1."
    ]
  }
  ```

---

## 🧪 Testing the API

You can verify the API's endpoints using the following two methods:

### Method 1: Automated Test Suite (Python)
An automated test script `test_api.py` is included in the project directory. It launches a local test server and runs comprehensive assertions against all routes and validators.

Run the test suite:
```bash
python test_api.py
```
Expected output:
```text
Starting Automated API verification tests...
  - Root info check passed.
  - GET /api/menu (length, CORS) passed.
  - GET /api/menu/item-1 detail retrieval passed.
  - GET /api/menu/invalid-id (404) passed.
  - GET /api/inventory (aggregations, low stock checks) passed.
  - POST /api/orders (valid calculations, warnings, CORS) passed.
  - POST /api/orders (validation checks) passed.

All automated checks completed successfully!
Stopping verification process...
```

### Method 2: Manual Queries (PowerShell)
You can run these command templates to query the active API server (running on `http://localhost:5000` via `python app.py`) from PowerShell.

#### Test Menu Retrieval
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/menu" -Method GET
```

#### Test Valid Order Creation
```powershell
$body = @{
    customer_name = "Alice Smith"
    items = @(
        @{ item_id = "item-2"; quantity = 2 }
        @{ item_id = "item-5"; quantity = 1 }
    )
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:5000/api/orders" -Method POST -Body $body -ContentType "application/json"
```

#### Test Error Validation Handling
```powershell
$badBody = @{
    customer_name = "   "
    items = @(
        @{ item_id = "invalid-item"; quantity = 0 }
    )
} | ConvertTo-Json -Depth 4

try {
    Invoke-RestMethod -Uri "http://localhost:5000/api/orders" -Method POST -Body $badBody -ContentType "application/json"
} catch {
    $_.Exception.Response.GetResponseStream() | ForEach-Object { 
        (New-Object System.IO.StreamReader($_)).ReadToEnd() 
    }
}
```
