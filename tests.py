from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import WebUser, Post
from app import config


class UserModelCase(unittest.TestCase):

    def setUp(self) -> None:
        app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URI_TEST']
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = WebUser(username='john', email='john@example')
        self.assertEqual(u.avatar(128), (
            'https://www.gravatar.com/avatar/'
            'd4c74594d841139328695756648b6bd6'
            '?d=identicon&s=128'
        ))

    def test_password_hashing(self):
        u = WebUser(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_follow(self):
        u1 = WebUser(username='john', email='john@example')
        u2 = WebUser(username='susan', email='susan@example')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followed.count(), 1)
        self.assertEqual(u2.followed.first().username, 'john')

    def test_follow_posts(self):
        u1 = WebUser(username='john', email='john@example')
        u2 = WebUser(username='susan', email='susan@example')
        u3 = WebUser(username='mary', email='susan@example')
        u4 = WebUser(username='david', email='david@example')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
