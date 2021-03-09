
from datetime import datetime, timedelta
from contactform import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# acnt_delete = db.Table('acnt_delete',
# db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
# db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'))
# )


# UserMixin-a class for all 4 functions..like get _id, is_authenticated


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    email = db.Column(db.String(50), nullable = False, unique = True)
    image_file =db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)
    posts = db.relationship("Post", backref ='author', lazy = True,cascade="all,delete")
    # comments_by_user = db.relationship("Comment", backref ='author', lazy = True,cascade="all,delete")
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)
    followed = db.relationship(
        'User', secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy ='dynamic'), lazy = 'dynamic')

    
    

    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id). count()>0
   

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                  followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)

        return followed.union(own).order_by(Post.timestamp.desc())          
       


# lazy - execution mode of the query 


    def get_token(self, expires_sec = 1500):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    # no self parameter 
    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)    

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"
    


class Post(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
 
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref = 'article', lazy = True, cascade="all,delete")


  
    
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"




class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    commented_user = db.Column(db.String(20),nullable=True)
    body = db.Column(db.String(60), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'),nullable = False)
    # user_comment_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)
    


    
