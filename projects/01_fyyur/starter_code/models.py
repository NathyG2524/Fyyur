from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Boolean, DATETIME, ForeignKey
from flask_migrate import Migrate

db = SQLAlchemy()

def db_init(app):
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:passabc@localhost:5432/fyyur'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config.from_object('config')
  db.app = app
  db.init_app(app)
  migrate = Migrate(app, db)
  return db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # new fields 
    genres = db.Column((db.JSON), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_description =db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Shows', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column((db.JSON), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
 
  # new fields 
    website_link = db.Column(db.String(120))
    seeking_description =db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship('Shows', backref='Artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

class Shows(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<Shows {self.id}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

