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

    def test_user_model(self):
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

    def test_user_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following),1)
        self.assertEqual(len(self.user2.followers),1)

        self.assertEqual(self.user1.following[0].id , self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)
    
    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_create_user(self):
        user3 = User(email = "user2@gmail.com", username = "test3", password = "abc")

        db.session.add(user3)
        db.session.commit()

        users = User.query.all()

        self.assertEqual(len(users), 3)

    def test_user_authenticate(self):
        test1 = User.authenticate(self.user1.username, "abc")
        test2 = User.authenticate("test", "abc")
        test3 = User.authenticate(self.user1.username, "ab")

        self.assertTrue(test1)
        self.assertFalse(test2)
        self.assertFalse(test3)