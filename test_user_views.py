"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()
db.session.expire_on_commit = False

app.config['WTF_CSRF_ENABLED'] = False



class UserViewTestCase(TestCase):
    """Test views for user views."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        

        app.config["TESTING"] = True
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser1_id = 101
        self.testuser2_id = 102
        self.testuser1.id = self.testuser1_id
        self.testuser2.id = self.testuser2_id

        db.session.commit()

        

        


    def tearDown(self):
        """Rollback session."""

        db.session.rollback()

    def login(self):
        self.client.post("/login", data={
            'form-login-username': "testuser1",
            'form-login-password': "testuser"
        })

    def set_followers(self):
        follow = Follows(user_being_followed_id=self.testuser2_id, user_following_id=self.testuser1_id)
        db.session.add(follow)
        db.session.commit()

    def test_users_index(self):
        resp = self.client.get("/users")

        self.assertIn("@testuser1", str(resp.data))
        self.assertIn("@testuser2", str(resp.data))

    
    def test_follow_pages_logged_in(self):
        """Tests user follower/following pages."""


        with self.client.session_transaction() as s:
            s[CURR_USER_KEY] = self.testuser1.id

        self.client.post(f"/users/follow/{self.testuser2_id}")

        res = self.client.get(f"/users/{self.testuser1_id}/following")
        html = res.get_data(as_text=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn("@testuser2", html)

        res = self.client.get(f"/users/{self.testuser2_id}/followers")
        html = res.get_data(as_text=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn("@testuser1", html)
        
    
    def test_follow_pages_logged_out(self):
        """Tests user follower/following pages."""

        res = self.client.get(f"/users/{self.testuser1_id}/following")
        self.assertEqual(res.status_code, 302)

        res = self.client.get("/")
        html = res.get_data(as_text=True)
        self.assertIn("Access unauthorized.", html)

        res = self.client.get(f"/users/{self.testuser2_id}/followers")
        self.assertEqual(res.status_code, 302)

        res = self.client.get("/")
        html = res.get_data(as_text=True)
        self.assertIn("Access unauthorized.", html)


    def test_message_logged_in(self):
        """Tests messaging when logged in."""

        with self.client.session_transaction() as s:
            s[CURR_USER_KEY] = self.testuser1.id

        self.client.post("/messages/new", data={
            'text': "Test message."
        })

        msg = Message.query.filter_by(user_id=self.testuser1_id).first()

        res = self.client.get(f"/messages/{msg.id}")
        self.assertIn("Test message.", str(res.data))

    
    def test_message_logged_out(self):
        """Tests messaging when logged out."""

        res = self.client.post("/messages/new", data={
            'text': "Test message."
        })
        self.assertEqual(res.status_code, 302)

        res = self.client.get("/")
        self.assertIn("Access unauthorized.", str(res.data))

    
    def test_like_logged_in(self):
        """Tests if a user can like a message when logged in."""

        with self.client.session_transaction() as s:
            s[CURR_USER_KEY] = self.testuser1.id

        res = self.client.post("/messages/new", data={
            'text': "Test message."
        })

        msg = Message.query.filter_by(user_id=self.testuser1_id).first()

        res = self.client.post(f"/users/add_like/{msg.id}")
        likes = Likes.query.filter_by(user_id=self.testuser1_id).all()

        self.assertEqual(res.status_code, 302)
        self.assertEqual(len(likes), 1)


    def test_like_logged_out(self):
        """Tests if a user can like a message when logged out."""

        msg = Message(text="Test message", user_id=self.testuser1_id)
        db.session.add(msg)
        db.session.commit()

        msg = Message.query.filter_by(user_id=self.testuser1_id).first()

        res = self.client.post(f"/users/add_like/{msg.id}")
        self.assertEqual(res.status_code, 302)

        res = self.client.get("/")
        self.assertIn("Access unauthorized.", str(res.data))
