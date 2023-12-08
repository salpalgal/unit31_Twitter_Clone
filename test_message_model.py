import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("test1", "test1@gmail.com", "abc", None)
        uid1 = 101
        user1.id = uid1
        user2 = User.signup("test2", "test2@gmail.com", "abc", None)
        uid2 = 202
        user2.id = uid2
        db.session.commit()

        user1 = User.query.get(uid1)
        user2 = User.query.get(uid2)

        self.user1 = user1
        self.uid1 = uid1

        self.user2 = user2
        self.uid2 = uid2

        
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        msg = Message(text = "hello", user_id = self.user1.id)
        db.session.add(msg)
        db.session.commit()
        
        msgs = Message.query.all()

        self.assertEqual(len(msgs),1)
        self.assertEqual(self.user1.messages[0].text, "hello")

    def test_message_likes(self):
        msg = Message(text = "meow", user_id = self.user1.id)

        self.user2.likes.append(msg)

        db.session.commit()

        likes = Likes.query.all()

        self.assertEqual(len(likes), 1)
        self.assertEqual(self.user2.likes[0].text, "meow")
        self.assertEqual(self.user2.likes[0].user_id ,self.user1.id)

    
