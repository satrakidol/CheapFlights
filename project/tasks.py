from project.make_celery import celery_app as celery
from flask_mail import Mail, Message
from . models import Notification, Cities, User
from . database import db_session
from . main import datetime,date
from amadeus import Client, ResponseError
from . config import Amadeus_client_id, Amadeus_client_secret, SECRET_KEY
from . main import amadeus, clean_string


@celery.task()
def print_hello():
    print("Hello from task")


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
        print(f"notifications: {notifications}")
    

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

            pricesGoList =[]

            for offer in flight_data:
                new_priceGo = float(offer['price']['total'])
                pricesGoList.append(new_priceGo)
                
            new_priceGo=min(pricesGoList)
            print(f"new_price is: {new_priceGo}")

            if new_priceGo < priceGo or new_priceGo == priceGo or new_priceGo > priceGo:
                #delete afterwards the 2 ors above
                notification_to_update = db_session.query(Notification).filter_by(notificationID=notificationID).first()
                notification_to_update.priceGo = new_priceGo
                # Commit the changes to the database
                db_session.commit()


                userIDTranslated = (
                        db_session.query(User.name).filter(User.id == Notification.userID)).first()
                userIDTranslated = clean_string(userIDTranslated)


                userEmail = (
                        db_session.query(User.email).filter(User.id == Notification.userID)).first()[0]

                print(f"userIDTranslated: {userIDTranslated}")
                print(f"userEmail: {userEmail}")



                originTranslated = db_session.query(Cities.city).filter(Cities.codes == origin).all()
                originTranslated = clean_string(originTranslated)
                destinationTranslated = db_session.query(Cities.city).filter(Cities.codes == destination).all()
                destinationTranslated = clean_string(destinationTranslated)
                
                message = Message(
                subject = "New cheaper flight for your destination",
                recipients = [userEmail],
                sender='CheapFlights',
            )
                message.body = f'Hello {userIDTranslated},\n\nThe new price for your trip from {originTranslated} to {destinationTranslated} is {new_priceGo} '
                mail.send(message)
            else:
                print("old priceGo is higher")
            #prices are coming sorted, so we need only 1 iteration
            # break

            pricesReturnList = []

            for offer in flight_data_return:
                new_priceReturn = float(offer['price']['total'])
                pricesReturnList.append(new_priceReturn)

            new_priceReturn=min(pricesReturnList)

            if new_priceReturn < priceReturn or new_priceReturn == priceReturn or new_priceReturn > priceReturn:
                #delete afterwards the 2 ors above
                notification_to_update = db_session.query(Notification).filter_by(notificationID=notificationID).first()
                notification_to_update.priceReturn = new_priceReturn
                # Commit the changes to the database
                db_session.commit()

                userIDTranslated = (
                        db_session.query(User.name).filter(User.id == Notification.userID)).first()
                userIDTranslated = clean_string(userIDTranslated)


                userEmail = (
                        db_session.query(User.email).filter(User.id == Notification.userID)).first()[0]

                message = Message(
                subject = "New cheaper flight for your destination",
                recipients = [userEmail],
                sender='CheapFlights',
            )
                message.body = f'Hello {userIDTranslated},\n\nThe new price for your trip from {originTranslated} to {destinationTranslated} is {new_priceGo} '
                mail.send(message)
            else:
                print("old priceReturn is higher")
            # break

        except ResponseError as error:
            pass 
