"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from sqlalchemy import select
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Profile
#from models import Person

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


# GET ALL USERS ----->
@app.route('/users', methods=['GET'])   
def get_users():
    stmt = select(User)
    users = db.session.execute(stmt).scalars().all()
    return jsonify([user.serialize() for user in users]), 200


# GET SINGLE USER ----->
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({'error':'User not found'}), 404
    return jsonify(user.serialize()),200


# POST USER ------->
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data or 'age' not in data:
        return jsonify({'error':'Missing data'}), 400

    # Crear usuario
    new_user = User(
        email=data['email'],
        password=data['password'],
        age=data['age']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 200

# DELETE USER 
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({'error':'User not found'}), 404
    if user.profile:
        db.session.delete(user.profile)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'user deleted'}),200

# PUT USER
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({'error':'User not found'}), 404
    user.email = data.get('email',user.email)
    user.age = data.get('age',user.age)
    user.password = data.get('password',user.password)
    db.session.commit()
    return jsonify(user.serialize()),200


# GET SINGLE USER PROFILE ----->
@app.route('/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({'error':'User not found'}), 404
    return jsonify(user.profile.serialize()),200


# PUT SINGLE USER PROFILE ------>
@app.route('/users/<int:user_id>/profile', methods=['PUT'])
def update_user_profile(user_id):
    data = request.get_json()
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    if user is None:
        return jsonify({'error':'User not found'}), 404
    if user.profile is None:
        return jsonify({'error':'This user has not profile create it using a "POST"'})
    
    user.profile.title = data.get('title',user.profile.title)
    user.profile.bio = data.get('bio',user.profile.bio)
    db.session.commit()
    return jsonify(user.profile.serialize()),200


# DELETE USER PROFILE ------>
@app.route('/users/<int:user_id>/profile', methods=['DELETE'])
def delete_user_profile(user_id):
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user is None:
        return jsonify({'error': 'User not found'}), 404

    if user.profile is None:
        return jsonify({'error': 'This user do not have a profile'}), 404

    db.session.delete(user.profile)
    db.session.commit()

    return jsonify({'message': 'User profile deleted'}), 200

# POST SINGLE USE PROFILE ------> 
@app.route('/users/<int:user_id>/profile', methods=['POST'])
def create_user_profile(user_id):
    data = request.get_json()

    if not data or 'title' not in data or 'bio' not in data:
        return jsonify({'error':'Missing data'}), 400
    
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    if user.profile:
        return jsonify({'error': 'User already have a profile, select "PUT" insted of "POST" '}), 404
    else:
        new_profile = Profile(title=data['title'], bio=data['bio'])
        user.profile = new_profile

    db.session.commit()

    return jsonify(user.profile.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

