"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from src.utils import APIException, generate_sitemap
from src.admin import setup_admin
from src.models import db, User, Person, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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
        "msg": "Hola, esta es la respuesta GET /user"
    }

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    results = [p.serialize() for p in people]
    return jsonify(results), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = db.session.get(Person, people_id)
    if person is None:
        return jsonify({"mensaje": "Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [p.serialize() for p in planets]
    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        return jsonify({"mensaje": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [u.serialize() for u in users]
    return jsonify(results), 200


def get_current_user():
    return db.session.get(User, 1)


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = get_current_user()
    if user is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    favs = Favorite.query.filter_by(user_id=user.id).all()
    out = []
    for f in favs:
        item = f.serialize()
        if f.planet_id:
            planet = db.session.get(Planet, f.planet_id)
            item['item'] = planet.serialize() if planet else None
            item['type'] = 'planet'
        if f.person_id:
            person = db.session.get(Person, f.person_id)
            item['item'] = person.serialize() if person else None
            item['type'] = 'person'
        out.append(item)
    return jsonify(out), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = get_current_user()
    if user is None:
        return jsonify({"message": "Current user not found"}), 404
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        return jsonify({"mensaje": "Planeta no encontrado"}), 404
    existing = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet_id).first()
    if existing:
        return jsonify({"mensaje": "Agregado en favoritos"}), 400
    fav = Favorite(user_id=user.id, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user = get_current_user()
    if user is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    person = db.session.get(Person, people_id)
    if person is None:
        return jsonify({"mensaje": "Personaje no encontrado"}), 404
    existing = Favorite.query.filter_by(
        user_id=user.id, person_id=people_id).first()
    if existing:
        return jsonify({"mensaje": "Agregado en favoritos"}), 400
    fav = Favorite(user_id=user.id, person_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user = get_current_user()
    if user is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    fav = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"mensaje": "Favorito no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({}), 204


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user = get_current_user()
    if user is None:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    fav = Favorite.query.filter_by(
        user_id=user.id, person_id=people_id).first()
    if not fav:
        return jsonify({"mensaje": "Favorito no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({}), 204


@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({"mensaje": "El nombre es obligatorio"}), 400
    person = Person(name=name, gender=data.get('gender'),
                    birth_year=data.get('birth_year'))
    db.session.add(person)
    db.session.commit()
    return jsonify(person.serialize()), 201


@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = db.session.get(Person, people_id)
    if person is None:
        return jsonify({"mensaje": "Personaje no encontrado"}), 404
    data = request.get_json() or {}
    if 'name' in data:
        person.name = data.get('name')
    if 'gender' in data:
        person.gender = data.get('gender')
    if 'birth_year' in data:
        person.birth_year = data.get('birth_year')
    db.session.add(person)
    db.session.commit()
    return jsonify(person.serialize()), 200


@app.route('/people/<int:people_id>', methods=['DELETE'])
def remove_person(people_id):
    person = db.session.get(Person, people_id)
    if person is None:
        return jsonify({"mensaje": "Personaje no encontrado"}), 404
    db.session.delete(person)
    db.session.commit()
    return jsonify({}), 204


@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({"mensaje": "El nombre es obligatorio"}), 400
    planet = Planet(name=name, climate=data.get('climate'),
                    population=data.get('population'))
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201


@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        return jsonify({"mensaje": "Planeta no encontrado"}), 404
    data = request.get_json() or {}
    if 'name' in data:
        planet.name = data.get('name')
    if 'climate' in data:
        planet.climate = data.get('climate')
    if 'population' in data:
        planet.population = data.get('population')
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 200


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def remove_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        return jsonify({"mensaje": "Planeta no encontrado"}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({}), 204


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
