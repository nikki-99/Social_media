from flask import render_template,  request, Blueprint, g,  current_app
from flask_login import current_user, login_required
from social_media.models import Post


from datetime import datetime
from social_media import  db



main = Blueprint('main',__name__)

@main.route('/')    
@main.route('/home')
def home():
    page = request.args.get('page', 1, type= int)
    q = request.args.get('q')

    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.content.contains(q)).order_by(Post.date_posted.desc()).paginate(page = page, per_page=7)
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=7)


    return render_template('home.html',posts = posts)


@main.route('/about')
def about():
    return render_template('about.html',title = 'About')    


@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
      






