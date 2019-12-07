from flask_testing import TestCase as FlaskTestingCase
from unittest import main
import requests
import json
from flask import Flask
from services import users
users.testing = True


class TestUserService(FlaskTestingCase):
    """ Tests for the Users service """

    def create_app(self):
        """ Dynamically bind a fake  database to real application """
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        users.db.init_app(app)
        app.app_context().push()  # this does the binding
        return app

    def setUp(self):
        """ Get everything ready for tests """
        self.url = "http://localhost:5000/users"
        self.post_url = "http://localhost:5000/users/new"
        self.new_user_json = """{"name": "Andy Bernard"}"""
        users.db.create_all()
        self.populate_db()

    def tearDown(self):
        """ Ensures that the database is emptied for next unit test """
        users.db.session.remove()
        users.db.drop_all()

    def test_user_record(self):
        """ Test if (de)serialization is working properly
        """
        user = users.User.query.get(1)
        with users.app.test_client() as get_user_route:
            response = requests.get(f"{self.url}/{user.id}")
            response_json = json.dumps(response.json())
            response_user = users.user_schema.loads(response_json)
            self.assertEqual(user.id, response_user.id)
            self.assertEqual(user.name, response_user.name)

    def test_new_user(self):
        """ Tests the creation of a new Showtime"""

        fake_user = users.user_schema.loads(self.new_user_json)
        with users.app.test_client() as new_user_route:
            # send data as POST form to endpoint:
            response = new_user_route.post(
                self.post_url, data=self.new_user_json)

            # check result from server with expected fake booking
            response_user_json = json.dumps(response.get_json())
            response_user = users.user_schema.loads(response_user_json)

            self.assertEqual(fake_user.name, response_user.name)

    def test_user_bookings(self):
        """ Test  user's bookings retrieving """
        get_bookings_url = "http://127.0.0.1/:5000/users"
        user = 2
        expected_response_json = """[
                                    {
                                        "date": "2019-11-01",
                                        "id": 2,
                                        "movie": 2,
                                        "rewarded": true,
                                        "user": 2
                                    }
                                ]"""
        expected_response_dict = json.loads(expected_response_json)

        with users.app.test_client() as get_bookings_route:
            response = requests.get(f"{self.url}/{user}/bookings")
            #actual_response_json = json.dumps(response.json())
            response_json = json.dumps(response.json())
            actual_response_dict = json.loads(response_json)

            self.assertEqual(expected_response_dict, actual_response_dict)

    def test_not_found(self):
        """ GET a invalid user """
        invalid_user = "999"
        with users.app.test_client() as invalid_user_route:
            response = invalid_user_route.get(f"{self.url}/{invalid_user}")
            self.assertEqual(response.status_code, 404,
                             "Got {actual_reply.status_code} but expected 404")

    def populate_db(self):
        """ Populates the database """
        u1 = users.User(name="Jim Halpert")
        u2 = users.User(name="Dwight Schrute")
        u3 = users.User(name="Michael Scott")

        users.db.session.add(u1)
        users.db.session.add(u2)
        users.db.session.add(u3)
        users.db.session.commit()


if __name__ == "__main__":
    main()
