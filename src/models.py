from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# A la hora de hacer los modelos de People y Planets, me he basado en las propiedades que mostraba
# en mi proyecto.
    
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50))
    hair_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    height = db.Column(db.Integer)
    homeworld = db.Column(db.String(50))
    birth_year = db.Column(db.String(50))
    skin_color = db.Column(db.String(50))
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "height": self.height,
            "homeworld": self.homeworld,
            "birth_year": self.birth_year,
            "skin_color": self.skin_color
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    population = db.Column(db.String(50))
    diameter = db.Column(db.String(50))
    gravity = db.Column(db.String(50))
    climate = db.Column(db.String(50))
    orbital_period = db.Column(db.String(50))
    surface_water = db.Column(db.String(50))
    rotation_period = db.Column(db.String(50))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "climate": self.climate,
            "orbital_period": self.orbital_period,
            "surface_water": self.surface_water,
            "rotation_period": self.rotation_period
        }

 # Las tres relaciones son de muchos a uno
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Relación con la tabla User usando la columna 'id'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Relación con la tabla Planet usando la columna 'id'
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    # Relación con la tabla People usando la columna 'id'
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id
        }