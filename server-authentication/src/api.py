import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request
from flask_cors import CORS, cross_origin
from apiHandler import ApiHandler
from jwtHandler import jwtHandler
from keycloakInterface import KeycloakInterface

app = Flask(__name__)
cors = CORS(app) # cors is added in advance to allow cors requests
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['KEYCLOAK_SERVER_URL'] = os.getenv('KEYCLOAK_SERVER_URL')
app.config['OIDC_OP_AUTHORIZATION_ENDPOINT'] = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT')
app.config['OIDC_OP_TOKEN_ENDPOINT'] = os.getenv('OIDC_OP_TOKEN_ENDPOINT')
app.config['OIDC_OP_USER_ENDPOINT'] = os.getenv('OIDC_OP_USER_ENDPOINT')
app.config['OIDC_OP_JWKS_ENDPOINT'] = os.getenv('OIDC_OP_JWKS_ENDPOINT')
app.config['OIDC_OP_LOGOUT_ENDPOINT'] = os.getenv('OIDC_OP_LOGOUT_ENDPOINT')
app.config['OIDC_OP_ENDSESSION_ENDPOINT'] = os.getenv('OIDC_OP_ENDSESSION_ENDPOINT')
app.config['OIDC_OP_LOGOUT_URL_METHOD'] = os.getenv('OIDC_OP_LOGOUT_URL_METHOD')
app.config['OIDC_RP_CLIENT_ID'] = os.getenv('OIDC_RP_CLIENT_ID')
app.config['OIDC_RP_REALM_ID'] = os.getenv('OIDC_RP_REALM_ID')
app.config['OIDC_RP_CLIENT_SECRET'] = os.getenv('OIDC_RP_CLIENT_SECRET')
app.config['OIDC_RP_SIGN_ALGO'] = os.getenv('OIDC_RP_SIGN_ALGO')

apiHandler = ApiHandler(
    KeycloakInterface(
            server_url=os.getenv('KEYCLOAK_SERVER_URL'),
            realm_name=os.getenv('OIDC_RP_REALM_ID'),
            client_id=os.getenv('OIDC_RP_CLIENT_ID'),
            client_secret_key=os.getenv('OIDC_RP_CLIENT_SECRET')
        )
)

@app.route('/users/', methods=["GET"])
@cross_origin()
def index():
    return apiHandler.get_users()

@app.route('/users/create', methods=["POST"])
@cross_origin()
def post_user():
    if request.method == 'POST':
        get_data = request.get_json() # get_data gets the body of post request
        username = get_data['username']
        password = get_data['password']
        if len(username) < 1 or len(password) < 1 :
            return {"message": "invalid username or password"}, 403
        if apiHandler.user_exists(username):
            return {"message": "user already exists"}, 409
        apiHandler.handle_register(username, password)
        return {"message": "account created"}, 201
        
@app.route('/users/update', methods=["PUT"])
@cross_origin()
def update_password(): 
    get_data = request.get_json()
    username = get_data['username']
    old_password = get_data['old-password']
    new_password = get_data['new-password']
    if not apiHandler.user_exists(username):
        return {"message": "username does not exist"}, 403
    if not apiHandler.password_validated(username, old_password):
        return {"message": "old password is not valid"}, 403
    apiHandler.handle_password_update(username, new_password)
    return {"message": "password changed"}, 200

@app.route('/users/login', methods=["POST"])
@cross_origin()
def handle_login():
    if request.method == 'POST':
        get_data = request.get_json()
        username = get_data['username']
        password = get_data['password']
        jwt = apiHandler.handle_auth(username, password)
        # if not apiHandler.user_exists(username):
        #     return {"message": "username does not exist"}, 403
        # if not apiHandler.password_validated(username, password):
        #     return {"message": "password is not valid"}, 403
        # jwt = jwtHandler.generate_jwt(username)
        return {"message": "Login Success", "data":{"jwt": jwt['access_token']}}, 200
   
@app.route('/users/delete', methods=["DELETE"])
@cross_origin()
def handle_deletion():
    get_data = request.get_json()
    username = get_data['username']
    password = get_data['password']
    if not apiHandler.user_exists(username):
        return {"message": "username does not exist"}, 404
    if not apiHandler.password_validated(username, password):
        return {"message": "password is not valid"}, 403
    apiHandler.handle_deletion(username)
    return {"message": "account deleted"}, 204

@app.route('/users/validation', methods=["GET"])
@cross_origin()
def validation_check():
    get_data=request.args.to_dict()
    token = get_data.get('jwt')

    if token is None:
        # get Bearer token from header
        token = request.headers.get('Authorization')
        if token is None:
            return {"message": "Authentication Failed", "type": "No token provided"}, 401
        token = token.split(" ")[1]

    print("validation_check", token)
    if apiHandler.is_token_valid(token):
        return {"message": "Authentication Successful", "data": {"name": apiHandler.get_user_info(token)["name"]}}, 200
    else:
        return {"message": "Authentication Failed", "type": "Not a Valid Token"}, 401