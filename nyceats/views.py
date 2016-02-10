from flask import render_template
from nyceats import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request
import googlemaps
import json
from math import sin, cos, sqrt, atan2, radians

with open('nyceats/conf/gmaps_settings.json', 'r') as f:
    data = json.load(f)

gkey=data ['gmaps']['gkey']
gmaps = googlemaps.Client(key=gkey)

user = 'klapina'           
host = 'localhost'
dbname = 'restr_db_all'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)


@app.route('/input')
@app.route('/')
@app.route('/index')
def input():
    return render_template("input.html" )

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/slides')
def slides():
    return render_template("slides.html")

@app.route('/output')
def nyc_output():
    R = 6373.0

    addr = request.args.get('addr')
    geocode_result = gmaps.geocode(address=addr, components={'locality': 'New York', 'country': 'US'})
    inlat = geocode_result[0]['geometry']['location']['lat']
    inlon = geocode_result[0]['geometry']['location']['lng']
    inlat = radians(inlat)
    inlon = radians(inlon)
    #just select restaurants from the  dtabase 
    query = "SELECT name, address,zip,lat,lon,type FROM restr_table"
    query_results=pd.read_sql_query(query,con)

    dist=[]
    col=[]
    for index in range(0,query_results.shape[0]):
        lat1 = radians(query_results.iloc[index]['lat'])
        lon1 = radians(query_results.iloc[index]['lon'])
        dlon = lon1 - inlon
        dlat = lat1 - inlat
        a = sin(dlat / 2)**2 + cos(inlat) * cos(lat1) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 1000 *R * c
        dist.append(distance) # m
        mycolor="FFFF00"
        if query_results.iloc[index]['type']>1:
            mycolor="1D7BfD"
        if query_results.iloc[index]['type']==1: 
            mycolor="FD1D7B"

        col.append(mycolor) # m

    query_results['dist']=dist
    query_results['color']=col

    all_names=query_results.sort_values(by='dist')

    return render_template("output.html",  all_names=all_names)


        
############################################################################


  
