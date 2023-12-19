# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Last twelve months of precipitation data from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"All stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"List of temperature observations from the most active station<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"List of Minimum Temperature, Average Temperature, and Maximum Temperature for a specified start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"List of Minimum Temperature, Average Temperature, and Maximum Temperature for specified start & end dates<br/>"
    )
##########
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
                      filter(Measurement.date > year_ago).all()
    
    dates_precip = []
    for date, precipitation in results:
        data_dict = {}
        data_dict["date"] = date
        data_dict["prcp"] = precipitation
        dates_precip.append(data_dict)

    return jsonify(dates_precip)
#######
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    
#######
    return jsonify(stations_query)

#######

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    active_station_count = session.query(Measurement.station,func.count(Measurement.station)).\
                                    group_by(Measurement.station).\
                                    order_by(func.count(Measurement.station).desc()).first()
    active_station = active_station_count[0]
    active_temp_obs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                             filter(Measurement.station == active_station).all()
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
                             filter(Measurement.station == active_station).\
                             filter(Measurement.date > year_ago).order_by(Measurement.date).all()
    
    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)    

######

@app.route("/api/v1.0/<start>")
def temps(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date - last_year
    end =  dt.date(2017, 8, 23)
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                              filter(Measurement.date >=start).filter(Measurement.date <= end).all()
    temperatures = list(np.ravel(temp_data))
    return jsonify(temperatures)

#######

@app.route("/api/v1.0/<start>/<end>")
def temps(start,end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)   
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    start = start_date - last_year
    end = end_date - last_year
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                              filter(Measurement.date >=start).filter(Measurement.date <= end).all()
    temperatures = list(np.ravel(temp_data))
    return jsonify(temperatures)    


#######
if __name__ == "__main__":
    app.run(debug=True)