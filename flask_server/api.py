# -*- coding: utf-8 -*-

import os
import sys
import json
import check_thread
from database import dao
from flask_api import status
from ConfigParser import SafeConfigParser
from logbook import Logger, StreamHandler
from flask import Flask, request, Response
from datetime import datetime, date, timedelta


config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config_server.cfg'))
reading_routes_folder = config.get("server", "reading_routes_folder")
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/travel_request', methods=['POST'])
def travel_request():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        departure = data['departure']
        lat_departure = data['lat_departure']
        lon_departure = data['lon_departure']
        arrival = data['arrival']
        lat_arrival = data['lat_arrival']
        lon_arrival = data['lon_arrival']
        time_departure = str(datetime.today())  # Not used, but inserted for future developments
        time_arrival = data['time_arrival']
        user = data['user']

        id_request = dao.insert_request(
            departure=departure,
            lat_departure=lat_departure,
            lon_departure=lon_departure,
            arrival=arrival,
            lat_arrival=lat_arrival,
            lon_arrival=lon_arrival,
            time_departure=time_departure,
            time_arrival=time_arrival,
            request_user=user
        )

        result = {"result": id_request}
        status_code = status.HTTP_200_OK

    else:

        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/optimized', methods=['POST'])
def optimized_route():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json
        license_plate = data['license_plate']

        id_bus = dao.get_bus_id(license_plate)
        if id_bus != None:
            yesterday = str(date.today() - timedelta(days=1))
            with open('../{0}/{1}.json'.format(reading_routes_folder, yesterday), 'r') as optimized_routes:
                data = json.load(optimized_routes)
                route = data[str(id_bus)]

            result = {"result": route}
            status_code = status.HTTP_200_OK
        else:
            result = {"result": "License plate inserted not exists"}
            status_code = status.HTTP_204_NO_CONTENT
    else:

        result = {"result": "wrong content type"}
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    return Response(
        json.dumps(result),
        status=status_code,
        mimetype="application/json"
    )


@app.route('/estimated_departure', methods=['POST'])
def estimated_departure():
    pass


@app.route('/send_coordinates', methods=['POST'])
def send_coordinates():
    pass


if __name__ == "__main__":

    """
    The main entry point of the application
    """

    StreamHandler(sys.stdout).push_application()
    log = Logger('Main - Urban Transport System')

    log.notice("Flask server started.")
    check_thread.main()
    log.notice("Control Thread started.")

    app.run(host="0.0.0.0", port=5000, debug=False)
