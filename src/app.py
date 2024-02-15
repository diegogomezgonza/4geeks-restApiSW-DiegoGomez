"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# Para los endpoint que reciben toda la información, he creado rutas con el mismo nombre
# que tiene SWAPI. Para recuperar todo el contenido de cada modelo, hago nombre.all(), una consulta
# la cual devuelve todo el contenido que esté en cada tabla de la bd.
# En los modelos, uso serialize para poder manipular todos los campos de las clases, de 
# forma que a la hora de recorrer las clases lo hago llamando a serialize y después recorriendo
# todos los campos con un for. Por último, paso a json los campos.

# Todos los personajes
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    serialized_people = [people.serialize() for people in people] 
    return jsonify(serialized_people), 200

# Todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify(serialized_planets), 200

# Todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]
    return jsonify(serialized_users), 200

# En el caso de los favoritos, aunque sigue siendo una consulta .all, como lo que quiero
# son todos los favoritos de un usuario concreto, hago otra consulta llamada filter_by, la cual
# me sirve para mostrar el contenido que quiero (Favorite) filtrándolo por lo que yo indique (el id de usuario)

# Los favoritos de un user concreto
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # ID del usuario
    user_id = 1 

    # Para mostrar los favoritos de un usuario en concreto, filtro los favoritos por el id del usuario
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    # Para enviar los favoritos en un formato JSON, serializo 
    serialized_favorites = [favorite.serialize() for favorite in favorites]

    return jsonify(serialized_favorites), 200

# Para sacar la información de un planeta o personaje individualmente, en la ruta añado
# el id del planeta o personaje correspondiente. En vez de hacer una consulta .all, hago una 
# .get, que recoge la información del planeta o personaje cuyo id coincida con el que hay en la ruta.
# Si el personaje o planeta es igual a null (no existe) aparecerá un mensaje.

# La información de un personaje
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    people = People.query.get(people_id)
    if people is None:
        raise APIException("El personaje no existe", status_code=404)
    return jsonify(people.serialze()), 200

#La información de un planeta
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("El planeta no existe", status_code=404)
    return jsonify(planet.serialize()), 200


# A la hora de añadir un favorito, la ruta empieza con favorite, el tipo de favorito a almacenar y el id
# del planeta o personaje. A la hora de añadir el favorito a la clase, añado el id del usuario actual
# y el id del planeta o personaje según corresponda. 
# Con session.add le indico a la bd que quiero insertar el contenido especificado una vez se haya hecho el commit
# de la siguiente línea. Si el añadido funciona, se muestra un mensaje.

# Añadir un personaje favorito al usuario
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    # Id de usuario
    user_id = 1 
    # Creación del favorito según del id
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Personaje añadido"}), 201

# Añadir un nuevo planeta favorito al usuario
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # Id de usuario
    user_id = 1 
    # Creación del favorito según del id
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Planeta añadido"}), 201

# El procedimiento para borrar el favorito, tiene la misma ruta y logica a la hora de usar
# el id del usuario, lo que cambia es el método y la consulta.
# Con filter_by, busco el id del planeta o personaje recibido en la ruta y lo busco en la tabla
# favorite del usuario. Con first puedo hacer una "condición" en la cual devuelve el id especificado
# y si no se encuentra entonces devuelve None, lo cual me ayuda para la condición que hago después 
# la cual según el valor de favorite hace el delete o no (if favorite sería cuando su valor es el id).

# Borrar un planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # Id de usuario
    user_id = 1
    # Eliminación del favorito según del id el id de usuario
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planeta favorito eliminado"}), 200
    else:
        raise APIException("El planeta no existe", status_code=404)

# Borrar un personaje favorito
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    # Assume the current user is retrieved from the request context or session
    user_id = 1 
    # Eliminación del favorito según del id el id de usuario
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Personaje favorito eliminado"}), 200
    else:
        raise APIException("El personaje no existe", status_code=404)
    
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)