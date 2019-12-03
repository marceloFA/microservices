from flask_testing  import TestCase as FlaskTestingCase
from http import HTTPStatus as http_status
from unittest import main
import requests
import json
from flask import Flask
from services import rewards
rewards.testing = True



class TestRewardService(FlaskTestingCase):
    """ This tests the Reward cinema service """

    def create_app(self):
        """ Dynamically bind a fake  database to real application """
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        rewards.db.init_app(app)
        app.app_context().push() # this does the binding
        return app

    def setUp(self):
        """ Get everything ready for tests """
        self.url = "http://127.0.0.1:5004/rewards"
        self.add_score_url = "http://127.0.0.1:5004/rewards/add_score/"
        self.is_prize_available_url = "http://127.0.0.1:5004/rewards/is_prize_available/"
        self.add_to_score_dict = {"user":1, "add_to_score": 1}
        self.new_score_json = {"score": 1,"user": 1}
        rewards.db.create_all()
        self.populate_db()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        rewards.db.session.remove()
        rewards.db.drop_all()     

    def test_reward_record(self):
        """ Test if (de)serialization is working properly
        and user has the expected score
        """
        reward_score = rewards.Reward.query.get(1)
        with rewards.app.test_client() as get_reward_route:
            response = requests.get(f"{self.url}/{reward_score.user}")
            print(response.json())
            response_json = json.dumps(response.json())
            response_reward = rewards.reward_schema.loads(response_json)
            self.assertEqual(reward_score.score, response_reward.score)
            self.assertEqual(reward_score.user, response_reward.user)
     
     # TODO
    def test_add_point_to_user_score(self):
        """ This asserts that a new point is computed correctly"""
        with rewards.app.test_client() as add_score_route:
            response = add_score_route.post(self.add_score_url, json=self.add_to_score_dict)
            #response_json = json.dumps(response.json())
            #self.assertEqual(http_status.OK, response.status_code)
            self.assertEqual(self.new_score_json, response.json())
               
    

    # TODO
    def test_is_prize_available(self):
        """ This asserts one can only get a prize if one has enough points"""
        '''username = 'dwight_schrute'
        score = self.GOOD_RESPONSES[username]
        expected_reply = {username : True}
        response = requests.get(f"{self.is_prize_available_url}/{username}")
        actual_reply = response.json().get('score')

        self.assertEqual(actual_reply, expected_reply,
        f"Got {actual_reply} but expected {expected_reply} ")'''


    def test_not_found(self):
        """ Test /rewards/<user> for non-existent users"""
        invalid_user = "999"
        with rewards.app.test_client() as invalid_user_route: 
            actual_reply = invalid_user_route.get(f"{self.url}/{invalid_user}")
            self.assertEqual(actual_reply.status_code, 404,
                                "Got {actual_reply.status_code} but expected 404")

    def populate_db(self):
        r1 = rewards.Reward(user=1, score=0)
        r2 = rewards.Reward(user=2, score=0)
        r3 = rewards.Reward(user=3, score=0)
        rewards.db.session.add(r1)
        rewards.db.session.add(r2)
        rewards.db.session.add(r3)
        rewards.db.session.commit()
