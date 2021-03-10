from flask import Blueprint

errors = Blueprint('errors', __name__)







@errors.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'),404


@errors.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'),500  


@errors.app_errorhandler(403)
def user_not_found_error(e):
    return render_template('errors/403.html'),403     
