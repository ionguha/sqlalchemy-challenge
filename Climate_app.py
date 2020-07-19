##############################################
# Designing a Flask API
##############################################
# Importing the required libraries
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# Importing Flask and jsonify
from flask import Flask, jsonify
from flask import render_template

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo = False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Mapping measurement class
Measurement = Base.classes.measurement
# Mapping station class
Station = Base.classes.station

#################################################
# Querying dates in the database
#################################################
# Create our session (link) from Python to the DB
session = Session(bind=engine)
# Let's count the total dates we have
total_dates = session.query(func.count(Measurement.date)).first()
# Let's find the earliest date
earliest_date = session.query(Measurement.date).order_by(Measurement.date).first()
# Let's find the latest date
latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# Let's find date 12 months before the latest day
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
# Closing session link
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Define what to do when a user hits the index route
@app.route("/")
def home():
    """List all available api routes."""
    return (
            f"*************************************************************"
            f"<h1> Welcome to &quot; Surf's UP &quot; Climate API! </h1>"
            f"*************************************************************"
            f"<h2>Available Routes:</h2>"
            f"****************************************"
            f"<br/>"
            f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
            f"<h2><em>Precipitation</em> for past twelve months:</h2>"
            f"<h3>/api/v1.0/precipitation</h3>"
            f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&<br/>"
            f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            f"<h2>List of <em>available stations</em>:</h2>"
            f"<h3>/api/v1.0/stations</h3>"
            f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%<br/>"
            f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
            f"<h2><em>Temperature</em> Observations from <em>most active</em> station:</h2>"
            f"<h3>/api/v1.0/tobs</h3>"
            f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&<br/>"
            f"<h2><em>Min, Max and Avg</em> Temperatures for given <em>start</em> day:</h2>"
            f"<h3><em>Any date between : 2010-01-01 and 2017-08-23</em></h3>"
            f"<h3>/api/v1.0/&#60; start &#62;</h3>"
            f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            f"<h2><em>Min, Max and Avg</em> Temperatures between <em>start</em> \
                and <em>end</em> day</h2>"
            f"<h3><em>Any date between : 2010-01-01 and 2017-08-23</em></h3>"
            f"<h3>/api/v1.0/&#60; start &#62;/&#60; end &#62;</h3>"
            f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%<br/>"
    )

# Define what to do when a user hits the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
# Create our session (link) from Python to the DB
    session = Session(engine)
    # Querying "date" and "precipitation" from Measurement table from past one year
    prcp_one_year = session.query(Measurement.date, Measurement.prcp).\
                                    filter(Measurement.date >= query_date).all()
    # Close session
    session.close()
    # Define the precipitation list
    prcp_list = []
    # Read the results in a list of dictionaries
    for date,prcp in prcp_one_year:
        dict = {} # Define an empty dictionary
        dict["Date"] = date # Fill in date
        dict["Precipitation"] = prcp # Fill in precipitation
        prcp_list.append(dict) # Append to the list

    return (jsonify(prcp_list)) # jsonify the list

# Define what to do when a user hits the stations route
@app.route("/api/v1.0/stations")
def stations():
# Create our session (link) from Python to the DB
    session = Session(engine)
    # Querying station_id and station_name from Station table 
    all_stations = session.query(Station.station, Station.name).all()
    # Close session
    session.close()
    # Define the stations list
    stations_list = []
    # Read the results in a list of dictionaries
    for station,name in all_stations:
        dict = {} # Define an empty dictionary
        dict["Station"] = station # Fill in station id
        dict["Name"] = name # Fill in station name
        stations_list.append(dict) # Append to the list

    return (jsonify(stations_list)) # jsonify the list

# Define what to do when a user hits the stations route
@app.route("/api/v1.0/tobs")
def temperature_obs():
# Create our session (link) from Python to the DB
    session = Session(engine)
    # Query to find the most active station
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).\
                          limit(1).first()
    # Querying "date" and "observed temperature" from Measurement table from past one year
    temp_one_year = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.date >= query_date).\
                        filter(Measurement.station == most_active_station[0])
    # Close session
    session.close()
    # Define the precipitation list
    obs_temp_list = []
    # Read the results in a list of dictionaries
    for date,temp in temp_one_year:
        dict = {} # Define an empty dictionary
        dict["Date"] = date # Fill in date
        dict["Temp"] = temp # Fill in temperature
        obs_temp_list.append(dict) # Append to the list

    return (jsonify(obs_temp_list)) # jsonify the list

# Define what to do when a user inputs a start date
@app.route("/api/v1.0/<start>")
def temperature_start(start,end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Convert the start string to datetime format
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    # Quering the max., min. and avg. temperatures beginning start_date
    results = session.query(func.max(Measurement.tobs),\
                            func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()
    # Close session
    session.close()
    # Define the temperature stats list
    temp_stat_list = []
     # Read the results in a list of dictionaries
    for max,min,avg in results:
        dict = {} # Define an empty dictionary
        dict["Start_Date"] = start_date.strftime("%A %d,%B %Y")
        dict["Max"] = max # Fill in max. temperature
        dict["Min"] = min # Fill in min. temperature
        dict["Avg"] = round(avg,2) # Fill in avg. temperature
        temp_stat_list.append(dict) # Append to the list  
    
    return jsonify(temp_stat_list)

# Define what to do when a user inputs a start & end date
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Convert the start string to datetime format
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')
    # Quering the max., min. and avg. temperatures beginning start_date
    results = session.query(func.max(Measurement.tobs),\
                            func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()
    # Close session
    session.close()
    # Define the temperature stats list
    temp_stat_list = []
     # Read the results in a list of dictionaries
    for max,min,avg in results:
        dict = {} # Define an empty dictionary
        dict["Start_Date"] = start_date.strftime("%A %d,%B %Y")
        dict["End_Date"] = end_date.strftime("%A %d,%B %Y")
        dict["Max"] = max # Fill in max. temperature
        dict["Min"] = min # Fill in min. temperature
        dict["Avg"] = round(avg,2) # Fill in avg. temperature
        temp_stat_list.append(dict) # Append to the list  
    
    return jsonify(temp_stat_list)

if __name__ == '__main__':
    app.run(debug=False)
