from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
from db import init_db, create_user, get_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        create_user(username, hashed.decode('utf-8'))
        return jsonify({'message': 'User created successfully'}), 201
    except:
        return jsonify({'error': 'Username already exists'}), 400
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = get_user(username)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        token = create_access_token(identity=username)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Wrong password'}), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello {current_user}!'}), 200
    



if __name__ == '__main__':
    app.run(debug=True)