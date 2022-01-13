from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice
from sqlalchemy.sql import func
import os

random = choice

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
my_api_key = os.environ.get("MY_API_KEY")

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite://cafes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#uses dictoinary comprehension to create dictionary from random cafe
def to_dict(self):
    return {column.name: getattr(self, column.name) for column in self.__table__.columns}


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=True, default=False, server_default="false")
    has_wifi = db.Column(db.Boolean, nullable=True, default=False, server_default="false")
    has_sockets = db.Column(db.Boolean, nullable=True, default=False, server_default="false")
    can_take_calls = db.Column(db.Boolean, nullable=True, default=False, server_default="false")
    coffee_price = db.Column(db.String(250), nullable=True)

db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record single cafe
@app.route(f"/random", methods=["GET"])
def random_choice():
    random_cafe = Cafe.query.order_by(func.random()).first()
    print(random_cafe.name)
    return jsonify(to_dict(random_cafe))

## HTTP Get all cafes
@app.route('/all', methods=['GET'])
def all():
    cafes = []
    # key = request.args.get('key')
    # if key == my_api_key:
    all_cafes = db.session.query(Cafe).all()
    for x in range(len(all_cafes)):
        cafe = Cafe.query.get(x+1)
        cafes.append(to_dict(cafe))
    return jsonify(cafes)
    # else:
    #     return jsonify(error={"No Access": " Sorry you do not have access to this feature"})

@app.route('/cafes', methods=["GET"])
def cafes():
    cafes = []
    key = request.args.get('key')
    if key == my_api_key:
        all_cafes = db.session.query(Cafe).all()
        for x in range(len(all_cafes)):
            cafe = Cafe.query.get(x+1)
            cafes.append(to_dict(cafe))
        return render_template('cafes.html', cafes=cafes)
    else:
        return jsonify(error={"No Access": " Sorry you do not have access to this feature"})

##Search for a a coffee shop by lat and lon
@app.route('/search')
def search():
    key = request.args.get('key')
    query_location = request.args.get('loc')
    if key == my_api_key:
        cafe_search = db.session.query(Cafe).filter_by(location=query_location).all()
        cafe_list = [to_dict(cafe) for cafe in cafe_search]
        if len(cafe_list) == 0:
            return jsonify(error={"Not Found": "Sorry no cafes in that area"})
        else:
            return jsonify(cafe=cafe_list)
    else:
        return jsonify(error={"No Access": " Sorry you do not have access to this feature"})

## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    # key = request.args.get('key')
    # if key == my_api_key:
    if request.method == "POST":
        if request.form.get('has_toilet').strip('') == 1:
            has_toilet_info = True
        else:
            has_toilet_info = False
        if request.form.get('has_wifi').strip('') == 1:
            has_wifi_info = True
        else:
            has_wifi_info = False
        if request.form.get('has_sockets').strip('') == 1:
            has_socket_info = True
        else:
            has_socket_info = False
        if request.form.get('can_take_calls').strip('') == 1:
            can_take_calls_info = True
        else:
            can_take_calls_info = False
        #create new record
        new_cafe = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('location'),
            seats=request.form.get('seats'),
            has_toilet=has_toilet_info,
            has_wifi=has_wifi_info,
            has_sockets=has_socket_info,
            can_take_calls=can_take_calls_info,
            coffee_price=request.form.get('coffee_price')
        )
        print(new_cafe)
        db.session.add(new_cafe)
        db.session.commit()
        return "your form was successfully submitted"
        # else:
        #     return jsonify(error={"No Access": " Sorry you do not have access to this feature"})

## HTTP PUT/PATCH - Update Record
##PATCH
@app.route('/update-price', methods=['PATCH'])
def update_price():
    key = request.args.get('key')
    if key == my_api_key:
        if request.method == "PATCH":
            cafe_id = request.args.get('cafe_id')
            print(cafe_id)
            price_of_coffee = request.args.get('coffee_price_change')
            cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
            # cafe_to_update = to_dict(cafe_to_update)
            print(cafe_to_update)
            cafe_listed = to_dict(cafe_to_update)
            print(cafe_listed)
            cafe_to_update.coffee_price = price_of_coffee
            db.session.commit()
            return jsonify(f'You changed the price of coffee at {cafe_to_update} successfully')
        else:
            return "not correct request"
    else:
        return jsonify(error={"No Access": " Sorry you do not have access to this feature"})

## HTTP DELETE - Delete Record
@app.route('/delete', methods=['POST'])
def delete():
    cafe_id = request.args.get('cafe_id')
    key = request.args.get('key')
    if key == my_api_key:
        cafe = Cafe.query.filter_by(id=cafe_id).first()
        db.session.delete(cafe)
        db.session.commit()
        return "cafe successfully deleted"
    else:
        return "you do not have access to this command"

if __name__ == '__main__':
    app.run(debug=True)
