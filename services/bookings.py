import requests
from os.path import dirname, realpath
# microframework for webapps
from flask import Flask, request, Response, abort
# local data storage
from flask_sqlalchemy import SQLAlchemy
# data serialization
from marshmallow import Schema, fields, post_load, ValidationError
# to return HTTP status to incoming requests
from http import HTTPStatus as http_status
# reads and dumps json data
import json
# exception handling
from werkzeug.exceptions import NotFound
from datetime import date as datetime_date

# instantiate a flask app and give it a name
app = Flask(__name__)

# load the database
root_dir = dirname(realpath(__file__ + '/..'))
db_file = f"sqlite:///{root_dir}/database/bookings.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Booking(db.Model):
    """ This class maps the database booking model using SQLAlchemy ORM"""
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    movie = db.Column(db.Integer, nullable=False)
    rewarded = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """ to simple represent an instance of a booking """
        return f"<Booking: user:{self.user} movie: {self.movie} @ {self.date}>"


class BookingSchema(Schema):
    """ Defines how a Booking instance will be serialized"""
    class Meta:
        """ Add meta attributes here """
        ordered = True  # The output will be ordered according to the order that the fields are defined in the class.

    date = fields.Date()
    id = fields.Int(required=False)
    movie = fields.Int()
    rewarded = fields.Boolean(required=False)
    user = fields.Int()

    @post_load
    def make_booking(self, data, **kwargs):
        """ Deals with deserialization """
        return Booking(**data)


# instantiate the schema serializer
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# manuals for this service
@app.route("/", methods=['GET'])
def hello():
    return json.dumps({
        "uri": "/",
        "subresource_uris": {
            "bookings": "/bookings",
            "booking": "/bookings/<user>"
        }
    })

# add a route to GET bookings json
@app.route("/bookings", methods=['GET'])
def booking_list():
    """ Return all booking instances """
    bookings = Booking.query.all()
    serialized_objects = bookings_schema.dumps(
        bookings, sort_keys=True, indent=4)

    return Response(
        response=serialized_objects,
        status=http_status.OK,
        mimetype="application/json"
    )

# route to GET bookings json from a specific user
@app.route("/bookings/<user>", methods=['GET'])
def booking_record(user):
    """ Return all booking instances of a certain user """
    user_bookings = Booking.query.filter_by(user=user).all()

    if not user_bookings:
        raise abort(404, description="Resource not found")

    serialized_objects = bookings_schema.dumps(
        user_bookings, sort_keys=True, indent=4)

    return Response(
        response=serialized_objects,
        status=http_status.OK,
        mimetype="application/json"
    )

# Route for adding a new booking
@app.route("/bookings/new", methods=["POST"])
def new_booking():
    """ Make a new booking after a POST request """
    # we may want to define a table in the db for this and other rewards
    points_ammount_for_new_booking = 1
    new_booking = ''
    try:
        # TODO: why the fuck request.get_json() return a python
        # dict instead of a json string? bug?
        new_booking = booking_schema.loads(request.data)
    except ValidationError as err:
        pass
        # TODO: send a exception  message

    # save data:
    db.session.add(new_booking)
    db.session.commit()

    # send a reward point for this user
    response_from_rewards_service = add_to_user_score(
        new_booking.user, points_ammount_for_new_booking)
    new_booking.rewarded = True if response_from_rewards_service == http_status.OK else False

    return Response(
        response=booking_schema.dumps(new_booking, sort_keys=True, indent=4),
        status=http_status.OK,
        mimetype='application/json'
    )


def add_to_user_score(user, points_to_be_added):
    """ This sends a new point to a user's score on the Rewards service"""
    post_score_url = "http://localhost:5004/rewards/add_score"
    data = {"user": user, "add_to_score": points_to_be_added}

    try:
        response = requests.post(post_score_url, json=data)
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Rewards service is unavailable.")

    if response.status_code == http_status.NOT_FOUND:
        raise NotFound(f"No reward record were found for user {user}")

    return response.status_code


# exeuted when this is called from the cmd
if __name__ == "__main__":
    app.run(port=5003, debug=True)
