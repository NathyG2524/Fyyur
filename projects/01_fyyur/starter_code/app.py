#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from os import abort
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Venue, Artist, Shows, db_init
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:passabc@localhost:5432/fyyur'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

moment = Moment(app)
# app.config.from_object('config')
db = db_init(app)

# migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, datetime):
    value = value.isoformat()
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  loc_data = []
  try:
    data = db.session.query((Venue.city), (Venue.state)).distinct().all()

    for loc in data:
      city = loc[0]
      state = loc[1]

      venues = Venue.query.filter_by(city=city, state=state).all()
      ven_data = []
      loc = {
        'city': city,
        'state' : state,
        'venues' : [],
        }
      for venue in venues:
        venue_show = Shows.query.filter_by(venue_id=venue.id).all()
        num_upc_show = 0
        past_show = 0
        upcoming = []
        past =[]
        for ven_show in venue_show:
          
          
          # num_upcoming_shows= ven_show.filter(ven_show.start_time > datetime.now())
          if ven_show.start_time > datetime.now() :
            num_upc_show = num_upc_show + 1
            upcoming.append(ven_show)
            # print(venue.id)
          else:
            past_show = past_show + 1
            past.append(ven_show)
        # print(past_show)
        # print(num_upc_show)
        # past_shows_query = db.session.query(Shows.join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time>datetime.now()).all())

        loc_venu={
          'name' : venue.name,
          'id' : venue.id,
          'num_upcoming_shows' : num_upc_show
        }
        print(venue.name)

        loc['venues'].append(loc_venu)
        
      loc_data.append(loc)
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/venues.html', areas=loc_data)
  
# 
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }


  search = request.form.get('search_term', '')

  search_result= Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()

  response={
    "count":len(search_result),
    "data": []
  }

  for result in search_result:
    upcoming_shows_query = db.session.query(Shows).join(Venue).filter(Shows.artist_id==result.id).filter(Shows.start_time>datetime.now()).all()
    searchr = {
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(upcoming_shows_query),
    }
    response["data"].append(searchr)



  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  if  venue is None:
    return not_found_error(404)
  # geners_list = []
  print(venue.genres)
  # for li in venue.genres:
  # # print(venue.genres)
  #   geners_list.append(li)
  # print(geners_list)

  venue_show = Shows.query.filter_by(venue_id=venue.id).all()
  upcoming_shows_query = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time>datetime.now()).all()
    # upcoming.append(upcoming_shows_query)
  upcoming = []
  
  for up_c in upcoming_shows_query:
    
    
    # num_upcoming_shows= ven_show.filter(ven_show.start_time > datetime.now())
    # if art.start_time > datetime.now() :
    #   num_upc_show = num_upc_show + 1
      artist = Artist.query.get(up_c.artist_id)
      upc_show ={
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": up_c.start_time,
      }
      upcoming.append(upc_show)
    #   # print(venue.id)
  past_shows_query = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time<datetime.now()).all()
  past =[]

  for pas_c in past_shows_query:

    # else:
    #   venue = Venue.query.get(art.venue_id)
    #   past_show = past_show + 1
      # past_shows = {
      #           "venue_id": venue.id,
      #           "venue_name": venue.name,
      #           "venue_image_link": venue.image_link,
      #           "start_time": str(art.start_time),
      #       }
    

    #   past.append(past_shows)
    artist= Artist.query.get(pas_c.artist_id)
    pc_show ={
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": pas_c.start_time,
      }
    past.append(pc_show)
  # num_upc_show = 0
  # past_show = 0
  # upcoming = []
  # past =[]
  # for ven_show in venue_show:
    
    
  #   # num_upcoming_shows= ven_show.filter(ven_show.start_time > datetime.now())
  #   if ven_show.start_time > datetime.now() :
  #     num_upc_show = num_upc_show + 1
  #     artist = Artist.query.get(ven_show.artist_id)
      # upc_show = {
      # "artist_id": artist.id,
      # "artist_name": artist.name,
      # "artist_image_link": artist.image_link,
      # "start_time": ven_show.start_time,
      # }
  #     upcoming.append(upc_show)
      
  #   else:
  #     artist = Artist.query.get(ven_show.artist_id)
  #     past_show = past_show + 1
  #     past_shows = {
  #     "artist_id": artist.id,
  #     "artist_name": artist.name,
  #     "artist_image_link": artist.image_link,
  #     "start_time": ven_show.start_time,
  #   }

      # past.append(past_shows)
  print(venue.seeking_talent)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  body = {}
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    if seeking_talent == 'y':
      boolean_v = True
    else:
      boolean_v = False

    venue = Venue (
                  name=name,
                  city=city,
                  state=state,
                  address= address,
                  phone=phone,
                  genres = genres,
                  facebook_link = facebook_link,
                  image_link=image_link,
                  website_link= website_link,
                  seeking_description = seeking_description,
                  seeking_talent = boolean_v,

                  )

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())  
  finally:
    db.session.close()
      # flash('An error occurred. Venue ' + request['name'] + ' could not be listed.')


  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  # return render_template('pages/artists.html', artists=data)
  return render_template('pages/artists.html', artists=Artist.query.order_by('id').all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search = request.form.get('search_term', '')

  search_result= Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()

  response={
    "count":len(search_result),
    "data": []
  }

  for result in search_result:
    upcoming_shows_query = db.session.query(Shows).join(Venue).filter(Shows.artist_id==result.id).filter(Shows.start_time>datetime.now()).all()
    searchr = {
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(upcoming_shows_query),
    }
    response["data"].append(searchr)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_artist.html', artist=data)

  artist = Artist.query.get(artist_id)
  if artist is None:
    return not_found_error(404)
  # geners_list = []
  # print(venue.genres[0])
  # for li in venue.genres:
  # # print(venue.genres)
  #   geners_list.append(li)
  # print(geners_list)

  # artist_show = Shows.query.filter_by(artist_id=artist.id).all()
  upcoming_shows_query = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist.id).filter(Shows.start_time>datetime.now()).all()
    # upcoming.append(upcoming_shows_query)
  upcoming = []
  
  for up_c in upcoming_shows_query:
    
    
    # num_upcoming_shows= ven_show.filter(ven_show.start_time > datetime.now())
    # if art.start_time > datetime.now() :
    #   num_upc_show = num_upc_show + 1
      venue = Venue.query.get(up_c.venue_id)
      upc_show ={
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(up_c.start_time),
            }
      upcoming.append(upc_show)
    #   # print(venue.id)
  past_shows_query = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time<datetime.now()).all()
  past =[]

  for pas_c in past_shows_query:

    # else:
    #   venue = Venue.query.get(art.venue_id)
    #   past_show = past_show + 1
    #   past_shows = {
    #             "venue_id": venue.id,
    #             "venue_name": venue.name,
    #             "venue_image_link": venue.image_link,
    #             "start_time": str(art.start_time),
    #         }
    

    #   past.append(past_shows)
    venue = Venue.query.get(up_c.venue_id)
    pc_show ={
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(pas_c.start_time),
            }
    past.append(pc_show)


  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    # "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  
  
  # return render_template('pages/show_venue.html', venue=data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(obj=Artist.query.get(artist_id))
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  artist = Artist.query.get(artist_id)
  if artist is None:
    return not_found_error(404)
  # geners_list = []
  # print(venue.genres[0])
  # for li in venue.genres:
  # # print(venue.genres)
  #   geners_list.append(li)
  # print(geners_list)

  artist_show = Shows.query.filter_by(artist_id=artist.id).all()
  # upcoming_shows_query = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist.id).filter(Shows.start_time>datetime.now()).all()
  #   # upcoming.append(upcoming_shows_query)
  # upcoming = []
  
  # for up_c in upcoming_shows_query:
    
    
  #   # num_upcoming_shows= ven_show.filter(ven_show.start_time > datetime.now())
  #   # if art.start_time > datetime.now() :
  #   #   num_upc_show = num_upc_show + 1
  #     venue = Venue.query.get(up_c.venue_id)
  #     upc_show ={
  #               "venue_id": venue.id,
  #               "venue_name": venue.name,
  #               "venue_image_link": venue.image_link,
  #               "start_time": str(up_c.start_time),
  #           }
  #     upcoming.append(upc_show)
  #   #   # print(venue.id)
  # past_shows_query = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist.id).filter(Shows.start_time<datetime.now()).all()
  # past =[]

  # for pas_c in past_shows_query:

    # else:
    # #   venue = Venue.query.get(art.venue_id)
    # #   past_show = past_show + 1
    # #   past_shows = {
    # #             "venue_id": venue.id,
    # #             "venue_name": venue.name,
    # #             "venue_image_link": venue.image_link,
    # #             "start_time": str(art.start_time),
    # #         }
    

    # #   past.append(past_shows)
    # venue = Venue.query.get(up_c.venue_id)
    # pc_show ={
    #             "venue_id": venue.id,
    #             "venue_name": venue.name,
    #             "venue_image_link": venue.image_link,
    #             "start_time": str(pas_c.start_time),
    #         }
    # past.append(pc_show)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    # "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    # "past_shows": past,
    # "upcoming_shows": upcoming,
    # "past_shows_count": len(past),
    # "upcoming_shows_count": len(upcoming),
  }
  # # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  up_artist = Artist.query.get(artist_id)
  if up_artist is None:
    return not_found_error(404)
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')

    if seeking_venue == 'y':
      boolean_v = True
    else:
      boolean_v = False
    
    up_artist.name=name
    up_artist.city=city
    up_artist.state=state
    up_artist.phone=phone
    up_artist.genres = genres
    up_artist.facebook_link = facebook_link
    up_artist.image_link=image_link
    up_artist.website_link= website_link
    up_artist.seeking_description = seeking_description
    up_artist.seeking_venue = boolean_v

                  

    db.session.add(up_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())  
  finally:
    db.session.close()
    if error == True:
      # flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      abort()
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(obj=Venue.query.get(venue_id))
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  venue = Venue.query.get(venue_id)

  if venue is None:
    return not_found_error(404)
  # geners_list = []
  print(venue.genres)
  # for li in venue.genres:
  # # print(venue.genres)
  #   geners_list.append(li)
  # print(geners_list)

  venue_show = Shows.query.filter_by(venue_id=venue.id).all()
  upcoming_shows_query = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time>datetime.now()).all()
    # upcoming.append(upcoming_shows_query)
  upcoming = []
  
  for up_c in upcoming_shows_query:
    
    
    # num_upcoming_shows= ven_show.filter(ven_show.start_time > datetime.now())
    # if art.start_time > datetime.now() :
    #   num_upc_show = num_upc_show + 1
      artist = Artist.query.get(up_c.artist_id)
      upc_show ={
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": up_c.start_time,
      }
      upcoming.append(upc_show)
    #   # print(venue.id)
  past_shows_query = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time<datetime.now()).all()
  past =[]

  for pas_c in past_shows_query:

    # else:
    #   venue = Venue.query.get(art.venue_id)
    #   past_show = past_show + 1
      # past_shows = {
      #           "venue_id": venue.id,
      #           "venue_name": venue.name,
      #           "venue_image_link": venue.image_link,
      #           "start_time": str(art.start_time),
      #       }
    

    #   past.append(past_shows)
    artist= Artist.query.get(pas_c.artist_id)
    pc_show ={
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": pas_c.start_time,
      }
    past.append(pc_show)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  up_venue = Venue.query.get(venue_id)
  if up_venue is None:
    return not_found_error(404)
  body = {}
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    if seeking_talent == 'y':
      boolean_v = True
    else:
      boolean_v = False
    
    up_venue.name=name
    up_venue.city=city
    up_venue.state=state
    up_venue.phone=phone
    up_venue.genres = genres
    up_venue.facebook_link = facebook_link
    up_venue.image_link=image_link
    up_venue.website_link= website_link
    up_venue.seeking_description = seeking_description
    up_venue.seeking_talent = boolean_v



    db.session.add(up_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())  
  finally:
    db.session.close()
    if error == True:
      # flash('An error occurred. Venue ' + request['name'] + ' could not be listed.')
      abort()

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  body = {}
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')

    if seeking_venue == 'y':
      boolean_v = True
    else:
      boolean_v = False
    artist = Artist (
                  name=name,
                  city=city,
                  state=state,
                  phone=phone,
                  genres = genres,
                  facebook_link = facebook_link,
                  image_link=image_link,
                  website_link= website_link,
                  seeking_description = seeking_description,
                  seeking_venue = boolean_v,

                  )

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())  
  finally:
    db.session.close()
    

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  shows=Shows.query.all()
  shows_ls = []

  # shows = Shows.query.all()

  for show in shows:
    artist = Artist.query.get(show.artist_id)
    show_l = {
                "venue_id": show.venue_id,
                "venue_name": Venue.query.get(show.venue_id).name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
    shows_ls.append(show_l)


  # return render_template('pages/shows.html', shows=data)
  return render_template('pages/shows.html', shows=shows_ls)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  body = {}
  error = False
  try:
    artist_id = request.form.get('artist_id')
    print(artist_id)
    venue_id = request.form.get('venue_id')
    start_time = format_datetime(request.form.get('start_time'))
    # print(start_time)
    print(str(start_time))
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    if artist is not None and venue is not None:
      show = Shows(
        artist_id = artist_id,
        venue_id = venue_id,
        start_time = start_time
      )
    
      db.session.add(show)

      db.session.commit()
      flash('Show was successfully listed!')
    else:
      flash('input valid value')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('Show was not successfully listed!')
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
