from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import requests  # Add this import to use the requests library

app = Flask(__name__)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Item model for MySQL
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price}

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Get all items
@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])

# Load the Foursquare API key from an environment variable
FOURSQUARE_API_KEY = os.getenv("fsq3/BH4FxUa8FuHEJoz8NPWo9A+xJPo3kmqa+EZQWXuZV4=")
FOURSQUARE_API_URL = "https://api.foursquare.com/v3/places/search"

# Define supported categories (based on Foursquare's categories)
CATEGORIES = {
    "food": "13065",  # General category for food
    "fuel": "17067",  # Gas stations category
    "hotel": "19014",
    "shopping": "18066",
    # Add more categories as needed
}

@app.route('/location-services', methods=['GET'])
def get_location_services():
    # Get the required parameters from the request
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    category = request.args.get('category')

    # Validate input parameters
    if not latitude or not longitude or not category:
        return jsonify({"error": "latitude, longitude, and category are required parameters"}), 400
    if category not in CATEGORIES:
        return jsonify({"error": f"Unsupported category. Supported categories: {list(CATEGORIES.keys())}"}), 400

    # Define the query parameters for the API
    headers = {
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "ll": f"{latitude},{longitude}",
        "categories": CATEGORIES[category],
        "limit": 10,  # Limit results to 10
        "radius": 5000  # Search within 5 km
    }

    # Make the request to Foursquare API
    response = requests.get(FOURSQUARE_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        places = [
            {
                "name": place["name"],
                "address": ", ".join(place["location"].get("formatted_address", "N/A")),
                "distance": place["distance"],
                "category": place["categories"][0]["name"] if place["categories"] else "N/A"
            }
            for place in data["results"]
        ]
        return jsonify(places)
    else:
        return jsonify({"error": "Failed to fetch data from Foursquare"}), response.status_code

# Other endpoints remain unchanged...

if __name__ == '__main__':
    app.run(debug=True)
