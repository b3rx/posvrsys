#!/usr/bin/env python
# -*- coding: utf-8 -*-

# package  : POSvrSys - PyGTK POS Video Rental System
# version  : $Id$
# copyright: Copyright (c) 2008-2009 Bertrand Kintanar <b3rxkintanar@gmail.com>
# license  : http://opensource.org/licenses/gpl-3.0.html
# url      : http://posvrsys.googlecode.com/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# If you find any bugs or have any suggestions email: b3rxkintanar@gmail.com
# URL: http://posvrsys.googlecode.com/
#
# POSvrSys needs the following to function properly:
#   python >= 2.5.1, gtk >= 2.12.9, pygtk >= 2.12.2, 
#   sqlite >= 2.3.5, sqlalchemy >= 0.5.0

from config import *

import base64
import datetime
import sys

# Try to import sqlalchemy modules
try:
    
    from sqlalchemy import *
    from sqlalchemy import __version__ as ver
    from sqlalchemy.orm import *
    from sqlalchemy.orm.exc import *
    from sqlalchemy.ext.associationproxy import AssociationProxy
    from sqlalchemy.ext.declarative import declarative_base
    
    try:
        
        assert ver >= "0.5.0"
        
        if DEBUG:
            
            print "Checking sqlalchemy 0.5.0...... Found"
            
    except AssertionError:
        
        print "%s requires SQLAlchemy 0.5.0 or higher, but %s was found" \
            % (APP_NAME, ver)
        
        sys.exit(1)
        
except ImportError, e:
    
    print "Import error POSvsSys cannot start:", e
    
    sys.exit(1)
    
Base = declarative_base()

class Cast(Base):
    
    __tablename__ = 'casts'
    
    id            = Column(Integer, primary_key=True)
    full_name     = Column(String(100))
    
    movieassoc = relation('MovieCast', cascade="all, delete-orphan", lazy=False)
    
    movies = AssociationProxy('movieassoc', 'movie', creator='MovieCast')
    
    def __init__(self, full_name):
        
        self.full_name   = full_name
        
    def __repr__(self):
        
        return "<Cast('%s')>" % (self.full_name)
        
class City(Base):
    
    __tablename__ = 'cities'
    
    id            = Column(Integer, primary_key=True)
    name          = Column(String(100))
    
    customer = relation("Customer", order_by="Customer.id", backref="cities")
    
    def __init__(self, name):
        
        self.name = name
        
    def __repr__(self):
        
        return "<City('%s')>" % (self.name)
    
class Country(Base):
    
    __tablename__ = 'countries'
    
    id       = Column(Integer, primary_key=True)
    code     = Column(String(2))
    name     = Column(String(100))
    
    customer = relation("Customer", order_by="Customer.id", backref="countries")
    
    def __init__(self, code, name):
        
        self.code = code
        self.name = name
        
    def __repr__(self):
        
        return "<Country('%s', '%s')>" % (self.code, self.name)
    
class Customer(Base):
    
    __tablename__  = 'customers'
    
    id             = Column(Integer, primary_key=True)
    last_name      = Column(String(50))
    first_name     = Column(String(50))
    middle_name    = Column(String(50))
    full_name      = Column(String(150))
    gender         = Column(Integer)
    contact_number = Column(String(50))
    street         = Column(String(50))
    city_id        = Column(Integer, ForeignKey('cities.id'))
    state_id       = Column(Integer, ForeignKey('states.id'))
    zip_code       = Column(String(10))
    country_id     = Column(Integer, ForeignKey('countries.id'))
    
    # One2Many
    city    = relation('City', backref=backref('customers', order_by=id))
    state   = relation('State', backref=backref('customers', order_by=id))
    country = relation('Country', backref=backref('customers', order_by=id))
    
    def __init__(self, last_name, first_name, middle_name, gender, 
        contact_number, street, zip_code):
        
        self.last_name      = last_name
        self.first_name     = first_name
        self.middle_name    = middle_name
        self.full_name      = "%s, %s %s." % (last_name, first_name, middle_name[0])
        self.gender         = gender
        self.contact_number = contact_number
        self.street         = street
        self.zip_code       = zip_code
        
    def __repr__(self):
        
        return "<Customer('%s', '%s', '%s', %s, %s, '%s', %s)>" % \
               (self.full_name, self.contact_number, self.street, self.city_id, 
                self.state_id, self.zip_code, self.country_id)
    
    def display(self):
        
        gender = {1:'(M)', 2:'(F)'}
        
        print "Customer ID:", self.id
        print "Name       :", self.full_name, gender[self.gender]
        print "Contact No.:", self.contact_number
        print "Address    : %s, %s" % (self.street, self.city.name)
        print "             %s %s %s" % \
            (self.zip_code, self.state.name, self.country.name)
    
class Director(Base):
    
    __tablename__ = 'directors'
    
    id            = Column(Integer, primary_key=True)
    full_name     = Column(String(100))
    
    def __init__(self, full_name):
        
        self.full_name   = full_name
        
    def __repr__(self):
        
        return "<Director('%s')>" % (self.full_name)
        
class Genre(Base):
    
    __tablename__ = 'genres'
    
    id            = Column(Integer, primary_key=True)
    name          = Column(String(50), unique=True)
    
    # AssociationTables
    movieassoc = relation('MovieGenre', cascade="all, delete-orphan", lazy=False)
    
    # Many2Many
    movies = AssociationProxy('movieassoc', 'movie', creator='MovieGenre')
    
    def __init__(self, name):
        
        self.name = name
        
    def __repr__(self):
        
        return "<Genre('%s')>" % (self.name)
    
class MovieGenre(Base):
    
    __tablename__ = 'movie_genres'
    
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)
    
    genre = relation('Genre', lazy=False)
    movie = relation('Movie', lazy=False)
    
    def __init__(self, genre):
        self.genre = genre
        
    def __repr__(self):
        
        return "<MovieGenre(%s, %s)>" % (self.movie_id, self.genre_id)
    
class MovieCast(Base):
    
    __tablename__ = 'movie_casts'
    
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    cast_id  = Column(Integer, ForeignKey('casts.id'), primary_key=True)
    
    cast = relation('Cast', lazy=False)
    movie = relation('Movie', lazy=False)
    
    def __init__(self, cast):
        self.cast = cast
        
    def __repr__(self):
        
        return "<MovieCast(%s, %s)>" % (self.movie_id, self.cast_id)
    
class MovieWriter(Base):
    
    __tablename__ = 'movie_writers'
    
    movie_id  = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    writer_id = Column(Integer, ForeignKey('writers.id'), primary_key=True)
    
    writer = relation('Writer', lazy=False)
    movie = relation('Movie', lazy=False)
    
    def __init__(self, writer):
        
        self.writer = writer
        
    def __repr__(self):
        
        return "<MovieWriter(%s, %s)>" % (self.movie_id, self.writer_id)
        
class Movie(Base):
    
    __tablename__ = 'movies'
    
    id            = Column(Integer, primary_key=True)
    director_id   = Column(Integer, ForeignKey('directors.id'))
    title         = Column(String(150))
    imdbCode      = Column(String(15))
    release       = Column(String(10))
    plot          = Column(String(500))
    rating        = Column(String(4))
    rent          = Column(Integer)
    allotted      = Column(Integer)
    status        = Column(Integer)
    revenue       = Column(String(150))
    rental        = Column(String(150))
    
    # AssociationTables
    genreassoc = relation('MovieGenre', cascade="all, delete-orphan", lazy=False)
    writerassoc = relation('MovieWriter', cascade="all, delete-orphan", lazy=False)
    castassoc = relation('MovieCast', cascade="all, delete-orphan", lazy=False)
    
    # One2Many
    director      = relation('Director', backref=backref('movies', order_by=id))
    
    # Many2Many
    genres  = AssociationProxy('genreassoc', 'genre', creator=MovieGenre)
    writers = AssociationProxy('writerassoc', 'writer', creator=MovieWriter)
    casts   = AssociationProxy('castassoc', 'cast', creator=MovieCast)
    
    def __init__(self, title, imdbCode, release, plot, rating, rent, allotted, status):
        
        self.title    = title
        self.imdbCode = imdbCode
        self.release  = release
        self.plot     = plot
        self.rating   = rating
        self.rent     = rent
        self.allotted = allotted
        self.status   = status
        self.revenue  = '0.00|0.00|0.00'
        self.rental   = '-.-|-.-|-.-'
        
    def __repr__(self):
        
        return "<Movie('%s', '%s', '%s', '%s', '%s')>" % \
            (self.title, self.imdbCode, self.release, self.plot, self.rating)
    
    def display(self):
        
        print "Title: %s (%s)" % (self.title, self.release)
        print "IMDB : %s" % self.imdbCode
        print "Plot : %s" % self.plot
        print "User Rating: %s" % self.rating
        print "Director:", self.director.full_name
        print "Writers:",
        for writer in self.writers:
            
            print writer.full_name,
            if writer != self.writers[-1]:
                print ';',
    
class State(Base):
    
    __tablename__ = 'states'
    
    id            = Column(Integer, primary_key=True)
    code          = Column(String(6))
    name          = Column(String(100))
    
    # One2Many
    customer = relation("Customer", order_by="Customer.id", backref="states")
    
    def __init__(self, code, name):
        
        self.code = code
        self.name = name
        
    def __repr__(self):
        
        return "<State('%s', '%s')>" % (self.code, self.name)
    
class User(Base):
    
    __tablename__ = "users"
    
    id            = Column(Integer, primary_key=True)
    username      = Column(String(30))
    password      = Column(String(30))
    user_type     = Column(Integer)
    
    def __init__(self, username, password):
        
        self.username = username
        self.password = base64.b64encode(password)
        
    def __repr__(self):
        
        return "<User('%s', '%s', %s)>" \
            % (self.username, self.password, self.user_type)
    
class Writer(Base):
    
    __tablename__ = 'writers'
    
    id            = Column(Integer, primary_key=True)
    full_name     = Column(String(100))
    
    # AssociationTables
    movieassoc = relation('MovieWriter', cascade="all, delete-orphan", lazy=False)
    
    # Many2Many
    movies = AssociationProxy('movieassoc', 'movie', creator='MovieWriter')

    
    def __init__(self, full_name):
        
        self.full_name   = full_name
        
    def __repr__(self):
        
        return "<Writer('%s')>" % (self.full_name)
        
def checkDatabase(db):
    
    """
    Check if database exists. If not, create it.
    """
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///%s" % db)#, echo=True)
    
    Session = sessionmaker()
    Session.configure(bind=engine)
    
    session = Session()
    
    try:
        
        # Try to open file for reading.
        fp = open(db, 'r')
        
    except IOError:
        
        if DEBUG:
        
            print "creating tables................",
            
            metadata = Base.metadata
            metadata.create_all(engine)
            
            print "Done"
            print "populating tables..............",
            
            session = populateTables(session)
            
            print "Done"
            
        else:
            
            metadata = Base.metadata
            metadata.create_all(engine)
            
            session = populateTables(session)
            
        insertDummy(session)
        
    return session
    
def insertCustomer(session, customer, city, state, country):
    
    for city in session.query(City).filter(City.name==city):
        customer.city_id = city.id
    
    for state in session.query(State).filter(State.name==state):
        customer.state_id = state.id
        
    for country in session.query(Country).filter(Country.name==country):
        customer.country_id = country.id
        
    session.add(customer)
    session.commit()
    
    return customer
    
def insertDummy(session):
    
    dr3w = Customer('Kintanar', 'Andrew', 'Son', 1, '+639176232756', 'Miñoza St. Talamban', '6000')
    b3rx = Customer('Kintanar', 'Bertrand', 'Son', 1, '+639152754070', 'Miñoza St. Talamban', '6000')
    ch4n = Customer('Kintanar', 'Christian', 'Son', 1, '+639167162398', 'Miñoza St. Talamban', '6000')
    p4p4 = Customer('Kintanar', 'Nestor', 'Ridad', 1, '+639195874254', 'Silliman Ave. Ext. corner Cervantes St.', '6200')
    
    insertCustomer(session, dr3w, 'Cebu City', 'Cebu', 'Philippines')
    insertCustomer(session, b3rx, 'Cebu City', 'Cebu', 'Philippines')
    insertCustomer(session, ch4n, 'Cebu City', 'Cebu', 'Philippines')
    insertCustomer(session, p4p4, 'Dumaguete', 'Negros Oriental', 'Philippines')
    
    plot = 'Seeking revenge for the death of his love, secret agent James Bond sets out to stop an environmentalist from taking control of a country\'s water supply'
    release = datetime.date(2008, 11, 5)
    
    writers = []
    casts   = []
    genres  = []
    writers.append(Writer('Paul Haggis'))
    writers.append(Writer('Neal Purvis'))
    
    casts.append(Cast('Daniel Craig'))
    casts.append(Cast('Olga Kurylenko'))
    
    session.add(Cast("Aasif Mandvi"))
    session.add(Cast("Adam Sandler"))
    session.add(Cast("Allen Covert"))
    session.add(Cast("Anatole Taubman"))
    session.add(Cast("Andy Gatjen"))
    session.add(Cast("Andy Milder"))
    session.add(Cast("Anil Kapoor"))
    session.add(Cast("Anthony Azizi"))
    session.add(Cast("Anthony Mackie"))
    session.add(Cast("Arthur Dignam"))
    session.add(Cast("Ayush Mahesh Khedekar"))
    session.add(Cast("Azharuddin Mohammed Ismail"))
    session.add(Cast("Barry Pepper"))
    session.add(Cast("Bill Nighy"))
    session.add(Cast("Bill Smitrovich"))
    session.add(Cast("Billy Bob Thornton"))
    session.add(Cast("Brad Oscar"))
    session.add(Cast("Bradley Cooper"))
    session.add(Cast("Brent Briscoe"))
    session.add(Cast("Brian Hutchison"))
    session.add(Cast("Bridget Moloney"))
    session.add(Cast("Bryan Brown"))
    session.add(Cast("Cameron Boyce"))
    session.add(Cast("Carice van Houten"))
    session.add(Cast("Carmen Electra"))
    session.add(Cast("Charles Carroll"))
    session.add(Cast("Charles Shaughnessy"))
    session.add(Cast("Chloe Moretz"))
    session.add(Cast("Christian Berkel"))
    session.add(Cast("Christopher Lloyd"))
    session.add(Cast("Ciarán Hinds"))
    session.add(Cast("Claire Lautier"))
    session.add(Cast("Colleen Camp"))
    session.add(Cast("Courteney Cox"))
    session.add(Cast("Damian Bradford"))
    session.add(Cast("Dan Fogelman"))
    session.add(Cast("Danny Masterson"))
    session.add(Cast("Dariush Kashani"))
    session.add(Cast("David Bamber"))
    session.add(Cast("David Harbour"))
    session.add(Cast("David Schofield"))
    session.add(Cast("Deborah Strang"))
    session.add(Cast("Dequina Moore"))
    session.add(Cast("Dev Patel"))
    session.add(Cast("Diedrich Bader"))
    session.add(Cast("Dustin Hoffman"))
    session.add(Cast("Dwight Yoakam"))
    session.add(Cast("Eddie Izzard"))
    session.add(Cast("Elpidia Carrillo"))
    session.add(Cast("Emma Watson"))
    session.add(Cast("Essie Davis"))
    session.add(Cast("Ethan Embry"))
    session.add(Cast("Fernando Guillén Cuervo"))
    session.add(Cast("Fionnula Flanagan"))
    session.add(Cast("Frances Conroy"))
    session.add(Cast("Frank Langella"))
    session.add(Cast("Freida Pinto"))
    session.add(Cast("Gemma Arterton"))
    session.add(Cast("Giancarlo Giannini"))
    session.add(Cast("Gina Hecht"))
    session.add(Cast("Greg Germann"))
    session.add(Cast("Greg Kinnear"))
    session.add(Cast("Guy Pearce"))
    session.add(Cast("Himanshu Tyagi"))
    session.add(Cast("Hugh Jackman"))
    session.add(Cast("Irrfan Khan"))
    session.add(Cast("J.P. Manoux"))
    session.add(Cast("Jack Donner"))
    session.add(Cast("Jaden Smith"))
    session.add(Cast("Jamal Bednarz-Metallah"))
    session.add(Cast("James Hong"))
    session.add(Cast("James Lipton"))
    session.add(Cast("Jamie Parker"))
    session.add(Cast("Jeanette Miller"))
    session.add(Cast("Jeffrey Wright"))
    session.add(Cast("Jeneva Talwar"))
    session.add(Cast("Jennifer Connelly"))
    session.add(Cast("Jesper Christensen"))
    session.add(Cast("Jesús Ochoa"))
    session.add(Cast("Jim Carrey"))
    session.add(Cast("Jira Banjara"))
    session.add(Cast("Joaquín Cosio"))
    session.add(Cast("Joe Nunez"))
    session.add(Cast("Joey Mazzarino"))
    session.add(Cast("John Cleese"))
    session.add(Cast("John Cothran Jr."))
    session.add(Cast("John Michael Higgins"))
    session.add(Cast("John Rothman"))
    session.add(Cast("John Travolta"))
    session.add(Cast("Jon Favreau"))
    session.add(Cast("Jon Hamm"))
    session.add(Cast("Jon Voight"))
    session.add(Cast("Jonathan Morgan Heit"))
    session.add(Cast("Jonathan Pryce"))
    session.add(Cast("Jordan Carlos"))
    session.add(Cast("Joseph Badalucco Jr."))
    session.add(Cast("Juan Riedinger"))
    session.add(Cast("Judi Dench"))
    session.add(Cast("Judyann Elder"))
    session.add(Cast("Julia K. Murney"))
    session.add(Cast("Kari Wahlgren"))
    session.add(Cast("Kathleen Landis"))
    session.add(Cast("Kathryn Joosten"))
    session.add(Cast("Kathy Bates"))
    session.add(Cast("Katy Mixon"))
    session.add(Cast("Keanu Reeves"))
    session.add(Cast("Kenneth Branagh"))
    session.add(Cast("Keri Russell"))
    session.add(Cast("Kevin Kline"))
    session.add(Cast("Kevin McNally"))
    session.add(Cast("Kristin Chenoweth"))
    session.add(Cast("Kyle Chandler"))
    session.add(Cast("Laura Ann Kesling"))
    session.add(Cast("Lillian Crombie"))
    session.add(Cast("Lucy Lawless"))
    session.add(Cast("Lynn Cohen"))
    session.add(Cast("Madison Pettis"))
    session.add(Cast("Mahesh Manjrekar"))
    session.add(Cast("Malcolm McDowell"))
    session.add(Cast("Mark Walton"))
    session.add(Cast("Mary Steenburgen"))
    session.add(Cast("Mathieu Amalric"))
    session.add(Cast("Matthew Broderick"))
    session.add(Cast("Max Cullen"))
    session.add(Cast("Michael Chiklis"))
    session.add(Cast("Michael Ealy"))
    session.add(Cast("Michelle Monaghan"))
    session.add(Cast("Miley Cyrus"))
    session.add(Cast("Molly Sims"))
    session.add(Cast("Nathin Butler"))
    session.add(Cast("Nick Swardson"))
    session.add(Cast("Nicole Kidman"))
    session.add(Cast("Rajendranath Zutshi"))
    session.add(Cast("Randy Savage"))
    session.add(Cast("Ray Barrett"))
    session.add(Cast("Raymond J. Lee"))
    session.add(Cast("Rebecca Chatfield"))
    session.add(Cast("Reese Witherspoon"))
    session.add(Cast("Rhys Darby"))
    session.add(Cast("Richard Griffiths"))
    session.add(Cast("Richard Jenkins"))
    session.add(Cast("Ricky Gervais"))
    session.add(Cast("Robbie Coltrane"))
    session.add(Cast("Robert Duvall"))
    session.add(Cast("Robert Knepper"))
    session.add(Cast("Robinne Lee"))
    session.add(Cast("Rocky Carroll"))
    session.add(Cast("Ronn Moss"))
    session.add(Cast("Rory Kinnear"))
    session.add(Cast("Rosario Dawson"))
    session.add(Cast("Rukiya Bernard"))
    session.add(Cast("Russell Brand"))
    session.add(Cast("Sam Gilroy"))
    session.add(Cast("Sanchita Couhdary"))
    session.add(Cast("Sarah Jane Morris"))
    session.add(Cast("Sasha Alexander"))
    session.add(Cast("Saurabh Shukla"))
    session.add(Cast("Sean O'Bryan"))
    session.add(Cast("Shea Adams"))
    session.add(Cast("Sheikh Wali"))
    session.add(Cast("Shia LaBeouf"))
    session.add(Cast("Sissy Spacek"))
    session.add(Cast("Spencer Garrett"))
    session.add(Cast("Stanley Tucci"))
    session.add(Cast("Steve Wiebe"))
    session.add(Cast("Sunil Kumar Agrawal"))
    session.add(Cast("Sunita Prasad"))
    session.add(Cast("Susie Essman"))
    session.add(Cast("Tanya Champoux"))
    session.add(Cast("Tara Carpenter"))
    session.add(Cast("Terence Stamp"))
    session.add(Cast("Teresa Palmer"))
    session.add(Cast("Thomas Kretschmann"))
    session.add(Cast("Tim Kelleher"))
    session.add(Cast("Tim McGraw"))
    session.add(Cast("Tim Pigott-Smith"))
    session.add(Cast("Tom Cruise"))
    session.add(Cast("Tom Hollander"))
    session.add(Cast("Tom Wilkinson"))
    session.add(Cast("Tony Barry"))
    session.add(Cast("Tony Hale"))
    session.add(Cast("Tracey Ullman"))
    session.add(Cast("Tyree Michael Simpson"))
    session.add(Cast("Vince Vaughn"))
    session.add(Cast("Will Smith"))
    session.add(Cast("William H. Macy"))
    session.add(Cast("William Sadler"))
    session.add(Cast("Woody Harrelson"))
    session.add(Cast("Zooey Deschanel"))
    
    session.add(Writer("Baz Luhrmann"))
    session.add(Writer("Caleb Wilson"))
    session.add(Writer("Chris Williams"))
    session.add(Writer("Christopher McQuarrie"))
    session.add(Writer("Dan Fogelman"))
    session.add(Writer("David Koepp"))
    session.add(Writer("David Scarpa"))
    session.add(Writer("Edmund H. North"))
    session.add(Writer("Grant Nieporte"))
    session.add(Writer("Jarrad Paul"))
    session.add(Writer("John Glenn"))
    session.add(Writer("John Kamps"))
    session.add(Writer("Kate DiCamillo"))
    session.add(Writer("Matt Allen"))
    session.add(Writer("Matt Lopez"))
    session.add(Writer("Nathan Alexander"))
    session.add(Writer("Nicholas Stoller"))
    session.add(Writer("Simon Beaufoy"))
    session.add(Writer("Stuart Beattie"))
    session.add(Writer("Tim Herlihy"))
    session.add(Writer("Travis Wright"))
    session.add(Writer("Vikas Swarup"))
    session.add(Writer("Will McRobb"))
    
    session.add(Director("Adam Shankman"))
    session.add(Director("Baz Luhrmann"))
    session.add(Director("Bryan Singer"))
    session.add(Director("Byron Howard"))
    session.add(Director("D.J. Caruso"))
    session.add(Director("Danny Boyle"))
    session.add(Director("David Koepp"))
    session.add(Director("Gabriele Muccino"))
    session.add(Director("Peyton Reed"))
    session.add(Director("Sam Fell"))
    session.add(Director("Scott Derrickson"))
    session.add(Director("Seth Gordon"))
    
    director = Director('Marc Foster')
    
    genres.append(Genre('Action'))
    genres.append(Genre('Adventure'))
    genres.append(Genre('Thriller'))
    
    movie = Movie('Quantum of Solace', 'tt0830515', release, plot, '7.1', 15, 3, 1)
    
    insertMovie(session, movie, director, writers, casts, genres)
    
    b3rx = User('b3rx', 'retardko')
    b3rx.user_type = 1
    
    session.add(b3rx)
    session.commit()

def insertMovie(session, movie, director, writers, casts, genres):
    
    movie.director = getDirector(session, director)
    
    for writer in writers:
        
        movie.writers.append(getWriter(session, writer))
        
    for cast in casts:
        
        movie.casts.append(getCast(session, cast))
        
    for genre in genres:
        
        movie.genres.append(getGenre(session, genre))
        
    session.add(movie)
    session.commit()
    
    return movie
    
def populateTables(session):
    
    states = {
        'PH-ABR':'Abra', 'PH-AGN':'Agusan del Norte', 
        'PH-AGS':'Agusan del Sur', 'PH-AKL':'Aklan', 'PH-ALB':'Albay', 
        'PH-ANT':'Antique', 'PH-APA':'Apayao', 'PH-AUR':'Aurora', 
        'PH-BAS':'Basilan', 'PH-BAN':'Bataan', 'PH-BTN':'Batanes', 
        'PH-BTG':'Batangas', 'PH-BEN':'Benguet', 'PH-BIL':'Biliran', 
        'PH-BOH':'Bohol', 'PH-BUK':'Bukidnon', 'PH-BUL':'Bulacan', 
        'PH-CAG':'Cagayan', 'PH-CAN':'Camarines Norte', 'PH-CAS':'Camarines Sur', 
        'PH-CAM':'Camiguin', 'PH-CAP':'Capiz', 'PH-CAT':'Catanduanes', 
        'PH-CAV':'Cavite', 'PH-CEB':'Cebu', 'PH-COM':'Compostela Valley', 
        'PH-DAV':'Davao del Norte', 'PH-DAS':'Davao del Sur', 
        'PH-DAO':'Davao Oriental', 'PH-EAS':'Eastern Samar', 
        'PH-GUI':'Guimaras', 'PH-IFU':'Ifugao', 'PH-ILN':'Ilocos Norte', 
        'PH-ILS':'Ilocos Sur', 'PH-ILI':'Iloilo', 'PH-ISA':'Isabela', 
        'PH-KAL':'Kalinga', 'PH-LAG':'Laguna', 'PH-LAN':'Lanao del Norte', 
        'PH-LAS':'Lanao del Sur', 'PH-LUN':'La Union', 'PH-LEY':'Leyte', 
        'PH-MAG':'Maguindanao', 'PH-MAD':'Marinduque', 'PH-MAS':'Masbate', 
        'PH-MDC':'Mindoro Occidental', 'PH-MDR':'Mindoro Oriental', 
        'PH-MSC':'Misamis Occidental', 'PH-MSR':'Misamis Oriental', 
        'PH-MOU':'Mountain Province', 'PH-NEC':'Negros Occidental', 
        'PH-NER':'Negros Oriental', 'PH-NCO':'Cotabato', 
        'PH-NSA':'Northern Samar', 'PH-NUE':'Nueva Ecija', 
        'PH-NUV':'Nueva Vizcaya', 'PH-PLW':'Palawan', 'PH-PAM':'Pampanga', 
        'PH-PAN':'Pangasinan', 'PH-QUE':'Quezon', 'PH-QUI':'Quirino', 
        'PH-RIZ':'Rizal', 'PH-ROM':'Romblon', 'PH-SAR':'Sarangani', 
        'PH-SIG':'Siquijor', 'PH-SOR':'Sorsogon', 'PH-SCO':'South Cotabato', 
        'PH-SLE':'Southern Leyte', 'PH-SUK':'Sultan Kudarat', 'PH-SLU':'Sulu', 
        'PH-SUN':'Surigao del Norte', 'PH-SUR':'Surigao del Sur', 
        'PH-TAR':'Tarlac', 'PH-TAW':'Tawi-Tawi', 'PH-WSA':'Samar', 
        'PH-ZMB':'Zambales', 'PH-ZAN':'Zamboanga del Norte', 
        'PH-ZAS':'Zamboanga del Sur', 'PH-ZSI':'Zamboanga Sibugay'
    }
    
    cities = (
        'Aborlan', 'Abra de Ilog', 'Abucay', 'Abulug', 'Abuyog', 'Adams', 
        'Agdangan', 'Aglipay', 'Agno', 'Agoncillo', 'Agoo', 'Aguilar', 
        'Aguinaldo', 'Agutaya', 'Ajuy', 'Akbar', 'Alabat', 'Alabel', 'Alamada', 
        'Alaminos', 'Alaminos City', 'Alangalang', 'Al-Barka', 'Albuera', 
        'Alburquerque', 'Alcala', 'Alcantara', 'Alcoy', 'Alegria', 'Aleosan', 
        'Alfonso', 'Alfonso Castaneda', 'Alfonso Lista', 'Aliaga', 'Alicia', 
        'Alilem', 'Alimodian', 'Alitagtag', 'Allacapan', 'Allen', 'Almagro', 
        'Almeria', 'Aloguinsan', 'Aloran', 'Altavas', 'Alubijid', 'Amadeo', 
        'Ambaguio', 'Amlan', 'Ampatuan', 'Amulung', 'Anahawan', 'Anao', 
        'Anda', 'Angadanan', 'Angat', 'Angeles City', 'Angono', 'Anilao', 
        'Anini-y', 'Antequera', 'Antipas', 'Antipolo City', 'Apalit', 'Aparri', 
        'Araceli', 'Arakan', 'Arayat', 'Argao', 'Aringay', 'Aritao', 'Aroroy', 
        'Arteche', 'Asingan', 'Asipulo', 'Asturias', 'Asuncion', 'Atimonan', 
        'Atok', 'Aurora', 'Ayungon', 'Baao', 'Babatngon', 'Bacacay', 'Bacarra', 
        'Baclayon', 'Bacnotan', 'Baco', 'Bacolod', 'Bacolod City', 
        'Bacolod-Kalawi', 'Bacolor', 'Bacong', 'Bacoor', 'Bacuag', 'Bacungan', 
        'Badian', 'Badiangan', 'Badoc', 'Bagabag', 'Bagac', 'Bagamanoc', 
        'Baganga', 'Baggao', 'Bago City', 'Baguio City', 'Bagulin', 'Bagumbayan', 
        'Bais', 'Bakun', 'Balabac', 'Balabagan', 'Balagtas', 'Balamban', 
        'Balanga City', 'Balangiga', 'Balangkayan', 'Balaoan', 'Balasan', 
        'Balatan', 'Balayan', 'Balbalan', 'Baleno', 'Baler', 'Balete', 
        'Baliangao', 'Baliguian', 'Balilihan', 'Balindong', 'Balingasag', 
        'Balingoan', 'Baliuag', 'Ballesteros', 'Baloi', 'Balud', 'Balungao', 
        'Bamban', 'Bambang', 'Banate', 'Banaue', 'Banaybanay', 'Banayoyo', 
        'Banga', 'Bangar', 'Bangued', 'Bangui', 'Bani', 'Banisilan', 
        'Banna', 'Bansalan', 'Bansud', 'Bantay', 'Bantayan', 'Banton', 'Baras', 
        'Barbaza', 'Barcelona', 'Barili', 'Barira', 'Barlig', 'Barobo', 
        'Barotac Nuevo', 'Barotac Viejo', 'Baroy', 'Barugo', 'Basay', 
        'Basco', 'Basey', 'Basilisia (Rizal)', 'Basista', 'Basud', 'Batac City', 
        'Batad', 'Batan', 'Batangas City', 'Bataraza', 'Bato', 'Batuan', 'Bauan', 
        'Bauang', 'Bauko', 'Baungon', 'Bautista', 'Bay', 'Bayabas', 'Bayambang', 
        'Bayang', 'Bayawan', 'Baybay City', 'Bayog', 'Bayombong', 'Bayugan', 
        'Belison', 'Benito Soliven', 'Besao', 'Bien Unido', 'Bilar', 'Biliran', 
        'Binalbagan', 'Binalonan', 'Biñan', 'Binangonan', 'Bindoy', 
        'Bingawan', 'Binidayan', 'Binmaley', 'Binuangan', 'Biri', 'Bislig City', 
        'Boac', 'Bobon', 'Bocaue', 'Bogo City', 'Bokod', 'Bolinao', 'Boliney', 
        'Boljoon', 'Bombon', 'Bongabon', 'Bongabong', 'Bongao', 'Bonifacio', 
        'Bontoc', 'Borbon', 'Borongan City', 'Boston', 'Botolan', 
        'Braulio E. Dujali', 'Brooke\'s Point', 'Buadiposo-Buntong', 'Bubong', 
        'Bucay', 'Bucloc', 'Buenavista', 'Bugallon', 'Bugasong', 'Buguey', 
        'Buguias', 'Buhi', 'Bula', 'Bulacan', 'Bulalacao', 'Bulan', 'Buldon', 
        'Buluan', 'Bulusan', 'Bumbaran', 'Bunawan', 'Burauen', 'Burdeos', 
        'Burgos', 'Buruanga', 'Bustos', 'Busuanga', 'Butig', 'Butuan City', 
        'Buug', 'Caba', 'Cabadbaran City', 'Cabagan', 'Cabanatuan City', 
        'Cabangan', 'Cabanglasan', 'Cabarroguis', 'Cabatuan', 'Cabiao', 
        'Cabucgayan', 'Cabugao', 'Cabusao', 'Cabuyao', 'Cadiz City', 
        'Cagayan de Oro', 'Cagayancillo', 'Cagdianao', 'Cagwait', 'Caibiran', 
        'Cainta', 'Cajidiocan', 'Calabanga', 'Calaca', 'Calamba', 'Calamba City', 
        'Calanasan', 'Calanogas', 'Calapan City', 'Calape', 'Calasiao', 
        'Calatagan', 'Calatrava', 'Calauag', 'Calauan', 'Calayan', 
        'Calbayog City', 'Calbiga', 'Calinog', 'Calintaan', 'Caloocan', 
        'Calubian', 'Calumpit', 'Caluya', 'Camalaniugan', 'Camalig', 'Camaligan', 
        'Camiling', 'Canaman', 'Can-avid', 'Candaba', 'Candelaria', 'Candijay', 
        'Candon City', 'Candoni', 'Canlaon', 'Cantilan', 'Caoayan', 'Capalonga', 
        'Capas', 'Capoocan', 'Capul', 'Caraga', 'Caramoan', 'Caramoran', 
        'Carasi', 'Carcar City', 'Cardona', 'Carigara', 'Carles', 'Carmen', 
        'Carmona', 'Carranglan', 'Carrascal', 'Casiguran', 'Castilla', 
        'Castillejos', 'Cataingan', 'Catanauan', 'Catarman', 'Catbalogan City', 
        'Cateel', 'Catigbian', 'Catmon', 'Catubig', 'Cauayan', 'Cauayan City', 
        'Cavinti', 'Cavite City', 'Cawayan', 'Cebu City', 'Cervantes', 'Clarin', 
        'Claver', 'Claveria', 'Columbio', 'Compostela', 'Concepcion', 'Conner', 
        'Consolacion', 'Corcuera', 'Cordoba', 'Cordon', 'Corella', 'Coron', 
        'Cortes', 'Cotabato City', 'Cuartero', 'Cuenca', 'Culaba', 'Culasi', 
        'Culion', 'Currimao', 'Cuyapo', 'Cuyo', 'Daanbantayan', 'Daet', 'Dagami', 
        'Dagohoy', 'Daguioman', 'Dagupan City', 'Dalaguete', 'Damulog', 'Danao', 
        'Danao City', 'Dangcagan', 'Danglas', 'Dao', 'Dapa', 'Dapitan City', 
        'Daraga', 'Daram', 'Dasmariñas', 'Dasol', 'Datu Abdullah Sangki', 
        'Datu Anggal Midtimbang', 'Datu Blah T. Sinsuat', 'Datu Odin Sinsuat', 
        'Datu Paglas', 'Datu Piang', 'Datu Saudi-Ampatuan', 'Datu Unsay', 
        'Dauin', 'Dauis', 'Davao City', 'Del Carmen', 'Del Gallego', 
        'Delfin Albano', 'Diadi', 'Diffun', 'Digos City', 'Dilasag', 
        'Dimasalang', 'Dimataling', 'Dimiao', 'Dinagat', 'Dinalungan', 
        'Dinalupihan', 'Dinapigue', 'Dinas', 'Dingalan', 'Dingle', 'Dingras', 
        'Dipaculao', 'Diplahan', 'Dipolog City', 'Ditsaan-Ramain', 'Divilacan', 
        'Dolores', 'Don Carlos', 'Don Marcelino', 'Don Victoriano Chiongbian', 
        'Doña Remedios Trinidad', 'Donsol', 'Dueñas', 'Duero', 'Dulag', 
        'Dumaguete', 'Dumalag', 'Dumalinao', 'Dumalneg', 'Dumangas', 'Dumanjug', 
        'Dumaran', 'Dumarao', 'Dumingag', 'Dupax del Norte', 'Dupax del Sur', 
        'Echague', 'El Nido', 'El Salvador', 'El Salvador City', 'Enrile', 
        'Enrique B. Magalona', 'Enrique Villanueva', 'Escalante City', 
        'Esperanza', 'Estancia', 'Famy', 'Ferrol', 'Flora', 'Floridablanca', 
        'Gabaldon', 'Gainza', 'Galimuyod', 'Gamay', 'Gamu', 'Ganassi', 'Gandara', 
        'Gapan City', 'Garchitorena', 'Garcia Hernandez', 'Gasan', 'Gattaran', 
        'Gen. Emilio Aguinaldo', 'Gen. Mariano Alvarez', 'Gen. S. K. Pendatun', 
        'Gen. Trias', 'General Luna', 'General MacArthur', 
        'General Mamerto Natividad', 'General Nakar', 'General Santos City', 
        'General Tinio', 'Gerona', 'Gigaquit', 'Gigmoto', 'Ginatilan', 
        'Gingoog City', 'Giporlos', 'Gitagum', 'Glan', 'Gloria', 'Goa', 'Godod', 
        'Gonzaga', 'Governor Generoso', 'Gregorio Del Pilar', 'Guagua', 'Gubat', 
        'Guiguinto', 'Guihulngan', 'Guimba', 'Guimbal', 'Guinayangan', 
        'Guindulman', 'Guindulungan', 'Guinobatan', 'Guinsiliban', 'Guipos', 
        'Guiuan', 'Gumaca', 'Gutalac', 'Hadji Mohammad Aju', 
        'Hadji Panglima Tahil', 'Hagonoy', 'Hamtic', 'Hermosa', 'Hernani', 
        'Hilongos', 'Himamaylan City', 'Hinabangan', 'Hinatuan', 'Hindang', 
        'Hingyon', 'Hinigaran', 'Hinoba-an', 'Hinunangan', 'Hinundayan', 
        'Hungduan', 'Iba', 'Ibaan', 'Ibajay', 'Igbaras', 'Iguig', 'Ilagan', 
        'Iligan City', 'Ilog', 'Iloilo City', 'Imelda', 'Impasug-Ong', 'Imus', 
        'Inabanga', 'Indanan', 'Indang', 'Infanta', 'Initao', 'Inopacan', 'Ipil', 
        'Iriga City', 'Irosin', 'Isabel', 'Isabela', 'Isabela City', 
        'Island Garden City of Samal', 'Isulan', 'Itbayat', 'Itogon', 'Ivana', 
        'Ivisan', 'Jabonga', 'Jaen', 'Jagna', 'Jalajala', 'Jamindan', 'Janiuay', 
        'Jaro', 'Jasaan', 'Javier', 'Jetafe', 'Jiabong', 'Jimalalud', 'Jimenez', 
        'Jipapad', 'Jolo', 'Jomalig', 'Jones', 'Jordan', 'Jose Abad Santos', 
        'Jose Dalman', 'Jose Panganiban', 'Josefina', 'Jovellar', 'Juban', 
        'Julita', 'Kabacan', 'Kabankalan City', 'Kabasalan', 'Kabayan', 
        'Kabugao', 'Kabuntalan', 'Kadingilan', 'Kalamansig', 'Kalawit', 
        'Kalayaan', 'Kalibo', 'Kalilangan', 'Kalingalan Caluang', 'Kananga', 
        'Kapai', 'Kapalong', 'Kapangan', 'Kapatagan', 'Kasibu', 'Katipunan', 
        'Kauswagan', 'Kawayan', 'Kawit', 'Kayapa', 'Kiamba', 'Kiangan', 'Kibawe', 
        'Kiblawan', 'Kibungan', 'Kidapawan City', 'Kinoguitan', 'Kitaotao', 
        'Kitcharao', 'Kolambugan', 'Koronadal City', 'Kumalarang', 
        'La Carlota City', 'La Castellana', 'La Libertad', 'La Paz', 
        'La Trinidad', 'Laak', 'Labangan', 'Labason', 'Labo', 'Labrador', 
        'Lacub', 'Lagangilang', 'Lagawe', 'Lagayan', 'Lagonglong', 'Lagonoy', 
        'Laguindingan', 'Lake Sebu', 'Lakewood', 'Lala', 'Lal-Lo', 'Lambayong', 
        'Lambunao', 'Lamitan City', 'Lamut', 'Langiden', 'Languyan', 'Lantapan', 
        'Lantawan', 'Lanuza', 'Laoac', 'Laoag City', 'Laoang', 'Lapinig', 
        'Lapu-Lapu City', 'Lapuyan', 'Larena', 'Las Navas', 'Las Nieves', 
        'Las Piñas', 'Lasam', 'Laua-an', 'Laur', 'Laurel', 'Lavezares', 
        'Lawaan', 'Lazi', 'Lebak', 'Leganes', 'Legazpi City', 'Lemery', 'Leon', 
        'Leyte', 'Lezo', 'Lian', 'Lianga', 'Libacao', 'Libagon', 'Libertad', 
        'Libjo (Albor)', 'Libmanan', 'Libon', 'Libona', 'Libungan', 'Licab', 
        'Licuan-Baay', 'Lidlidda', 'Ligao City', 'Lila', 'Liliw', 'Liloan', 
        'Liloy', 'Limasawa', 'Limay', 'Linamon', 'Linapacan', 'Lingayen', 
        'Lingig', 'Lipa City', 'Llanera', 'Llorente', 'Loay', 'Lobo', 'Loboc', 
        'Looc', 'Loon', 'Lope de Vega', 'Lopez', 'Lopez Jaena', 'Loreto', 
        'Los Baños', 'Luba', 'Lubang', 'Lubao', 'Lubuagan', 'Lucban', 
        'Lucena City', 'Lugait', 'Lugus', 'Luisiana', 'Lumba-Bayabao', 
        'Lumbaca-Unayan', 'Lumban', 'Lumbatan', 'Lumbayanague', 'Luna', 'Lupao', 
        'Lupi', 'Lupon', 'Lutayan', 'Luuk', 'Maasim', 'Maasin', 'Maasin City', 
        'Ma-ayon', 'Mabalacat', 'Mabinay', 'Mabini', 'Mabitac', 'Mabuhay', 
        'Macabebe', 'Macalelon', 'Macarthur', 'Maco', 'Maconacon', 'Macrohon', 
        'Madalag', 'Madalum', 'Madamba', 'Maddela', 'Madrid', 'Madridejos', 
        'Magalang', 'Magallanes', 'Magarao', 'Magdalena', 'Magdiwang', 'Magpet', 
        'Magsaysay', 'Magsingal', 'Maguing', 'Mahaplag', 'Mahatao', 'Mahayag', 
        'Mahinog', 'Maigo', 'Maimbung', 'Mainit', 'Maitum', 'Majayjay', 'Makati', 
        'Makato', 'Makilala', 'Malabang', 'Malabon', 'Malabuyoc', 'Malalag', 
        'Malangas', 'Malapatan', 'Malasiqui', 'Malay', 'Malaybalay City', 
        'Malibcong', 'Malilipot', 'Malimono', 'Malinao', 'Malita', 
        'Malitbog', 'Mallig', 'Malolos City', 'Malungon', 'Maluso', 'Malvar', 
        'Mamasapano', 'Mambajao', 'Mamburao', 'Mambusao', 'Manabo', 'Manaoag', 
        'Manapla', 'Manay', 'Mandaluyong', 'Mandaon', 'Mandaue City', 
        'Mangaldan', 'Mangatarem', 'Mangudadatu', 'Manila', 'Manito', 'Manjuyod', 
        'Mankayan', 'Manolo Fortich', 'Mansalay', 'Manticao', 'Manukan', 
        'Mapanas', 'Mapandan', 'Mapun', 'Marabut', 'Maragondon', 'Maragusan', 
        'Maramag', 'Marantao', 'Marawi City', 'Marcos', 'Margosatubig', 'Maria', 
        'Maria Aurora', 'Maribojoc', 'Marihatag', 'Marikina', 'Marilao', 
        'Maripipi', 'Mariveles', 'Marogong', 'Masantol', 'Masbate City', 
        'Masinloc', 'Masiu', 'Maslog', 'Mataas na Kahoy', 'Matag-ob', 'Matalom', 
        'Matanao', 'Matanog', 'Mati City', 'Matnog', 'Matuguinao', 'Matungao', 
        'Mauban', 'Mawab', 'Mayantoc', 'Maydolong', 'Mayorga', 'Mayoyao', 
        'Medellin', 'Medina', 'Mendez', 'Mercedes', 'Merida', 'Mexico', 
        'Meycauayan City', 'Miagao', 'Midsalip', 'Midsayap', 'Milagros', 
        'Milaor', 'Mina', 'Minalabac', 'Minalin', 'Minglanilla', 'M\'Lang', 
        'Moalboal', 'Mobo', 'Mogpog', 'Moises Padilla', 'Molave', 'Moncada', 
        'Mondragon', 'Monkayo', 'Monreal', 'Montevista', 'Morong', 'Motiong', 
        'Mulanay', 'Mulondo', 'Munai', 'Muntinlupa', 'Murcia', 'Mutia', 'Naawan', 
        'Nabas', 'Nabua', 'Nabunturan', 'Naga', 'Naga City', 'Nagbukel', 
        'Nagcarlan', 'Nagtipunan', 'Naguilian', 'Naic', 'Nampicuan', 'Narra', 
        'Narvacan', 'Nasipit', 'Nasugbu', 'Natividad', 'Natonin', 'Naujan', 
        'Naval', 'Navotas', 'New Bataan', 'New Corella', 'New Lucena', 
        'New Washington', 'Norala', 'Northern Kabuntalan', 'Norzagaray', 
        'Noveleta', 'Nueva Era', 'Nueva Valencia', 'Numancia', 'Nunungan', 'Oas', 
        'Obando', 'Ocampo', 'Odiongan', 'Old Panamao', 'Olongapo City', 
        'Olutanga', 'Omar', 'Opol', 'Orani', 'Oras', 'Orion', 'Ormoc City', 
        'Oroquieta City', 'Oslob', 'Oton', 'Ozamis City', 'Padada', 
        'Padre Burgos', 'Padre Garcia', 'Paete', 'Pagadian City', 'Pagagawan', 
        'Pagalungan', 'Pagayawan', 'Pagbilao', 'Paglat', 'Pagsanghan', 
        'Pagsanjan', 'Pagudpud', 'Pakil', 'Palanan', 'Palanas', 'Palapag', 
        'Palauig', 'Palayan City', 'Palimbang', 'Palo', 'Palompon', 'Paluan', 
        'Pambujan', 'Pamplona', 'Panabo City', 'Panaon', 'Panay', 
        'Pandag', 'Pandami', 'Pandan', 'Pandi', 'Panganiban', 
        'Pangantucan', 'Pangil', 'Panglao', 'Panglima Estino', 'Panglima Sugala', 
        'Pangutaran', 'Paniqui', 'Panitan', 'Pantabangan', 'Pantao Ragat', 
        'Pantar', 'Pantukan', 'Panukulan', 'Paoay', 'Paombong', 'Paracale', 
        'Paracelis', 'Parañaque', 'Paranas', 'Parang', 'Pasacao', 'Pasay', 
        'Pasig', 'Pasil', 'Passi City', 'Pastrana', 'Pasuquin', 'Pata', 
        'Pateros', 'Patikul', 'Patnanungan', 'Patnongon', 'Pavia', 'Payao', 
        'Peñablanca', 'Peñaranda', 'Peñarrubia', 'Perez', 'Piagapo', 'Piat', 
        'Picong', 'Piddig', 'Pidigan', 'Pigkawayan', 'Pikit', 'Pila', 'Pilar', 
        'Pili', 'Pililla', 'Pinabacdao', 'Pinamalayan', 'Pinamungahan', 'Piñan', 
        'Pinili', 'Pintuyan', 'Pinukpuk', 'Pio Duran', 'Pio V. Corpuz', 'Pitogo', 
        'Placer', 'Plaridel', 'Pola', 'Polanco', 'Polangui', 'Polillo', 
        'Polomolok', 'Pontevedra', 'Poona Bayabao', 'Poona Piagapo', 'Porac', 
        'Poro', 'Pototan', 'Pozzorubio', 'Pres. Carlos P. Garcia', 
        'Pres. Manuel A. Roxas', 'Presentacion', 'President Quirino', 
        'Prieto Diaz', 'Prosperidad', 'Pualas', 'Pudtol', 'Puerto Galera', 
        'Puerto Princesa City', 'Pugo', 'Pulilan', 'Pulupandan', 'Pura', 
        'Quezon', 'Quezon City', 'Quinapondan', 'Quirino', 'Ragay', 
        'Rajah Buayan', 'Ramon', 'Ramon Magsaysay', 'Ramos', 'Rapu-Rapu', 'Real', 
        'Reina Mercedes', 'Remedios T. Romualdez', 'Rizal', 'Rodriguez', 
        'Romblon', 'Ronda', 'Rosales', 'Rosario', 'Roseller Lim', 'Roxas', 
        'Roxas City', 'Sabangan', 'Sablan', 'Sablayan', 'Sabtang', 'Sadanga', 
        'Sagada', 'Sagay', 'Sagay City', 'Sagbayan', 'Sagñay', 'Saguday', 
        'Saguiaran', 'Saint Bernard', 'Salay', 'Salcedo', 'Sallapadan', 'Salug', 
        'Salvador', 'Salvador Benedicto', 'Samal', 'Samboan', 'Sampaloc', 
        'San Agustin', 'San Andres', 'San Antonio', 'San Benito', 
        'San Carlos City', 'San Clemente', 'San Dionisio', 'San Emilio', 
        'San Enrique', 'San Esteban', 'San Fabian', 'San Felipe', 'San Fernando', 
        'San Fernando City', 'San Francisco', 'San Gabriel', 'San Guillermo', 
        'San Ildefonso', 'San Isidro', 'San Jacinto', 'San Joaquin', 'San Jorge', 
        'San Jose', 'San Jose City', 'San Jose De Buan', 
        'San Jose del Monte City', 'San Juan', 'San Julian', 'San Leonardo', 
        'San Lorenzo', 'San Lorenzo Ruiz', 'San Luis', 'San Manuel', 
        'San Marcelino', 'San Mariano', 'San Mateo', 'San Miguel', 'San Narciso', 
        'San Nicolas', 'San Pablo', 'San Pablo City', 'San Pascual', 'San Pedro', 
        'San Policarpo', 'San Quintin', 'San Rafael', 'San Remigio', 
        'San Ricardo', 'San Roque', 'San Sebastian', 'San Simon', 'San Teodoro', 
        'San Vicente', 'Sanchez-Mira', 'Santa', 'Santa Ana', 'Santa Barbara', 
        'Santa Catalina', 'Santa Cruz', 'Santa Elena', 'Santa Fe', 
        'Santa Ignacia', 'Santa Josefa', 'Santa Lucia', 'Santa Magdalena', 
        'Santa Marcela', 'Santa Margarita', 'Santa Maria', 'Santa Monica', 
        'Santa Praxedes', 'Santa Rita', 'Santa Rosa', 'Santa Rosa City', 
        'Santa Teresita', 'Santander', 'Santiago', 'Santiago City', 
        'Santo Domingo', 'Santo Niño', 'Santo Tomas', 'Santol', 'Sapad', 
        'Sapang Dalaga', 'Sapa-Sapa', 'Sapi-an', 'Sara', 'Sarangani', 'Sariaya', 
        'Sarrat', 'Sasmuan', 'Science City of Muñoz', 'Sebaste', 
        'Sen. Ninoy Aquino', 'Sergio Osmeña Sr.', 'Sevilla', 'Shariff Aguak', 
        'Siasi', 'Siaton', 'Siay', 'Siayan', 'Sibagat', 'Sibalom', 'Sibonga', 
        'Sibuco', 'Sibulan', 'Sibunag', 'Sibutad', 'Sibutu', 'Sierra Bullones', 
        'Sigay', 'Sigma', 'Sikatuna', 'Silago', 'Silang', 'Silay City', 
        'Silvino Lobos', 'Simunul', 'Sinacaban', 'Sinait', 'Sindangan', 
        'Siniloan', 'Siocon', 'Sipalay City', 'Sipocot', 'Siquijor', 'Sirawai', 
        'Siruma', 'Sison', 'Sitangkai', 'Socorro', 'Sofronio Española', 'Sogod', 
        'Solana', 'Solano', 'Solsona', 'Sominot', 'Sorsogon City', 'South Ubian', 
        'South Upi', 'Sual', 'Subic', 'Sudipen', 'Sugbongcogon', 'Sugpon', 
        'Sulat', 'Sulop', 'Sultan Dumalondong', 'Sultan Kudarat', 'Sultan Mastura', 
        'Sultan Naga Dimaporo', 'Sultan sa Barongis', 'Sumilao', 'Sumisip', 
        'Surallah', 'Surigao City', 'Suyo', 'Taal', 'Tabaco City', 'Tabango', 
        'Tabina', 'Tabogon', 'Tabontabon', 'Tabuelan', 'Tabuk City', 
        'Tacloban City', 'Tacurong City', 'Tadian', 'Taft', 'Tagana-an', 
        'Tagapul-an', 'Tagaytay City', 'Tagbilaran City', 'Tagbina', 
        'Tagkawayan', 'Tago', 'Tagoloan', 'Tagoloan Ii', 'Tagudin', 'Taguig', 
        'Tagum City', 'Talacogon', 'Talaingod', 'Talakag', 'Talalora', 
        'Talavera', 'Talayan', 'Talibon', 'Talipao', 'Talisay', 'Talisay City', 
        'Talisayan', 'Talitay', 'Talugtug', 'Talusan', 'Tambulig', 'Tampakan', 
        'Tamparan', 'Tampilisan', 'Tanauan', 'Tanauan City', 'Tanay', 
        'Tandag City', 'Tandubas', 'Tangalan', 'Tangcal', 'Tangub City', 
        'Tanjay', 'Tantangan', 'Tanudan', 'Tanza', 'Tapaz', 'Tapul', 'Taraka', 
        'Tarangnan', 'Tarlac City', 'Tarragona', 'Tayabas City', 'Tayasan', 
        'Taysan', 'Taytay', 'Tayug', 'Tayum', 'T\'Boli', 'Teresa', 'Ternate', 
        'Tiaong', 'Tibiao', 'Tigaon', 'Tigbao', 'Tigbauan', 'Tinambac', 'Tineg', 
        'Tinglayan', 'Tingloy', 'Tinoc', 'Tipo-Tipo', 'Titay', 'Tiwi', 
        'Tobias Fornier', 'Toboso', 'Toledo City', 'Tolosa', 'Tomas Oppus', 
        'Tongkil', 'Torrijos', 'Trece Martires City', 'Trento', 'Trinidad', 
        'Tuao', 'Tuba', 'Tubajon', 'Tubao', 'Tubaran', 'Tubay', 'Tubigon', 
        'Tublay', 'Tubo', 'Tubod', 'Tubungan', 'Tuburan', 'Tudela', 'Tugaya', 
        'Tuguegarao City', 'Tukuran', 'Tulunan', 'Tumauini', 'Tunga', 'Tungawan', 
        'Tupi', 'Turtle Islands', 'Tuy', 'Ubay', 'Umingan', 'Ungkaya Pukan', 
        'Unisan', 'Upi', 'Urbiztondo', 'Urdaneta City', 'Uson', 'Uyugan', 
        'Valderrama', 'Valencia', 'Valencia City', 'Valenzuela', 'Valladolid', 
        'Vallehermoso', 'Veruela', 'Victoria', 'Victorias City', 'Viga', 
        'Vigan City', 'Villaba', 'Villanueva', 'Villareal', 'Villasis', 
        'Villaverde', 'Villaviciosa', 'Vincenzo A. Sagun', 'Vintar', 'Vinzons', 
        'Virac', 'Wao', 'Zamboanga City', 'Zamboanguita', 'Zaragoza', 'Zarraga', 
        'Zumarraga'
    )
    
    genres = (
        'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 
        'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 
        'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News', 
        'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Talk-Show', 
        'Thriller', 'War', 'Western'
    )
    
    # add states to the database
    for code, state in states.items():
        
        session.add(State(code, state))
        
    # add cities to the database
    for city in cities:
        
        session.add(City(city))
        
    # add genres to the database
    for genre in genres:
        
        session.add(Genre(genre))
        
    # add a country to the database
    session.add(Country('PH', 'Philippines'))
        
    session.commit()
    
    return session

def getGenre(session, genre):
    
    """
    checks the table Genre and returns a Genre object to the calling environment.
    """
    try:
        return session.query(Genre).filter_by(name=genre.name).one()
    
    except NoResultFound:
        
        session.add(genre)
        session.commit()
        
        if DEBUG:
            
            print "New genre added", genre
        
        return session.query(Genre).filter_by(name=genre.name).one()
    
def getCast(session, cast):
    
    """
    checks the table Cast and returns a Cast object to the calling environment.
    """
    try:
        
        return session.query(Cast).filter_by(full_name=cast.full_name).one()
    
    except NoResultFound:
        
        session.add(cast)
        session.commit()
        
        if DEBUG:
            
            print "New cast added", cast
        
        return session.query(Cast).filter_by(full_name=cast.full_name).one()
    
def getDirector(session, director):
    
    """
    checks the table Director and returns a Directors object to the calling environment.
    """
    try:
        
        return session.query(Director).filter_by(full_name=director.full_name).one()
    
    except NoResultFound:
        
        session.add(director)
        session.commit()
        
        if DEBUG:
            
            print "New director added", director
        
        return session.query(Director).filter_by(full_name=director.full_name).one()
    
def getWriter(session, writer):
    
    """
    checks the table Writer and returns a Writer object to the calling environment.
    """
    try:
        
        return session.query(Writer).filter_by(full_name=writer.full_name).one()
    
    except NoResultFound:
        
        session.add(writer)
        session.commit()
        
        if DEBUG:
            
            print "New writer added", writer
        
        return session.query(Writer).filter_by(full_name=writer.full_name).one()
    
def main():
    
    session = checkDatabase('posvrsys.sqlite')
    
    for instance in session.query(Customer):
        
        instance.display()
        
    session.close()
        
if __name__ == '__main__':
    
    main()
    
    sys.exit(0)
    