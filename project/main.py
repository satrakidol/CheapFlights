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
from . models import Airlines, Cities, Airports, Notification
from . database import db_session, init_db
from datetime import date
# import datetime
from datetime import datetime, timedelta
from celery import shared_task



main = Blueprint('main', __name__)

amadeus = Client(
    client_id = os.getenv('Amadeus_client_id'),
    client_secret= os.getenv('Amadeus_client_secret')
)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/get_flight_price', methods=['GET', 'POST'])
def get_flight_price():
    if request.method == 'GET':
        
        # origin=offer['origin'],
        # destination=offer['destination'],
        # departureDate=offer['departureDate'],
        # price=offer['price']['total']
        originLocationCode = request.args.get('origin')
        destination = request.args.get('destination')
        departure_date = request.args.get('departureDate')
        price = request.args.get('price')
        # return redirect(url_for('main.get_flight_price', originLocationCode = originLocationCode))
        # data = request.data
    
        print(f'Price:{price}')
        
        if not originLocationCode and not destination and not departure_date and not price:
            return render_template('search_flight.html')
        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=originLocationCode,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=1,
                # oneWay=True,
                # nonStop=True,
                # maxPrice=1000,
                max=10
            )
            flight_data = response.data  
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

            return render_template('show_results.html', flight_data=flight_data, airline=airline, airlines=airlines, departures=departures, departureAirport=departureAirport, ArrivalAirport=ArrivalAirport, arrivals=arrivals) 
            # flight_data_return=flight_data_return, airline=airline, airlines=airlines, airlinesReturn=airlinesReturn, departureAirport=departureAirport,departures=departures, departuresReturn=departuresReturn, ArrivalAirport=ArrivalAirport, arrivals=arrivals, ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn)  # Pass it to the template
        except ResponseError as error:
            print(f"Amadeus API Error: {error}")
            return render_template('show_results.html', error=f"Failed to fetch data: {str(error)}")
    # return render_template('show_results.html', flight_data=flight_data, flight_data_return=flight_data_return, airline=airline, airlines=airlines, airlinesReturn=airlinesReturn, departureAirport=departureAirport,departures=departures, departuresReturn=departuresReturn, ArrivalAirport=ArrivalAirport, arrivals=arrivals, ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn)  # Pass it to the template


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
        print(f'departure:{departure}')
        # print(f'departureCity:{departureCity}')
        print(f'Type of departure:{type(departure)}')
        print(f'destination:{destination}')
        print(f'Type of destination:{type(destination)}')
        # departure_code = str(departure_code)
        # print(f'departure_code:{departure_code}')
        # print(f'departure: {departure}')
        # print(f'departureCity: {departureCity}')

        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=departure,
                destinationLocationCode=destination,
                departureDate=begin_date,
                adults=1,
                max=10
            )
            # print(departureDate)
            response_return = amadeus.shopping.flight_offers_search.get(
                originLocationCode=destination,
                destinationLocationCode=departure,
                departureDate=return_date,
                adults=1,
                max=10
            )
            # print(response)
            flight_data = response.data  
            flight_data_return = response_return.data

            import pprint
            pprint.pprint(response)
            print(f'RESPONSE: {flight_data}')
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
            
            #Translate DEPARTURE
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


                
            #Translate ARRIVAL
            for offer in flight_data_return:
                #Company IATA
                carrier_code = offer['itineraries'][0]['segments'][0]['carrierCode']
                print(f"Carrier Code: {carrier_code}")           
                airline=db_session.query(Airlines).filter(Airlines.codes == carrier_code).first()
                print(f"Airline from Database: {airline}")
                airlinesReturn.append(airline)
                price =  offer['price']['total']
                print(f'price: {price}')
               
                
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

            # return render_template('show_results1.html', flight_data=flight_data, flight_data_return=flight_data_return, airline2 =airline2)
            return render_template('show_results.html', flight_data=flight_data, flight_data_return=flight_data_return, airline=airline, airlines=airlines, airlinesReturn=airlinesReturn, departureAirport=departureAirport,departures=departures, departuresReturn=departuresReturn, ArrivalAirport=ArrivalAirport, arrivals=arrivals, ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn)  # Pass it to the template
        except ResponseError as error:
            print(error)
            return render_template('show_results.html', error=f"Failed to fetch data: {str(error)}")

        return render_template('search_flight.html')

@main.route('/get_cheapest_dates', methods=['GET', 'POST'])
def get_cheapest_dates():
    if request.method == 'POST':  
        departure = request.form['departure']
        destination = request.form['destination']
        min_date = request.form['min_date']
        max_date = request.form['max_date']

        print(f'departure from form :{departure}')
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

        today = date.today()

        if not min_date:
            min_date = today
        
        if not max_date:
            max_date = today + timedelta(days=360)


        departureDate= f"{min_date},{max_date}"


        # departureDate="2023-09-25,2023-12-25",

        print(f'checkDestinationCode :{checkDestinationCode}')
        print(f'destination :{destination}')
        print(f'departureDate :{departureDate}')


        print(f'departure:{departure}')
        # print(f'departureCity:{departureCity}')
        print(f'Type of departure:{type(departure)}')
        print(f'destination:{destination}')
        print(f'Type of destination:{type(destination)}')
        

        try:
            response = amadeus.shopping.flight_dates.get(
                origin = departure,
                destination=destination,
                departureDate= departureDate,
                oneWay=True,
                nonStop=True,
                viewBy="DATE"
            )
              
            response_return = amadeus.shopping.flight_dates.get(
                origin=destination,
                destination=departure,
                departureDate= departureDate,
                oneWay=True,
                nonStop=True,
                viewBy="DATE"
            )

            # print(response)
            flight_data = response.data  
            flight_data_return = response_return.data

            # # Retrieve the access token from the client
            # access_token = amadeus.access_token

            # # Create the Authorization header with the access token
            # headers = {
            #     'Authorization': f'Bearer {access_token}'
            # }

            # # Make a request with the correct headers
            # authenticated_link = requests.get(flight_offer_url, headers=headers)

            # # Now 'response_with_headers' contains the response from the URL with the correct headers
            # print("Response with Headers:", authenticated_link.text)

            import pprint
            # pprint.pprint(response)
            print(f'RESPONSE: {response.data}')
            # print(f'RESPONSE: {response.json}')
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
            pricesGO=[]
            pricesReturn=[]
                        
            # #DEPARTURE
            for offer in flight_data:
                full_url = offer['links']['flightOffers']
                
                # print(f'flight_offer_url:  {flight_offer_url}')

            # headers = {
            #     "Authorization": "Bearer c9m4n5z4esn6t8mz2nkqh33se",
            #     "Accept": "application/json"
            # }
        
            # flight_offer = requests.get(full_url, headers=headers)


                
            #     #Company IATA
            #     carrier_code = offer['itineraries'][0]['segments'][0]['carrierCode']
            #     # print(f"Carrier Code: {carrier_code}")           
            #     airline=db_session.query(Airlines).filter(Airlines.codes == carrier_code).first()
            #     # print(f"Airline from Database: {airline}")
            #     airlines.append(airline)

            #     #Departure Airport IATA
                airportCodeDeparture = offer['origin']
                departureAirport = db_session.query(Airports).filter(Airports.codes == airportCodeDeparture).first()
                print(f"departures from Database: {departureAirport}")
                departures.append(departureAirport)

                #Arrival Airport IATA
                airportCodeArrival = offer['destination']
                ArrivalAirport = db_session.query(Airports).filter(Airports.codes == airportCodeArrival).first()
                # print(f"departures from Database: {departureAirport}")
                arrivals.append(ArrivalAirport)

            #CREATING NEW GO NOTIFICATION IN DB

                priceGo = float(offer['price']['total'])
                pricesGO.append(priceGo)
            priceGo=min(pricesGO)
            print(f'minpriceGo: {priceGo}')

                
            #ARRIVAL
            for offer in flight_data_return:
                #Company IATA
                # carrier_code = offer['itineraries'][0]['segments'][0]['carrierCode']
                # print(f"Carrier Code: {carrier_code}")           
                # airline=db_session.query(Airlines).filter(Airlines.codes == carrier_code).first()
                # print(f"Airline from Database: {airline}")
                # airlinesReturn.append(airline)
                # price =  offer['price']['total']
                # print(f'price: {price}')
               
                
                #Departure Airport IATA
                airportCode =  offer['origin']
                departureAirport = db_session.query(Airports).filter(Airports.codes == airportCode).first()
                # print(f"departures from Database: {departureAirport}")
                departuresReturn.append(departureAirport)

                #Arrival Airport IATA
                airportCodeArrivalReturn = offer['destination']
                ArrivalAirportReturn = db_session.query(Airports).filter(Airports.codes == airportCodeArrivalReturn).first()
                # print(f"departures from Database: {departureAirport}")
                arrivalsReturn.append(ArrivalAirportReturn)   

            #CREATING NEW RETURN NOTIFICATION IN DB

                priceReturn = float(offer['price']['total'])
                # print(f'priceReturn: {priceReturn}')
                pricesReturn.append(priceReturn)

            minpriceReturn = min(pricesReturn)
            print(f'priceReturnList: {pricesReturn}')
            print(f'minpriceReturn: {minpriceReturn}')
            # for i in pricesReturn:
            #     print(f'minpriceReturn: {i}')
            # print(f'minpriceReturn: {priceReturn}')
            notification = Notification(userID=current_user.id,origin=departure, destination = destination,
                                        minDate = min_date, maxDate = max_date,
                                        priceGo=priceGo, priceReturn=minpriceReturn)
            db_session.add(notification)
            db_session.commit()

            return render_template('show_results_cheapest_date.html',
                                    flight_data=flight_data,flight_data_return=flight_data_return,
                                    departureAirport=departureAirport,departures=departures,
                                    departuresReturn=departuresReturn, arrivals=arrivals, 
                                    ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn)
            # return render_template('show_results_cheapest_date.html', flight_data=flight_data, flight_data_return=flight_data_return, 
            # airline=airline, airlines=airlines, airlinesReturn=airlinesReturn, departureAirport=departureAirport,departures=departures, departuresReturn=departuresReturn, ArrivalAirport=ArrivalAirport, arrivals=arrivals, ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn, error=error)  # Pass it to the template
        except ResponseError as error:
            print(f"Amadeus API Error: {error}")
            return render_template('show_results_cheapest_date.html', error=f"Failed to fetch data: {str(error)}")

    return render_template('search_cheapest dates.html')

 
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

    
# @main.route('/redirectToOffer', methods=['GET', 'POST'])
# def redirectToOffer():
#     originLocationCode = request.args.get('origin')
#     destination = request.args.get('destination')
#     departure_date = request.args.get('departureDate')
#     price = request.args.get('price')
#     # return redirect(url_for('get_flight_price', originLocationCode = originLocationCode))

#     try:
#         response = amadeus.shopping.flight_offers_search.get(
#             # originLocationCode=MARIA,
#             originLocationCode=departure,
#             # originLocationCode=departure_code,
#             destinationLocationCode=destination,
#             departureDate=begin_date,
#             adults=1,
#             max=10
#     )
    # # print(departureDate)
    # response_return = amadeus.shopping.flight_offers_search.get(
    #     originLocationCode=destination,
    #     destinationLocationCode=departure,
    #     departureDate=return_date,
    #     adults=1,
    #     max=10
    # )
    #     return render_template('show_results.html', flight_data=flight_data, flight_data_return=flight_data_return, airline=airline, airlines=airlines, airlinesReturn=airlinesReturn, departureAirport=departureAirport,departures=departures, departuresReturn=departuresReturn, ArrivalAirport=ArrivalAirport, arrivals=arrivals, ArrivalAirportReturn=ArrivalAirportReturn, arrivalsReturn=arrivalsReturn)  # Pass it to the template
    # except ResponseError as error:
    #     print(error)
    #     return render_template('show_results.html', error=f"Failed to fetch data: {str(error)}")

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


@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    return a + b

@main.post("/add")
def start_add() -> dict[str, object]:
    a = request.form.get("a", type=int)
    b = request.form.get("b", type=int)
    result = add_together.delay(a, b)
    return {"result_id": result.id}