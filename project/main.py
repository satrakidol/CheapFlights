from flask import Blueprint, render_template, Flask, request
from flask_login import login_required, current_user
from . import db
from flask import Flask, render_template, redirect, request, flash, url_for,jsonify
# from models import User, LoginForm
# from config import SECRET_KEY
# from flask_bcrypt import Bcrypt
from werkzeug.security import check_password_hash
from flask import session
import requests
from amadeus import Client, ResponseError
import os
import re
from datetime import datetime
import flask_login
from flask_login import LoginManager
from . config import Amadeus_client_id, Amadeus_client_secret, SECRET_KEY
from . models import Airlines, Cities, Airports
from . database import db_session, init_db



# from database import db_session, init_db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/get_flight_price', methods=['GET', 'POST'])
def get_flight_price():
    if request.method == 'POST':  
        departure = request.form['departure']
        destination = request.form['destination']
        begin_date = request.form['begin_date']
        return_date = request.form['return_date']

        print(f'destination from form :{destination}')

        checkDepartureCode = db_session.query(Cities).filter(Cities.codes == departure).first()
        

        if not checkDepartureCode:
            departure = db_session.query(Cities.codes).filter(Cities.city == departure).all()
            departure = str(departure)
            departure=departure.replace("(", "").replace(")", "").replace("," , "").replace("[" , "").replace("]" , "").replace("'" , "")

        checkDestinationCode = db_session.query(Cities).filter(Cities.codes == destination).first()

        if not checkDestinationCode:
            destination = db_session.query(Cities.codes).filter(Cities.city == destination).all()
            destination = str(destination)
            destination=destination.replace("(", "").replace(")", "").replace("," , "").replace("[" , "").replace("]" , "").replace("'" , "")

        print(f'checkDestinationCode :{checkDestinationCode}')
        print(f'destination :{destination}')
        # departureCity = db_session.query(Cities.codes).filter(Cities.city == departure).all()# departureCity = db_session.query(Cities.codes).filter(Cities.city == departure).all()
        # departureCity = db_session.query(Cities).filter(Cities.city == departure).first()

        # print(f'departureCity after query:{departureCity}')


        # MARIA= (MARIA, 1, 0)

        print(f'departure:{departure}')
        # print(f'departureCity:{departureCity}')
        # print(f'MARIA:{MARIA}')
        # print(f'Type of MARIA:{type(MARIA)}')
        print(f'Type of departure:{type(departure)}')
        print(f'destination:{destination}')
        print(f'Type of destination:{type(destination)}')

        # if departureCity:
        #     departure_code = departureCity.codes
        # else:
        #     # Handle the case where the destination name is not found in the database
        #     departure_code = None

        # departure_code = str(departure_code)

        # print(f'departure_code:{departure_code}')
        
        # if departureCity[0] is not None:
        #     result = departureCity.split(',')[0]
        #     print(f'result:result')
        # else:
        #     print("The value is None")
        # MARIA = departureCity.split(',')[0]
        # print(f'departure: {departure}')
        # print(f'departureCity: {departureCity}')
        # print(f'MARIA: {MARIA}')

        

        amadeus = Client(
            client_id = os.getenv('Amadeus_client_id'),
            client_secret= os.getenv('Amadeus_client_secret')
        )

        try:
            response = amadeus.shopping.flight_offers_search.get(
                # originLocationCode=MARIA,
                originLocationCode=departure,
                # originLocationCode=departure_code,
                destinationLocationCode=destination,
                departureDate=begin_date,
                adults=1
            )
            response_return = amadeus.shopping.flight_offers_search.get(
                originLocationCode=destination,
                destinationLocationCode=departure,
                departureDate=return_date,
                adults=1
            )
            # print(response)
            flight_data = response.data  
            flight_data_return = response_return.data

            import pprint
            pprint.pprint(response)
            # {{ offer['price']['total'] }} {{ offer['price']['currency'] }}


            ####APO EDO####
            # carrier_code2 = flight_data['itineraries'][0]['segments'][0]['carrierCode']
            # airline2=db_session.query(Airlines).filter(Airlines.codes == carrier_code2).first()
            # print(f"Carrier Code: {carrier_code2}")
            # print(f"Airline from Database: {airline2}")
            #### OS EDO####
            airlines = []
            airlinesReturn = []
            departures = []
            departuresReturn = []
            arrivals=[]
            arrivalsReturn=[]
            
            #DEPARTURE
            for offer in flight_data:
                #Company IATA
                carrier_code = offer['itineraries'][0]['segments'][0]['carrierCode']
                # print(f"Carrier Code: {carrier_code}")           
                airline=db_session.query(Airlines).filter(Airlines.codes == carrier_code).first()
                # print(f"Airline from Database: {airline}")
                airlines.append(airline)

                #Departure Airport IATA
                airportCodeDeparture = offer['itineraries'][0]['segments'][0]['departure']['iataCode']
                departureAirport = db_session.query(Airports).filter(Airports.codes == airportCodeDeparture).first()
                # print(f"departures from Database: {departureAirport}")
                departures.append(departureAirport)

                #Arrival Airport IATA
                airportCodeArrival = offer['itineraries'][0]['segments'][-1]['arrival']['iataCode']
                ArrivalAirport = db_session.query(Airports).filter(Airports.codes == airportCodeArrival).first()
                # print(f"departures from Database: {departureAirport}")
                arrivals.append(ArrivalAirport)


                
            #ARRIVAL
            for offer in flight_data_return:
                #Company IATA
                carrier_code = offer['itineraries'][0]['segments'][0]['carrierCode']
                print(f"Carrier Code: {carrier_code}")           
                airline=db_session.query(Airlines).filter(Airlines.codes == carrier_code).first()
                print(f"Airline from Database: {airline}")
                airlinesReturn.append(airline)
                
                #Departure Airport IATA
                airportCode = offer['itineraries'][0]['segments'][0]['departure']['iataCode']
                departureAirport = db_session.query(Airports).filter(Airports.codes == airportCode).first()
                # print(f"departures from Database: {departureAirport}")
                departuresReturn.append(departureAirport)

                #Arrival Airport IATA
                airportCodeArrivalReturn = offer['itineraries'][0]['segments'][-1]['arrival']['iataCode']
                ArrivalAirportReturn = db_session.query(Airports).filter(Airports.codes == airportCodeArrivalReturn).first()
                # print(f"departures from Database: {departureAirport}")
                arrivalsReturn.append(ArrivalAirportReturn)

                

            # if airline:
            #     airline_name = airline
            # else:
            #     airline_name = "Airline not found"
            
            # print(f"Airline : {airline}") 

#KAI THN GRAMMH APO KATO
            # return render_template('show_results1.html', flight_data=flight_data, flight_data_return=flight_data_return, airline2 =airline2)
            return render_template('show_results.html', flight_data=flight_data, flight_data_return=flight_data_return, airline=airline, airlines=airlines, airlinesReturn=airlinesReturn, departureAirport=departureAirport,departures=departures, departuresReturn=departuresReturn, ArrivalAirport=ArrivalAirport, arrivals=arrivals, ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn)  # Pass it to the template
        except ResponseError as error:
            print(error)
            return render_template('show_results.html', error="Failed to fetch data.")

    return render_template('search_flight.html')

 
@main.app_template_filter('duration_formatter')
def duration_formatter(duration):
    duration_parts = re.findall(r'(\d+)([A-Z])', duration)
    formatted_duration = []

    for amount, unit in duration_parts:
        if unit == 'H':
            formatted_duration.append(f"{amount} hours")
        elif unit == 'M':
            formatted_duration.append(f"{amount} minutes")

    return ' '.join(formatted_duration)

@main.app_template_filter('format_datetime')
def format_datetime(iso_datetime):
    parsed_datetime = datetime.strptime(iso_datetime, '%Y-%m-%dT%H:%M:%S')
    formatted_datetime = parsed_datetime.strftime('%B %d, %Y %I:%M %p')
    return formatted_datetime


@main.route('/total', methods=['GET', 'POST'])
def total():
    if request.method == 'GET':
        carrierCodeGo = request.args.get('carrierCodeGo')
        index = request.args.get('index')
        priceGo = request.args.get('priceGo')
        priceGo = float(priceGo)

        carrierCodeReturn = request.args.get('carrierCodeReturn')
        indexReturn= request.args.get('indexReturn')
        priceReturn = request.args.get('priceReturn')
        priceReturn = float(priceReturn)
        totalPrice = priceGo + priceReturn
        

        return render_template('confirmation.html', carrierCodeGo=carrierCodeGo, index=index, priceGo=priceGo, priceReturn=priceReturn, indexReturn=indexReturn, totalPrice=totalPrice, carrierCodeReturn=carrierCodeReturn)
    else:
        return render_template('base.html')

    



# @main.route('/select_flight', methods=['POST', 'GET'])
# def select_flight():
#     if request.method == 'POST':
#         selected_outgoing_index = int(request.form.get('selected_offer_outgoing', -1))
#         selected_return_index = int(request.form.get('selected_offer_return', -1))

#         selected_outgoing_flight = None
#         selected_return_flight = None

#         if selected_outgoing_index != -1 and selected_outgoing_index < len(flight_data):
#             selected_outgoing_flight = flight_data[selected_outgoing_index]

#         if selected_return_index != -1 and selected_return_index < len(flight_data_return):
#             selected_return_flight = flight_data_return[selected_return_index]

#         # You can now use the selected_outgoing_flight and selected_return_flight variables
#         # to access the details of the selected flights and perform further processing.

#         return render_template('confirmation.html', 
#             selected_outgoing_flight=selected_outgoing_flight, 
#             selected_return_flight=selected_return_flight)

    