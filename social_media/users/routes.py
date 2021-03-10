
from flask import render_template, flash, url_for, redirect, request, abort, Blueprint
from social_media import  db, bcrypt
from social_media.models import User, Post


from social_media.users.forms import RegistrationForm, LoginForm, UpdateAccountForm,ResetPasswordForm, ResetForm, DeleteForm
from flask_login import login_user, current_user,login_required, logout_user
from social_media.users.utils import picture_set, send_token_for_mail
from datetime import datetime


users = Blueprint('users',__name__)

@users.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password= hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created. You are now able to log in!', 'success')
        return redirect(url_for('users.login')) 
    return render_template('register.html',title = 'Register', form = form)    

@users.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
   
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:    
            
            flash(f'Login Unsuccessful. Please check email or password','error')
    return render_template('login.html',title = 'Login', form = form)        


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))




@users.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()






@users.route('/account', methods = ['GET','POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form )



@users.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
   
    user = User.query.filter_by(username=username).first()
   

    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('users.user_posts_info', username=username))
    

        
@users.route('/unfollow/<username>', methods=['GET','POST'])
@login_required
def unfollow(username):
    
    user = User.query.filter_by(username=username).first()
    
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('users.user_posts_info', username=username))


@users.route('/delete', methods = ['GET','POST'])
@login_required
def delete_account():
    form = DeleteForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            db.session.delete(current_user)
            db.session.commit()
            flash(f'Your account has been successfully deleted.','success')
            return redirect(url_for('main.home'))
    return render_template('delete_account.html',title = 'Delete Account',form = form)
        

@users.route('/user/<string:username>')
@login_required
def user_posts_info(username):
    page = request.args.get('page', 1, type= int)
    user = User.query.filter_by(username= username).first()
    if user is None:
        return render_template('errors/403.html'), 403

    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page = page, per_page=8)
   
    return render_template('user.html',posts = posts, user = user)


@users.route('/reset_pass', methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_token_for_mail(user)
        flash(f'An email has been sent. Please check', 'success')
        return redirect(url_for('users.login'))


    return render_template('reset_request.html', title = 'Reset Password', form = form)


@users.route('/reset_pass/<token>', methods = ['GET','POST'])
def reset_by_token(token):  
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    user = User.verify_token(token)
    if user is None:
        flash(f'It is an invalid or expired token', 'error') 
        return redirect(url_for('users.reset_request'))   
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password  has been changed. You are now able to log in!', 'success')
        return redirect(url_for('users.login')) 
    return render_template('reset_by_token.html', title = 'Reset Password', form = form)
   