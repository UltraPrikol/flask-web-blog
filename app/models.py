from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from flask_login import UserMixin
from app import login
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from hashlib import md5


followers = db.Table('followers',
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('web_user.id')),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('web_user.id'))
)


class WebUser(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author'
    )
    about_me: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=True)
    last_seen: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    followed = so.relationship(
        'WebUser', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=so.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def follow(self, user):
        if not self.isfollowing(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def __repr__(self):
        return '<user {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?identicon&s={}'.format(
            digest, size
        )


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(WebUser.id),
                                               index=True)

    author: so.Mapped[WebUser] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return db.session.get(WebUser, int(id))
