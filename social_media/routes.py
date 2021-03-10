from flask import render_template, flash, url_for, redirect, request, abort
from social_media import app, db, bcrypt, mail
from social_media.models import User, Post,Comment
import secrets
import os
from PIL import Image

from social_media.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm,ResetPasswordForm, ResetForm, CommentForm, DeleteForm
from flask_login import login_user, current_user,login_required, logout_user
from flask_mail import Message
from datetime import datetime




@app.route('/')    
@app.route('/home')
def home():
    page = request.args.get('page', 1, type= int)

    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=7)


    return render_template('home.html',posts = posts)


@app.route('/about')
def about():
    return render_template('about.html',title = 'About')    



@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password= hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created. You are now able to log in!', 'success')
        return redirect(url_for('login')) 
    return render_template('register.html',title = 'Register', form = form)    



@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
   
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:    
            
            flash(f'Login Unsuccessful. Please check email or password','error')
    return render_template('login.html',title = 'Login', form = form)        


def picture_set(form_pic):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_pic.filename)
    picture_fn = random_hex + file_ext 
    picture_path = os.path.join(app.root_path, 'static/profile', picture_fn)
    size=(125, 125)
    im = Image.open(form_pic)
    im.thumbnail(size)
    im.save(picture_path)
    return picture_fn



@app.route('/account', methods = ['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.pics.data:
            picture_file = picture_set(form.pics.data)
            current_user.image_file = picture_file
        current_user.username=form.username.data
        current_user.email = form.email.data
        

        db.session.commit()
        flash(f'Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form )



@app.route('/post/new', methods = ['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('make_post.html', title = 'Make Post',form = form )





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

   
@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post =post) 
    
@app.route('/post/<int:post_id>/update', methods = ['GET','POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
         
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash(f'Your post has been updated!','success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':    
        form.title.data = post.title
        form.content.data = post.content
    return render_template('update_post.html', title = 'Update Post',form = form )





@app.route('/user/<string:username>')
@login_required
def user_posts_info(username):
    page = request.args.get('page', 1, type= int)
    user = User.query.filter_by(username= username).first()
    if user is None:
        return render_template('403.html'), 403

    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page = page, per_page=8)
   
    return render_template('user.html',posts = posts, user = user)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500  


@app.errorhandler(403)
def internal_server_error(e):
    return render_template('403.html'),403     


# external -- for getting absolute url not relative 
def send_token_for_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request', sender='nikitadasmsd@gmail.com', recipients=[user.email])
    msg.body =f'''
    If you want to reset your password, visit the following link: {url_for('reset_by_token', token = token, _external = True)}


    If you don't want then ignore this email.
    '''
    mail.send(msg)




@app.route('/reset_pass', methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_token_for_mail(user)
        flash(f'An email has been sent. Please check', 'success')
        return redirect(url_for('login'))


    return render_template('reset_request.html', title = 'Reset Password', form = form)


@app.route('/reset_pass/<token>', methods = ['GET','POST'])
def reset_by_token(token):  
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    user = User.verify_token(token)
    if user is None:
        flash(f'It is an invalid or expired token', 'error') 
        return redirect(url_for('reset_request'))   
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password  has been changed. You are now able to log in!', 'success')
        return redirect(url_for('login')) 
    return render_template('reset_by_token.html', title = 'Reset Password', form = form)
   

@app.route('/post/<int:post_id>/delete', methods = ['GET','POST'])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()    
    flash(f'Your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()








@app.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
   
    user = User.query.filter_by(username=username).first()
   

    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user_posts_info', username=username))
    

        
@app.route('/unfollow/<username>', methods=['GET','POST'])
@login_required
def unfollow(username):
    
    user = User.query.filter_by(username=username).first()
    
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user_posts_info', username=username))




    
@app.route('/post/<int:post_id>/comment', methods = ['GET','POST'])
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
                return redirect(url_for('post', post_id = post.id))
    return render_template('post_comment.html', title = 'Comment Post', form = form, post_id = post_id)    



@app.route('/delete', methods = ['GET','POST'])
@login_required
def delete_account():
    form = DeleteForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            db.session.delete(current_user)
            db.session.commit()
            flash(f'Your account has been successfully deleted.','success')
            return redirect(url_for('home'))
    return render_template('delete_account.html',title = 'Delete Account',form = form)
        



    






@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}










    