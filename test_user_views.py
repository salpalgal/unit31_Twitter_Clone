import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
# from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user1 = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.user1_id = 1001
        self.user1.id = self.user1_id

        self.user2 = User.signup("abc", "test1@test.com", "password", None)
        self.user2_id = 2002
        self.user2.id = self.user2_id
        self.user3 = User.signup("efg", "test2@test.com", "password", None)
        self.user3_id = 3003
        self.user3.id = self.user3_id
        self.u4 = User.signup("hij", "test3@test.com", "password", None)
        self.u5 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_list_users(self):
        with self.client as client:
            res = client.get("/users")

            self.assertEqual(res.status_code, 200)
            self.assertIn("abc", str(res.data))
            self.assertIn("hij", str(res.data))
            self.assertIn("testuser", str(res.data))

    def test_user_show(self):
        with self.client as client:
            res = client.get(f"/users/{self.user1.id}")

            self.assertEqual(res.status_code, 200)

    def test_user__show_likes(self):
        m1 = Message(text = "abc", user_id = self.user1.id)
        m2 = Message(text = "meow", user_id = self.user2.id)

        self.user3.likes.append(m1)
        self.user3.likes.append(m2)

        db.session.commit()

        with self.client as client:
            res = client.get(f"/users/{self.user3.id}")

            self.assertEqual(res.status_code, 200)
            self.assertIn("efg", str(res.data))
            self.assertEqual(len(self.user3.likes),2)

    def test_add_likes(self):
        m1 = Message(id = 123 ,text="woof", user_id = self.user1.id)
        db.session.add(m1)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            res= client.post("/messages/123/like", follow_redirects = True)

            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == 123).all()

            self.assertEqual(len(likes),1)

    def test_remove_likes(self):
        m1 = Message(id = 1234 ,text="woof", user_id = self.user1.id)
        self.user2.likes.append(m1)
        
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
            res= client.post("/messages/1234/unlike", follow_redirects = True)

            self.assertEqual(res.status_code, 200)
            m = Likes.query.filter(Likes.message_id == 1234).all()
            self.assertEqual(len(m),0)

    def test_show_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()
        
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            res = client.get(f"/users/{self.user1.id}/following")
            self.assertEqual(res.status_code, 200)
            self.assertIn("abc", str(res.data))

    def test_show_followers(self):
        self.user1.followers.append(self.user2)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            res = client.get(f"/users/{self.user1.id}/followers")
            self.assertEqual(res.status_code, 200) 
            self.assertIn("abc", str(res.data))          
        
