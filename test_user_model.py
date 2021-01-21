"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import db, User, Message, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Rollback session."""

        db.session.rollback()

    def test_1_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.__repr__(), f"<User #{u.id}: testuser, test@test.com>")

    def test_2_user_follows(self):
        """Tests to see if a user can follow other users."""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="password"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="pass1234"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        u1.following.append(u2)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u1), True)

        u1.following.remove(u2)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u2.is_followed_by(u1), False)


    def test_3_signup(self):
        """Creates a user with proper credentials."""

        u = User.signup(username="user1", email="user1@test.com", password="pass1234", image_url=None)
        db.session.commit()
        self.assertEqual(u.__repr__(), f"<User #{u.id}: user1, user1@test.com>")

        from sqlalchemy.exc import IntegrityError

        with self.assertRaises(IntegrityError):
            x = User.signup(username="user1", email="user1@test.com", password="pass1234", image_url=None)
            db.session.commit()

    def test_4_login(self):
        """Tests login functionality."""

        u = User.signup(username="user1", email="user1@test.com", password="pass1234", image_url=None)
        u = User.authenticate(username="user1", password="pass1234")
        self.assertNotEqual(u, False)

        u = User.authenticate(username="user1", password="password")
        self.assertEqual(u, False)

