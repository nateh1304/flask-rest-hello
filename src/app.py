"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite, Character, Planet, Vehicle


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/get/initial', methods=['GET'])
def get_data():
    if not Character.query.all():
        characters_url = 'https://swapi.dev/api/people'
        characters_response = requests.get(characters_url).json()

        for elm in characters_response['results']: 
            new_character = Character(name=elm["name"], height=elm["height"], gender=elm["gender"], hair_color=elm["hair_color"], eye_color=elm["eye_color"])
            db.session.add(new_character)
            db.session.commit()

        
        vehicles_url = 'https://swapi.dev/api/vehicles'
        vehicles_response = requests.get(vehicles_url).json()

        for elm in vehicles_response['results']:  
            new_vehicle = Vehicle(name=elm["name"], model=elm["model"], manufacturer=elm["manufacturer"])
            db.session.add(new_vehicle)
            db.session.commit()

        
        planets_url = 'https://swapi.dev/api/planets'
        planets_response = requests.get(planets_url).json()

        for elm in planets_response['results']: 
            new_planet = Planet(name=elm["name"], diameter=elm["diameter"], population=elm["population"], terrain=elm["terrain"])
            db.session.add(new_planet)
            db.session.commit()
        
    planets_records = Planet.query.all()
    char_records = Character.query.all()
    vehicles_records = Vehicle.query.all()

    return jsonify(
        {
            "char_records":  list(map(lambda x: x.serialize(), char_records)),
            "vehicles_records": list(map(lambda x: x.serialize(), vehicles_records)),
            "planets_records": list(map(lambda x: x.serialize(),  planets_records)),
        }
            ), 200
    


@app.route('/users', methods=['GET'])
def handle_users():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    return jsonify({"results": users_list}), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def handle_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    favorites_list = [fav.serialize() for fav in user.favorites]
    return jsonify({"results": favorites_list}), 200

@app.route('/characters', methods=['GET'])
def handle_characters():
    characters = Character.query.all()
    characters_list = [char.serialize() for char in characters]
    return jsonify({"results": characters_list}), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def handle_single_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    return jsonify({"results": character.serialize()}), 200


@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planet.query.all()
    planets_list = [planet.serialize() for planet in planets]
    
    return jsonify({"results": planets_list}), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify({"results": planet.serialize()}), 200

@app.route('/vehicles/<int:id>', methods=['GET'])
def handle_single_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if vehicle is None:
        return jsonify({"error": "Vehicle not found"}), 404
    return jsonify({"results": vehicle.serialize()}), 200


@app.route('/users', methods=['POST'])
def add_users():
    body= request.json
    new_user = User(username=body["username"], email= body["email"], password= body["password"])
    db.session.add(new_user)
    db.session.commit()

    user_created = User.query.filter_by(username=body["username"]).first()
    if user_created:
        return jsonify(user_created.serialize()), 201
    else: return jsonify("User was not created"), 500


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get("user_id")
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({"error": "User or planet not found"}), 404
    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"results": "Planet added to favorites"}), 201


@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    user_id = request.json.get("user_id")
    user = User.query.get(user_id)
    character = Character.query.get(character_id)
    if not user or not character:
        return jsonify({"error": "User or character not found"}), 404
    new_favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"results": "Character added to favorites"}), 201

@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['POST'])
def add_favorite_vehicle(vehicle_id):
    user_id = request.json.get("user_id")
    user = User.query.get(user_id)
    vehicle = Vehicle.query.get(vehicle_id)
    if not user or not vehicle:
        return jsonify({"error": "User or vehicle not found"}), 404
    new_favorite = Favorite(user_id=user_id, vehicle_id=vehicle_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"results": "Vehicle added to favorites"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = request.json.get("user_id")
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"results": "Favorite planet removed"}), 200


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def remove_favorite_character(character_id):
    user_id = request.json.get("user_id")
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"results": "Favorite character removed"}), 200


@app.route('/vehicles', methods=['GET'])
def handle_vehicles():
    vehicles = Vehicle.query.all()
    vehicles_list = [vehicle.serialize() for vehicle in vehicles]
    return jsonify({"results": vehicles_list}), 200


@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['DELETE'])
def remove_favorite_vehicle(vehicle_id):
    user_id = request.json.get("user_id")
    favorite = Favorite.query.filter_by(user_id=user_id, vehicle_id=vehicle_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"results": "Favorite vehicle removed"}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
