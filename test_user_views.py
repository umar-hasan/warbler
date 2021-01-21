"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes
from flask import session


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

        self.testuser1.id = 101
        self.testuser2.id = 102

        db.session.commit()

        


    def tearDown(self):
        """Rollback session."""

        db.session.rollback()

    def login(self):
        self.client.post("/login", data={
            'form-login-username': "testuser1",
            'form-login-password': "testuser"
        })

    
    # def test_follow_pages_logged_in(self):
    #     """Tests user follower/following pages."""

    #     with self.client.session_transaction() as s:
    #         s[CURR_USER_KEY] = self.testuser1.id

    #         follow = Follows(user_being_followed_id=self.testuser1.id, user_following_id=self.testuser2.id)
    #         db.session.add(follow)
    #         db.session.commit()

    #         res = self.client.get(f"/users/{self.testuser1.id}/following")
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("@testuser2", html)

    #         res = self.client.get(f"/users/{self.testuser2.id}/followers")
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("@testuser1", html)
        
    
    # def test_follow_pages_logged_out(self):
    #     """Tests user follower/following pages."""

    #     follow = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser1.id)
    #     db.session.add(follow)

    #     req = self.client.get(f"/users/101/following")
    #     html = req.get_data(as_text=True)

    #     self.assertEqual(req.status_code, 302)

    #     res = self.client.get(f"/users/102/followers")

    #     self.assertEqual(res.status_code, 200)
    #     self.assertIn("@testuser2", html)


    def test_message_logged_in(self):
        """Tests messaging when logged in."""

        msg = Message(text="Test message.", user_id=self.testuser1.id)
        db.session.add(msg)
        db.session.commit()
        with self.client.session_transaction() as s:
            s[CURR_USER_KEY] = self.testuser1.id

            res = self.client.get(f"/messages/{msg.id}")
            self.assertIn("Test message.", str(res.data))

    
    # def test_message_logged_out(self):
    #     """Tests messaging when logged out."""

    #     msg = Message(text="Test message.", user_id=self.testuser1.id)
    #     db.session.add(msg)
    #     db.session.commit()

    #     res = self.client.get(f"/messages/{msg.id}")
    #     self.assertIn("Access unauthorized.", str(res.data))

    
    def test_like(self):
        """Tests if a user can like a message."""

        msg = Message(text="Test message.", user_id=self.testuser2.id)
        db.session.add(msg)
        db.session.commit()

        with self.client.session_transaction() as s:
            s[CURR_USER_KEY] = self.testuser1.id

            res = self.client.post(f"/users/add_like/{msg.id}")

            self.assertEqual(res.status_code, 302)
            self.assertEqual(len(self.testuser1.likes), 1)
