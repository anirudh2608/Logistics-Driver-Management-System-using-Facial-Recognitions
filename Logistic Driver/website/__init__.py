from flask import Flask, session, g
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from os import name, path

#Initialize the database variable
db = SQLAlchemy()
DB_NAME = "logistics.db"

def create_app():
    app = Flask(__name__)

    #Configure Secret Key and Database for the app
    app.config['SECRET_KEY'] = 'sbfdsbfa secrret key hai sadhsa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    db.init_app(app)

    from .views import views
    from .auth import auth

    #Register the auth and views blueprint in the app
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Customer, Order, Admin, Driver, Truck, Checkpoint,Role

    create_database(app)

    @app.before_request
    def before_request():
        g.user = None

        #If user did not logout before closing the app, keep him logged in when the app runs again 
        if 'user' in session:
            g.user = session['user']

    return app

def create_database(app):
    #If the database does not exist
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("Successfully created database!")


    
    
