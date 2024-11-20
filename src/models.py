from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    favorites = db.relationship('Favorite', back_populates='user')

    
    def __repr__(self):
        return '<User %r>' % self.id
    



    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites": list(map(lambda favorites: favorites.serialize(), self.favorites))
        }


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.String(100))
    gender = db.Column(db.String(100), nullable=True)
    hair_color = db.Column(db.String(100), nullable=False)
    eye_color = db.Column(db.String(100))
    favorites = db.relationship('Favorite', back_populates='character')

    def __repr__(self):
        return '<Character %r>' % self.id


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    diameter = db.Column(db.String(100))
    population = db.Column(db.String(100))
    terrain = db.Column(db.String(100))
    favorites = db.relationship('Favorite', back_populates='planet')


    def __repr__(self):
        return '<Planet %r>' % self.id


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "terrain": self.terrain
        }

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100))
    model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    favorites = db.relationship('Favorite', back_populates='vehicle')


    def __repr__(self):
        return '<Vehicle %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "model": self.model,
            "manufacturer": self.manufacturer,
            
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True)
    user = db.relationship('User', back_populates='favorites')
    character = db.relationship('Character', back_populates='favorites')
    planet = db.relationship('Planet', back_populates='favorites')
    vehicle = db.relationship('Vehicle', back_populates='favorites')


    def __repr__(self):
        return '<Favorite %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
            "vehicle_id": self.vehicle_id
        }