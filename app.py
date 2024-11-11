from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

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

# Get a specific item by ID
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get(item_id)
    return jsonify(item.to_dict()) if item else {"error": "Item not found"}, 404

# Create a new item
@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    new_item = Item(name=data['name'], price=data['price'])
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

# Update an existing item
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get(item_id)
    if item is None:
        return {"error": "Item not found"}, 404
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.price = data.get('price', item.price)
    db.session.commit()
    return jsonify(item.to_dict())

# Delete an item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item is None:
        return {"error": "Item not found"}, 404
    db.session.delete(item)
    db.session.commit()
    return {"message": "Item deleted"}, 204

if __name__ == '__main__':
    app.run(debug=True)
