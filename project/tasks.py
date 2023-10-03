from project.make_celery import celery_app as celery
from flask_mail import Mail, Message
from . models import Notification
from . database import db_session
from . main import datetime,date
from amadeus import Client, ResponseError
from . config import Amadeus_client_id, Amadeus_client_secret, SECRET_KEY
from . main import amadeus

@celery.task()
def print_hello():
    print("Hello from task")



maria = 'kor'

@celery.task()
def email():

    mail = Mail() 
    notifications = db_session.query(Notification).all()

    # Iterate through the notifications
    for notification in notifications:
        notificationID = notification.notificationID
        userID = notification.userID
        origin = notification.origin
        destination = notification.destination
        min_date = notification.minDate
        max_date = notification.maxDate
        priceGo = notification.priceGo
        priceReturn = notification.priceReturn

        print(f"notificationID: {notificationID}")
        print(f"userID: {userID}")
        print(f"origin: {origin}")
        print(f"destination: {destination}")
        print(f"min_date: {min_date}")
        print(f"max_date: {max_date}")
        print(f"priceGo: {priceGo}")
        print(f"priceReturn: {priceReturn}")

        #in case min_date had passed today's date, set today as min_date to search

        # Parse min_date into a date object
        min_date_obj = datetime.strptime(min_date, "%Y-%m-%d").date()

        today = date.today()

        if min_date_obj < today:
            min_date = today

        #in case max_date had passed today's date, set to search 360 days in the future

        # Parse min_date into a date object
        max_date_obj = datetime.strptime(max_date, "%Y-%m-%d").date()
        
        if max_date_obj < today:
            max_date = today + timedelta(days=360)

        departureDate= f"{min_date},{max_date}"

        print(f"departureDate: {departureDate}")

        try:
            response = amadeus.shopping.flight_dates.get(
                origin = origin,
                destination=destination,
                departureDate= departureDate,
                oneWay=True,
                nonStop=True,
                viewBy="DATE"
            )
            
            response_return = amadeus.shopping.flight_dates.get(
                origin=destination,
                destination=origin,
                departureDate= departureDate,
                oneWay=True,
                nonStop=True,
                viewBy="DATE"
            )

            # print(response)
            flight_data = response.data  
            flight_data_return = response_return.data

            for offer in flight_data:
                new_priceGo = float(offer['price']['total'])
                print(f"new_price is: {new_priceGo}")
                if new_priceGo < priceGo:
                    notification_to_update = db_session.query(Notification).filter_by(notificationID=notificationID).first()
                    notification_to_update.priceGo = new_price
                    # Commit the changes to the database
                    db_session.commit()
                    #SENT EMAIL
                else:
                    print("old priceGo is higher")
                #prices are comming sorted, so we need only 1 iteration
                break



            for offer in flight_data_return:
                new_priceReturn = float(offer['price']['total'])
                if new_priceReturn < priceReturn:
                    notification_to_update = db_session.query(Notification).filter_by(notificationID=notificationID).first()
                    notification_to_update.priceReturn = new_price
                    # Commit the changes to the database
                    db_session.commit()
                    #SENT EMAIL
                else:
                    print("old priceReturn is higher")
                break



            print(f"flight_data: {flight_data}")
            print(f"flight_data_return: {flight_data_return}")




            message = Message(
                subject = "New cheaper flight for your destination",
                recipients = ['ap22017@hua.gr'],
                sender='CheapFlights',
            )
            message.body = f'The new price is {new_priceGo}'
            mail.send(message)

        except ResponseError as error:
            return 
        #     print(f"Amadeus API Error: {error}")
        # return render_template('show_results_cheapest_date.html', error=f"Failed to fetch data: {str(error)}", new_price=new_price)
            

    # return "sent"