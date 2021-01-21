import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class MessageModelTest(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_message_model(self):
        """Tests if the message model works correctly."""

        message1 = Message(text="Some text.", user_id=self.testuser.id)
        db.session.add(message1)
        db.session.commit()

        self.assertEqual(len(self.testuser.messages), 1)

        from sqlalchemy.exc import IntegrityError

        with self.assertRaises(IntegrityError):
            message2 = Message(user_id=self.testuser.id)
            db.session.add(message2)
            db.session.commit()