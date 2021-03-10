
from flask import render_template, flash, url_for, redirect, request, Blueprint
from social_media import  db
from social_media.models import Post, Comment


from social_media.comment.forms import  CommentForm
from flask_login import login_user, current_user,login_required



comments = Blueprint('comments',__name__)















    
@comments.route('/post/<int:post_id>/comment', methods = ['GET','POST'])
@login_required
def post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.commented_user.data != current_user.username:
                flash(f'Please enter your own username')
            else:    
            
                comment = Comment(commented_user = form.commented_user.data,body = form.body.data, article = post)
                db.session.add(comment)
                db.session.commit()
                flash(f'Your comment has been posted!','success')
                return redirect(url_for('posts.post', post_id = post.id))
    return render_template('post_comment.html', title = 'Comment Post', form = form, post_id = post_id)    
