import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from sqlalchemy import create_engine, func , inspect


from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#List all routes that are available
@app.route('/')
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )
#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary


query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)


    results_prec = session.query(Measurements.date, Measurements.prcp).\
    filter(Measurements.date >= query_date ).\
    order_by(Measurements.date).all()

    return jsonify(results_prec)
   


# Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    list_of_statons = session.query(Measurements.station, Stations.name, func.count(Measurements.station)).\
filter(Measurements.station == Stations.station).\
order_by(func.count(Measurements.station).desc()).\
group_by(Measurements.station).all()

    return jsonify(list_of_statons)

# Query the dates and temperature observations of the most active station for the last year of data.

# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    sel = [func.min(Measurements.tobs),
          func.max(Measurements.tobs),
          func.avg(Measurements.tobs)]

    most_active_station = session.query(*sel).\
        group_by(Measurements.station).\
        order_by(func.count(Measurements.id).desc()).first()

    result_temps = session.query(Measurements.date, Measurements.tobs).\
    filter(Measurements.station == 'USC00519281').\
    filter(Measurements.date >= query_date).all()

    return jsonify(result_temps)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.


@app.route("/api/v1.0/<start>")

def start(start):

    session = Session(engine)

    
    sel = [func.min(Measurements.tobs),
      func.max(Measurements.tobs),
      func.avg(Measurements.tobs)]


    results_start = session.query(*sel).filter(Measurements.date >= query_date).all()


    start_date_list=[]

    for min,avg,max in results_start:
        start_date_dict = {}
        start_date_dict["TMIN"] = min

        start_date_dict["TMAX"] = max
        start_date_dict["TAVG"] = avg
        start_date_list.append(start_date_dict)

        return jsonify(start_date_list)

    


# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
        
@app.route("/api/v1.0/<start>/<end>")

def start_end():

    session = Session(engine)

    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    results_start_end = sel = [func.min(Measurements.tobs),
      func.max(Measurements.tobs),
      func.avg(Measurements.tobs)]


    most_active_station = session.query(*sel).\
    group_by(Measurements.station).\
    filter(Measurements.date >=query_date).\
    filter(Measurements.date <= query_date).\
    order_by(func.count(Measurements.id).desc()).all()


    return jsonify(results_start_end)


if __name__ == '__main__':
    app.run(debug=True)



