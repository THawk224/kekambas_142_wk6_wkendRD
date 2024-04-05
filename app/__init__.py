from flask import Flask # Import the Flask class from the flask module
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config # Import the Config class from the config module

# Create an instance of Flask called an app which will be the central object for our application
app = Flask(__name__)

# Set the cofiguration for the app to use the config class we created
app.config.from_object(Config)

# Create an instance of SQLAlchemy called db which will be used to create the database
db = SQLAlchemy(app)
# Create an instance of Migrate called migrate which will be used to create the migrations
migrate = Migrate(app, db)

# Import the routes to the application and also the models 
from .import models, routes 