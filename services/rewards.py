from os.path import dirname, realpath
# to return HTTP status to incoming requests
from http import HTTPStatus as http_status
# microframework for webapps
from flask import Flask, request, Response
# local data storage
from flask_sqlalchemy import SQLAlchemy
# data serialization
from marshmallow import Schema, fields, post_load

# read and dump as json data
import json
# exception handling
from werkzeug.exceptions import NotFound

# instantiate a flask app and give it a name
app = Flask(__name__)

# load the database
root_dir = dirname(realpath(__file__ + '/..'))
db_file = f"sqlite:///{root_dir}/database/rewards.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Reward(db.Model):
    """ This class maps the database reward model """
    user = db.Column(db.Integer, primary_key=True, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Reward: {self.user} has {self.score} points>"


class RewardSchema(Schema):
    """ Defines how a Reward instance will be serialized"""
    user = fields.Int()
    score = fields.Int()

    @post_load
    def make_reward(self, data, **kwargs):
        return Reward(**data)


# instantiate the schema serializer
reward_schema = RewardSchema()
rewards_schema = RewardSchema(many=True)


# add a route to GET all rewards
@app.route("/rewards", methods=['GET'])
def rewards_list():
    """ Return all Reward instances """
    rewards = Reward.query.all()
    serialized_objects = rewards_schema.dumps(
        rewards, sort_keys=True, indent=4)

    return Response(
        response=serialized_objects,
        status=http_status.OK,
        mimetype="application/json"
    )

# route to get a reward by its id
@app.route("/rewards/<user>", methods=['GET'])
def reward_info(user):
    """ GET a reward by user id"""
    reward = Reward.query.get(user)

    if not reward:
        raise NotFound

    serialized_object = reward_schema.dumps(reward, sort_keys=True, indent=4)

    return Response(
        response=serialized_object,
        status=http_status.OK,
        mimetype="application/json"
    )

# Route for adding a new score
@app.route("/rewards/add_score", methods=["POST"])
def add_score():
    """ POST a new score """
    user = request.get_json().get('user')
    add_to_score = request.get_json().get('add_to_score')

    user_score = Reward.query.get(user)
    if not user_score:
        return NotFound

    user_score.score += add_to_score
    db.session.commit()

    return Response(
        response=reward_schema.dumps(user_score, sort_keys=True, indent=4),
        status=http_status.OK,
        mimetype='application/json'
    )


@app.route("/rewards/prizes/<user>", methods=['GET', ])
def is_prize_available(user):
    """ Route to determine if user can retrieve prizes given a score
        response json has the following format:
        {
            "user": user: Int,
            "prize_available" : false: Bool,
            "points_unitil_prize": remaining_points: Int
        }
    """
    # May we have a database for this?
    # For now this is hard-coded
    needed_points_for_prize = 5
    user = int(user)
    user_record = Reward.query.get(user)

    if not user_record:
        return NotFound
    # check if user can get a prize
    if user_record.score < needed_points_for_prize:
        prize_available = False
        remaining_points = needed_points_for_prize - user_record.score

    response_dict = {"user": user,
                     "prize_avaliable": prize_available,
                     "points_until_prize": remaining_points
                     }

    return Response(
        response=json.dumps(response_dict, sort_keys=True, indent=4),
        status=http_status.OK,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(port=5004, debug=True)
