"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 1001
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_message_new_no_session(self):
        with self.client as client:
            res = client.post("/messages/new", data={"text": "meow"}, follow_redirects = True)
            self.assertEqual(res.status_code , 200)
            self.assertIn("unauthorized", str(res.data))

    def test_messages_show(self):
        with self.client as client: 
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        msg = Message(id = 111 , text = "woof", user_id = self.testuser.id)
        db.session.add(msg)
        db.session.commit()
        get_msg = Message.query.get(111)
        

        res = client.get(f"/messages/{get_msg.id}")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(get_msg.text , "woof")

    def test_invalid_message_show(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
       
        res = client.get("/messages/123")

        self.assertEqual(res.status_code, 404)

    def test_message_delete(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        msg = Message(id = 111 , text = "woof", user_id = self.testuser.id)
        db.session.add(msg)
        db.session.commit()
        get_msg = Message.query.get(111)
        
        res = client.post(f"/messages/{get_msg.id}/delete", follow_redirects = True)
        
        self.assertEqual(res.status_code, 200)
        
    def test_unauthorized_message_delete(self):
        user2 = User.signup(username="user2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        user2.id = 2002
        db.session.add(user2)
        db.session.commit()
        msg = Message(id = 111 , text = "woof", user_id = self.testuser.id)
        db.session.add(msg)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2002
            res = client.post("/messages/111/delete", follow_redirects = True)
            self.assertEqual(res.status_code , 200)
            self.assertIn("Access unauthorized", str(res.data))
            m = Message.query.get(111)
            self.assertIsNotNone(m)
        


                


       

