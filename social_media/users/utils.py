
from flask import url_for, current_app
from social_media import  mail

import secrets
import os
from PIL import Image

from flask_mail import Message


def picture_set(form_pic):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_pic.filename)
    picture_fn = random_hex + file_ext 
    picture_path = os.path.join(current_app.root_path, 'static/profile', picture_fn)
    size=(125, 125)
    im = Image.open(form_pic)
    im.thumbnail(size)
    im.save(picture_path)
    return picture_fn


# external -- for getting absolute url not relative 
def send_token_for_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request', sender='nikitadasmsd@gmail.com', recipients=[user.email])
    msg.body =f'''
    If you want to reset your password, visit the following link: {url_for('users.reset_by_token', token = token, _external = True)}


    If you don't want then ignore this email.
    '''
    mail.send(msg)
