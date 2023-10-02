from flask import Flask, jsonify, request, make_response, render_template
from flask_restful import Api, Resource, reqparse
from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskapp.db'
db.init_app(app)
api = Api(app)

@app.route('/')
@app.route('/<int:id>')
def home(id=0):
    return render_template("index.html")

class HeroesResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        hero_list = []
        for hero in heroes:
            hero_data = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            }
            hero_list.append(hero_data)
        return hero_list, 200

class HeroResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            hero_data = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "powers": []
            }
            for hero_power in hero.powers:
                power_data = {
                    "id": hero_power.power.id,
                    "name": hero_power.power.name,
                    "description": hero_power.power.description
                }
                hero_data["powers"].append(power_data)
            return hero_data, 200
        else:
            return {"error": "Hero not found"}, 404

class PowersResource(Resource):
    def get(self):
        powers = Power.query.all()
        power_list = []
        for power in powers:
            power_data = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            power_list.append(power_data)
        return power_list, 200

class PowerResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            power_data = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            return power_data, 200
        else:
            return {"error": "Power not found"}, 404

class PowerUpdateResource(Resource):
    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return {"error": "Power not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("description", type=str, required=True)
        args = parser.parse_args()

        power.description = args["description"]
        db.session.commit()

        power_data = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        return power_data, 200

class HeroPowerResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("strength", type=str, required=True)
        parser.add_argument("power_id", type=int, required=True)
        parser.add_argument("hero_id", type=int, required=True)
        args = parser.parse_args()

        hero = Hero.query.get(args["hero_id"])
        power = Power.query.get(args["power_id"])

        if not hero or not power:
            return {"error": "Hero or Power not found"}, 404

        hero_power = HeroPower(strength=args["strength"], hero=hero, power=power)
        db.session.add(hero_power)
        db.session.commit()

        hero_data = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "powers": []
        }
        for hero_power in hero.powers:
            power_data = {
                "id": hero_power.power.id,
                "name": hero_power.power.name,
                "description": hero_power.power.description
            }
            hero_data["powers"].append(power_data)

        return hero_data, 201

api.add_resource(HeroesResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowersResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(PowerUpdateResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/heropowers')

if __name__ == '__main__':
    app.run(debug=True)
