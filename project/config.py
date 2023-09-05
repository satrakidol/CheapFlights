from dotenv import load_dotenv
import os


APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
print(dotenv_path)
load_dotenv(dotenv_path)

connection_string = os.getenv("DBURL")
print(f"connection_string = {connection_string}")

Amadeus_client_secret = os.getenv("Amadeus_client_secret")
Amadeus_client_id = os.getenv("Amadeus_client_id")
SECRET_KEY = os.getenv("SECRET_KEY")