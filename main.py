from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import requests

ENDPOINT = "http://127.0.0.1:5000"

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        """Mengubah tabel ke dictionary"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    response = requests.get(url=f"{ENDPOINT}/all")
    cafes = response.json()['cafes']
    return render_template("index.html", all_cafes=cafes)
    

## HTTP GET - Read Record
@app.route("/random")
def get_random() :
    cafes = Cafe.query.all()
    random_cafe = random.choice(cafes)
    
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all() :
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def get_particular() :
    try :
        loc = request.args.get(key="loc")
        cafe = Cafe.query.filter_by(location=loc).first()
        return jsonify(cafe=cafe.to_dict())
    except :
        return jsonify(error={"Not found": "Sorry we don't have cafe at that location."})

## HTTP POST - Create Record

@app.route('/add', methods=['POST'])
def add_new_Cafe() :
    new_cafe = Cafe(
        name = request.form.get('name'),
        map_url = request.form.get('map_url'),
        img_url = request.form.get('img_url'),
        location = request.form.get('location'),
        seats = request.form.get('seats'),
        has_toilet = bool(request.form.get('has_toilet')),
        has_wifi = bool(request.form.get('has_wifi')),
        has_sockets = bool(request.form.get('has_sockets')),
        can_take_calls = bool(request.form.get('can_take_calls')),
        coffee_price = request.form.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id) :
    new_price = request.args.get('price')
    print(f'\n\n{new_price}\n\n')
    try :
        cafe_to_update = Cafe.query.get(cafe_id)
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully update the coffee price."}), 200
    except :
        return jsonify(response={"Not found": "Sorry we don't have cafe with that id."}), 404


## HTTP DELETE - Delete Record

@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id) :
    api_key = request.args.get('api-key')
    if api_key == "TopSecretAPIKey" :
        try :
            cafe_to_delete = Cafe.query.get(cafe_id)
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully delete the cafe."}), 200
        except :
            return jsonify(response={"Not found": "Sorry we don't have cafe with that id."}), 404
    else :
        return jsonify(response={"error": "Sorry that's not allowed, make sure you have the right api-key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
