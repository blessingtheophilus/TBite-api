#!/usr/bin/env python
"""
TBite Cafe Backend API
Architecture: Zero-dependency REST API using Python standard library http.server.
Features: REST endpoints, native CORS support, data validation, order calculations.
"""

import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# 1. MOCK MENU DATABASE (Consistent with Frontend Offerings & Recipes)
MENU_DATA = {
  "item-1": {
    "id": "item-1",
    "name": "Artisan Cappuccino",
    "category": "coffee",
    "price": 4.75,
    "tags": ["Hot", "Classic", "Strong Espresso"],
    "description": "Double-shot espresso layered with thick microfoam and lightly dusted with low-stock cocoa dusting.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Espresso Beans", "baseQty": 18, "unit": "g", "lowStock": False},
        {"name": "Whole Milk", "baseQty": 120, "unit": "ml", "lowStock": False},
        {"name": "Cocoa Dusting", "baseQty": 1.5, "unit": "g", "lowStock": True}
      ]
    }
  },
  "item-2": {
    "id": "item-2",
    "name": "Matcha Latte",
    "category": "coffee",
    "price": 5.25,
    "tags": ["Hot or Iced", "Uji Matcha", "Creamy"],
    "description": "Premium Japanese stone-ground matcha whisked creamy with organic oat milk and raw agave nectar.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Uji Matcha Powder", "baseQty": 4, "unit": "g", "lowStock": False},
        {"name": "Oat Milk", "baseQty": 180, "unit": "ml", "lowStock": False},
        {"name": "Agave Nectar", "baseQty": 8, "unit": "ml", "lowStock": False}
      ]
    }
  },
  "item-3": {
    "id": "item-3",
    "name": "Decadent Mocha Macchiato",
    "category": "coffee",
    "price": 5.50,
    "tags": ["Sweet", "Cold Brewed", "Drizzle"],
    "description": "Bold espresso layered with Swiss chocolate syrup, chilled milk, and finished with a dark mocha caramel drizzle.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Espresso Beans", "baseQty": 18, "unit": "g", "lowStock": False},
        {"name": "Chocolate Syrup", "baseQty": 25, "unit": "ml", "lowStock": False},
        {"name": "Whole Milk", "baseQty": 150, "unit": "ml", "lowStock": False},
        {"name": "Caramel Drizzle", "baseQty": 5, "unit": "ml", "lowStock": False}
      ]
    }
  },
  "item-4": {
    "id": "item-4",
    "name": "Butter Croissant",
    "category": "pastries",
    "price": 3.75,
    "tags": ["Bakery", "Butter-rich", "Warm Servings"],
    "description": "Golden, flaky French pastry baked daily with layers of high-quality organic European butter.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Lamination Flour", "baseQty": 45, "unit": "g", "lowStock": False},
        {"name": "European Butter", "baseQty": 32, "unit": "g", "lowStock": True},
        {"name": "Bakers Yeast", "baseQty": 2, "unit": "g", "lowStock": False}
      ]
    }
  },
  "item-5": {
    "id": "item-5",
    "name": "Vanilla Cinnamon Roll",
    "category": "pastries",
    "price": 4.25,
    "tags": ["Sweet", "Glazed", "Soft Baked"],
    "description": "Soft leavened dough swirled with Ceylon cinnamon sugar, topped with rich vanilla bean glaze.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Roll Dough Flour", "baseQty": 55, "unit": "g", "lowStock": False},
        {"name": "Ceylon Cinnamon", "baseQty": 5, "unit": "g", "lowStock": False},
        {"name": "Brown Sugar", "baseQty": 15, "unit": "g", "lowStock": False},
        {"name": "Vanilla Bean Glaze", "baseQty": 20, "unit": "g", "lowStock": False}
      ]
    }
  },
  "item-6": {
    "id": "item-6",
    "name": "Classic Caprese Panini",
    "category": "sandwiches",
    "price": 8.95,
    "tags": ["Fresh Mozzarella", "Pesto", "Toasted"],
    "description": "Artisanal sourdough loaded with thick heirloom tomatoes, fresh basil leaves, and house pine-nut pesto.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Sourdough Slices", "baseQty": 2, "unit": "slices", "lowStock": False},
        {"name": "Buffalo Mozzarella", "baseQty": 65, "unit": "g", "lowStock": False},
        {"name": "Heirloom Tomato", "baseQty": 3, "unit": "slices", "lowStock": False},
        {"name": "Pine-Nut Pesto", "baseQty": 15, "unit": "g", "lowStock": False}
      ]
    }
  },
  "item-7": {
    "id": "item-7",
    "name": "Radish Avocado Toast",
    "category": "sandwiches",
    "price": 9.50,
    "tags": ["Vegan Option", "Superfood", "Zesty"],
    "description": "Rustic whole-grain sourdough topped with hand-smashed Haas avocado, chili flakes, and radish slices.",
    "recipe": {
      "baseServings": 1,
      "ingredients": [
        {"name": "Whole-Grain Bread", "baseQty": 1, "unit": "slice", "lowStock": False},
        {"name": "Haas Avocado", "baseQty": 1.5, "unit": "fruits", "lowStock": True},
        {"name": "Chili Flakes", "baseQty": 1.5, "unit": "g", "lowStock": False},
        {"name": "Radish Garnishment", "baseQty": 10, "unit": "g", "lowStock": False}
      ]
    }
  }
}

# In-memory storage for orders
ORDERS_DATABASE = []

class TBiteRequestHandler(BaseHTTPRequestHandler):
  """Custom Request Handler implementing CORS and API endpoints."""

  def _set_cors_headers(self):
    """Native CORS support settings."""
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")

  def _send_json_response(self, status_code, data):
    """Helper to send unified JSON HTTP response packets."""
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self._set_cors_headers()
    self.end_headers()
    self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

  def do_OPTIONS(self):
    """Handle preflight requests for cross-origin API compliance."""
    self.send_response(200)
    self._set_cors_headers()
    self.end_headers()

  def do_GET(self):
    """Handle all GET requests."""
    parsed_path = urlparse(self.path)
    path_segments = parsed_path.path.strip("/").split("/")

    # Root endpoint info
    if not path_segments or path_segments[0] == "":
      self._send_json_response(200, {
        "app": "TBite Cafe API Server",
        "status": "Online",
        "endpoints": [
          "GET /api/menu",
          "GET /api/menu/<item_id>",
          "GET /api/inventory",
          "POST /api/orders"
        ]
      })
      return

    # Route segment matching
    if path_segments[0] == "api":
      if len(path_segments) > 1:
        endpoint = path_segments[1]
        
        # 1. GET /api/menu
        if endpoint == "menu":
          if len(path_segments) == 2:
            # Return list of all menu items
            menu_list = list(MENU_DATA.values())
            self._send_json_response(200, menu_list)
            return
          elif len(path_segments) == 3:
            # GET /api/menu/<item_id>
            item_id = path_segments[2]
            if item_id in MENU_DATA:
              self._send_json_response(200, MENU_DATA[item_id])
            else:
              self._send_json_response(404, {"error": f"Menu item '{item_id}' not found."})
            return

        # 2. GET /api/inventory
        elif endpoint == "inventory":
          # Aggregate unique ingredients and check stock levels
          inventory = {}
          for item in MENU_DATA.values():
            for ing in item["recipe"]["ingredients"]:
              name = ing["name"]
              if name not in inventory:
                inventory[name] = {
                  "name": name,
                  "unit": ing["unit"],
                  "status": "Low Stock" if ing["lowStock"] else "OK",
                  "lowStock": ing["lowStock"],
                  "used_in": []
                }
              if item["name"] not in inventory[name]["used_in"]:
                inventory[name]["used_in"].append(item["name"])
          
          self._send_json_response(200, list(inventory.values()))
          return

    # Fallback to 404 for unknown endpoints
    self._send_json_response(404, {"error": "Endpoint not found."})

  def do_POST(self):
    """Handle all POST requests."""
    parsed_path = urlparse(self.path)
    path_segments = parsed_path.path.strip("/").split("/")

    if path_segments == ["api", "orders"]:
      # Read JSON post body
      content_length = int(self.headers.get('Content-Length', 0))
      if content_length == 0:
        self._send_json_response(400, {"errors": ["Empty request body."]})
        return
      
      raw_post_data = self.rfile.read(content_length)
      try:
        post_data = json.loads(raw_post_data.decode("utf-8"))
      except json.JSONDecodeError:
        self._send_json_response(400, {"errors": ["Invalid JSON syntax in request body."]})
        return

      # --- INPUT VALIDATION LAYER ---
      errors = []
      
      # 1. Validate customer name
      customer_name = post_data.get("customer_name")
      if customer_name is None:
        errors.append("Field 'customer_name' is missing.")
      elif not isinstance(customer_name, str):
        errors.append("Field 'customer_name' must be a string.")
      elif not customer_name.strip():
        errors.append("Field 'customer_name' cannot be empty or blank spaces.")

      # 2. Validate ordered items
      ordered_items = post_data.get("items")
      if ordered_items is None:
        errors.append("Field 'items' list is missing.")
      elif not isinstance(ordered_items, list):
        errors.append("Field 'items' must be a JSON array (list).")
      elif len(ordered_items) == 0:
        errors.append("Field 'items' must contain at least one menu selection.")
      else:
        # Validate elements inside list
        for index, entry in enumerate(ordered_items):
          if not isinstance(entry, dict):
            errors.append(f"Item entry at index {index} must be an object.")
            continue
          
          item_id = entry.get("item_id")
          quantity = entry.get("quantity")

          # Validate item_id
          if item_id is None:
            errors.append(f"Item entry at index {index} is missing 'item_id'.")
          elif not isinstance(item_id, str):
            errors.append(f"Item 'item_id' at index {index} must be a string.")
          elif item_id not in MENU_DATA:
            errors.append(f"Item 'item_id' '{item_id}' at index {index} does not exist in our menu database.")

          # Validate quantity
          if quantity is None:
            errors.append(f"Item entry at index {index} is missing 'quantity'.")
          # Must be numeric (specifically check for bool since isinstance(True, int) is True)
          elif isinstance(quantity, bool) or not isinstance(quantity, int):
            errors.append(f"Item 'quantity' at index {index} must be an integer.")
          elif quantity < 1:
            errors.append(f"Item 'quantity' at index {index} must be a positive integer greater than or equal to 1.")

      # Return errors if validation failed
      if errors:
        self._send_json_response(400, {"errors": errors})
        return

      # --- ORDER PROCESSING & RECEIPT CALCULATION ---
      processed_items = []
      subtotal = 0.0
      warnings = []

      for entry in ordered_items:
        item_id = entry["item_id"]
        qty = entry["quantity"]
        db_item = MENU_DATA[item_id]
        
        # Check stock validation for low items
        for ing in db_item["recipe"]["ingredients"]:
          if ing["lowStock"]:
            warn_msg = f"Low stock warning: Ingredient '{ing['name']}' in item '{db_item['name']}' is running low."
            if warn_msg not in warnings:
              warnings.append(warn_msg)

        item_total = db_item["price"] * qty
        subtotal += item_total
        processed_items.append({
          "item_id": item_id,
          "name": db_item["name"],
          "price_per_unit": db_item["price"],
          "quantity": qty,
          "total_price": round(item_total, 2)
        })

      tax = subtotal * 0.08
      grand_total = subtotal + tax

      receipt = {
        "order_id": f"ORD-{random.randint(100000, 999999)}",
        "customer_name": customer_name.strip(),
        "items": processed_items,
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "grand_total": round(grand_total, 2),
        "warnings": warnings,
        "status": "Confirmed"
      }

      ORDERS_DATABASE.append(receipt)
      self._send_json_response(201, receipt)
      return

    # Fallback to 404 for unknown post routes
    self._send_json_response(404, {"error": "Endpoint not found."})

def run_server(port=5000):
  """Starts the zero-dependency REST API server."""
  server_address = ("", port)
  httpd = HTTPServer(server_address, TBiteRequestHandler)
  print(f"🚀 TBite Backend API running offline at http://localhost:{port} ...")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print("\n🛑 Server shutting down gracefully...")
    httpd.server_close()

if __name__ == "__main__":
  run_server()
