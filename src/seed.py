from src.app import app
from src.models import db, User, Planet, Person, Favorite


def seed():
    with app.app_context():
        db.create_all()

        user = db.session.get(User, 1)
        if not user:
            user = User(id=1, email='abel@ejemplo.com',
                        password='123456', is_active=True)
            db.session.add(user)

        planets_data = [
            {'name': 'Tatooine', 'climate': 'arid', 'population': '200000'},
            {'name': 'Alderaan', 'climate': 'temperate', 'population': '2000000000'},
            {'name': 'Hoth', 'climate': 'frozen', 'population': 'unknown'},
        ]

        people_data = [
            {'name': 'Luke Skywalker', 'gender': 'male', 'birth_year': '19BBY'},
            {'name': 'Leia Organa', 'gender': 'female', 'birth_year': '19BBY'},
            {'name': 'Darth Vader', 'gender': 'male', 'birth_year': '41.9BBY'},
        ]

        planets = []
        for p in planets_data:
            exists = Planet.query.filter_by(name=p['name']).first()
            if not exists:
                exists = Planet(name=p['name'], climate=p.get(
                    'climate'), population=p.get('population'))
                db.session.add(exists)
            planets.append(exists)

        people = []
        for p in people_data:
            exists = Person.query.filter_by(name=p['name']).first()
            if not exists:
                exists = Person(name=p['name'], gender=p.get(
                    'gender'), birth_year=p.get('birth_year'))
                db.session.add(exists)
            people.append(exists)

        db.session.commit()

        if planets:
            first_planet = Planet.query.filter_by(
                name=planets_data[0]['name']).first()
            if first_planet:
                fav = Favorite.query.filter_by(
                    user_id=user.id, planet_id=first_planet.id).first()
                if not fav:
                    fav = Favorite(user_id=user.id, planet_id=first_planet.id)
                    db.session.add(fav)

        if people:
            first_person = Person.query.filter_by(
                name=people_data[0]['name']).first()
            if first_person:
                fav = Favorite.query.filter_by(
                    user_id=user.id, person_id=first_person.id).first()
                if not fav:
                    fav = Favorite(user_id=user.id, person_id=first_person.id)
                    db.session.add(fav)

        db.session.commit()


if __name__ == '__main__':
    seed()
