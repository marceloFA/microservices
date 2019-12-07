from os.path import dirname, realpath
# microframework for webapps
from flask import Flask, request, Response
# local data storage
from flask_sqlalchemy import SQLAlchemy
# data serialization
from marshmallow import Schema, fields, post_load
# to return HTTP status to incoming requests
from http import HTTPStatus as http_status
# read and dump as json data
import json
import requests
# exception handling
from werkzeug.exceptions import NotFound


app = Flask(__name__)
root_dir = dirname(realpath(__file__ + '/..'))
db_file = f"sqlite:///{root_dir}/database/users.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """ This class maps the database user model """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User: {self.name}>"


class UserSchema(Schema):
    """ Defines how a user instance will be serialized"""

    class Meta:
        """ Add meta attributes here """
        ordered = True  # The output will be ordered according to the order that the fields are defined in the class.

    id = fields.Int(requeired=False)
    name = fields.String()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


# instantiate the schema serializer
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/", methods=['GET'])
def hello():
    return json.dumps({
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<user>",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    })


@app.route("/users", methods=['GET'])
def users_list():
    """ Return all booking instances """
    users = User.query.all()
    serialized_objects = users_schema.dumps(users, sort_keys=True, indent=4)

    return Response(
        response=serialized_objects,
        status=http_status.OK,
        mimetype="application/json"
    )


@app.route("/users/<user>", methods=['GET'])
def user_record(user):
    user = User.query.get(user)

    if not user:
        raise NotFound

    serialized_objects = user_schema.dumps(user, sort_keys=True, indent=4)

    return Response(
        response=serialized_objects,
        status=http_status.OK,
        mimetype="application/json"
    )

# Route for adding a new user
@app.route("/users/new", methods=["POST"])
def new_user():
    """ POST a new user"""
    new_user = None
    try:
        new_user = user_schema.loads(request.data)
    except ValidationError as err:
        pass
        # TODO: send a exception  message
    # save data:
    db.session.add(new_user)
    db.session.commit()

    return Response(
        response=user_schema.dumps(new_user, sort_keys=True, indent=4),
        status=http_status.OK,
        mimetype='application/json'
    )

# TODO: refactor this method
@app.route("/users/<user>/bookings", methods=['GET'])
def user_bookings(user):
    """
    Gets booking information from the bookings service for this user

    response format is like:
    """
    get_bookings_url = "http://127.0.0.1:5003/bookings"
    if not User.query.get(user):
        return NotFound

    try:
        response = requests.get(f"{get_bookings_url}/{user}")
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Bookings service is unavailable.")

    if response.status_code == http_status.NOT_FOUND:
        raise NotFound(f"No bookings were found for user {user}")

    return Response(
        response=json.dumps(response.json()),
        status=http_status.OK,
        mimetype='application/json'
    )

# TODO: implement this
@app.route("/users/<username>/suggested", methods=['GET'])
def user_suggested(username):
    """
    Returns movie suggestions. The algorithm returns a list of 3 top ranked
    movies that the user has not yet booked.
    :param username:
    :return: Suggested movies
    """
    raise NotImplementedError()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
