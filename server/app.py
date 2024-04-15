#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def heroes():
    heroes = [hero.to_dict(rules=("-hero_powers",)) for hero in Hero.query.all()]
    response = make_response(
        heroes,
        200
    )
    return response

@app.route('/heroes/<int:id>')
def hero(id):
    hero = Hero.query.filter(Hero.id==id).first()

    if hero  == None:
        response = make_response(
            {"error": "Hero not found"},
            404
        )
        return response
    
    else:
        hero_dict = hero.to_dict()

        response = make_response(
            hero_dict,
            200
        )
        return response
    
#Where do I include sort keys = True    
@app.route('/powers')
def powers():
    powers = [power.to_dict("-hero_powers",) for power in Power.query.all()]

    response = make_response(
        powers,
        200
    )

    return response
    

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power(id):
    power = Power.query.filter(Power.id == id).first()

    if power == None:
        response = make_response(
            {"error": "Power not found"},
            404
        )
        return response
    
    else:
        if request.method == 'GET':
            power_dict = power.to_dict()
            response = (
                power_dict,
                200
            )
            return response
        
        elif request.method == 'PATCH':
            data = request.json
            if 'description' not in data:
                response = make_response(
                    {"errors": "Description is required"},
                    400
                )
                return response
            
            new_description = data['description']

            if len(new_description) < 20:
                response = make_response(
                    {"errors": ["validation errors"]},
                    400
                )
                return response
            
            power.description = new_description
            db.session.commit()

            updated_power = power.to_dict()

            response = (
                updated_power,
                200
            )

            return response
        
@app.route('/hero_powers', methods=['POST'])
def hero_power():
    data = request.get_json()

    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')

    if not all([strength, power_id, hero_id]):
        response = make_response(
            {"errors": ["Missing required fields"]},
            400
        )
        return response
    
    if strength not in ['Strong', 'Weak', 'Average']:
        response = make_response(
            {"errors": ["validation errors"]},
            400
        )
        return response
    
    hero = Hero.query.filter(Hero.id == hero_id).first()
    power = Power.query.filter(Power.id == power_id).first()

    if hero is None or power is None:
        response = make_response(
            {"errors": ["Hero or Power is not found"]},
            404
        )

    hero_power = HeroPower(strength=strength, hero=hero, power=power)

    db.session.add(hero_power)
    db.session.commit()

    hero_power_dict = hero_power.to_dict()
    response = make_response(
        hero_power_dict,
        200
    )
    return response

            

if __name__ == '__main__':
    app.run(port=5555, debug=True)



