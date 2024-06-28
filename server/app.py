#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries', methods=['GET', 'POST'])
def bakeries():
    if request.method == 'GET':
        bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
        return make_response(jsonify(bakeries), 200)

    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            return make_response(jsonify({"error": "Missing required fields"}), 400)
        
        new_bakery = Bakery(name=name)
        db.session.add(new_bakery)
        db.session.commit()

        return make_response(jsonify(new_bakery.to_dict()), 201)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    
    bakery = Bakery.query.filter_by(id=id).first()
    
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    if request.method == 'GET':
        bakery_serialized = bakery.to_dict()
        return make_response(jsonify(bakery_serialized), 200)
    
    if request.method == 'PATCH':
        new_name = request.form.get('name')
        if new_name:
            bakery.name = new_name
            db.session.commit()
            return make_response(jsonify(bakery.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "No name provided for update"}), 400)

@app.route('/baked_goods/<int:id>', methods=['GET', 'DELETE'])
def baked_good_by_id(id):
    baked_good = BakedGood.query.get_or_404(id)
    
    if request.method == 'GET':
        return make_response(jsonify(baked_good.to_dict()), 200)
    
    if request.method == 'DELETE':
        db.session.delete(baked_good)
        db.session.commit()
        return make_response(jsonify({'message': 'Baked good successfully deleted'}), 200)

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'GET':
        baked_goods = [bg.to_dict() for bg in BakedGood.query.all()]
        return make_response(jsonify(baked_goods), 200)
    
    if request.method == 'POST':
        name = request.form.get('name')
        bakery_id = request.form.get('bakery_id')
        price = request.form.get('price')

        if not name or not bakery_id or not price:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        new_baked_good = BakedGood(name=name, bakery_id=bakery_id, price=price)
        db.session.add(new_baked_good)
        db.session.commit()

        return make_response(jsonify(new_baked_good.to_dict()), 201)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(jsonify(baked_goods_by_price_serialized), 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if most_expensive:
        most_expensive_serialized = most_expensive.to_dict()
        return make_response(jsonify(most_expensive_serialized), 200)
    else:
        return make_response(jsonify({"error": "No baked goods found"}), 404)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
