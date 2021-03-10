import os
class Config:
    SECRET_KEY='hard to guess'
    SQLALCHEMY_DATABASE_URI='sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD= os.environ.get('MAIL_PASSWORD')
    
    MAIL_USE_TLS = False
    
    MAIL_USE_SSL = True 