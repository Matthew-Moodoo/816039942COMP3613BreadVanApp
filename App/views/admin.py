from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from flask_admin import Admin
from flask import flash, redirect, url_for, request
from App.database import db
from App.models import Driver, Resident, Route, Street, Stop

class AdminView(ModelView):

    @jwt_required()
    def is_accessible(self):
        return current_user is not None

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Login to access admin")
        return redirect(url_for('index_page', next=request.url))

def setup_admin(app):
    admin = Admin(app, name='FlaskMVC', template_mode='bootstrap3')
    admin.add_view(AdminView(Driver, db.session))
    admin.add_view(AdminView(Resident, db.session))
    admin.add_view(AdminView(Route, db.session))
    admin.add_view(AdminView(Street, db.session))
    admin.add_view(AdminView(Stop, db.session))