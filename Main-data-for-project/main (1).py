import pandas as pd
import random
from faker import Faker
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase for the first database
cred = credentials.Certificate(
    "credit-card-702af-firebase-adminsdk-a6zts-c3571dc809.json")
firebase_admin.initialize_app(
    cred,
    {'databaseURL': 'https://credit-card-702af-default-rtdb.firebaseio.com/'})

# Firebase references to your data in the two databases
ref1 = db.reference('/credit_card_transactions')
ref2 = db.reference('/credit_card_transactions_other'
                    )  # Change this to your second database path

# Create a Faker object to generate synthetic data
fake = Faker()

# Define the number of legitimate and fraud records
n_records = 1000
fraud_percentage = 5  # Adjust as needed (5% fraud transactions)

# Generate synthetic data with timestamps and add to Firebase in real-time
for i in range(n_records):
  # Add a time delay to simulate real-time data
  time.sleep(random.uniform(
      1, 10))  # Adjust the sleep interval for a more realistic time interval

  if i < 20:
    ref = ref1  # Send the first 20 records to the first database
    # For the first 20 records, split them evenly between legitimate and fraud
    if i % 2 == 0:
      is_fraud = 1  # Set as 1 for fraud transactions
    else:
      is_fraud = 0  # Set as 0 for legitimate transactions
  else:
    ref = ref2  # Send the rest of the records to the second database
    is_fraud = 1 if random.randint(1, 100) <= fraud_percentage else 0

  if is_fraud == 0:
    # Simulate a legitimate transaction
    transaction_data = {
        'index':
        i,
        'trans_date_trans_time':
        fake.date_time_between(start_date='-30d',
                               end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
        'cc_num':
        fake.credit_card_number(card_type='mastercard'),
        'merchant':
        fake.company(),
        'category':
        fake.job(),
        'amt':
        round(random.uniform(20, 500), 2),
        'first':
        fake.first_name(),
        'last':
        fake.last_name(),
        'gender':
        fake.random_element(elements=('M', 'F')),
        'street':
        fake.street_address(),
        'city':
        fake.city(),
        'state':
        fake.state(),
        'zip':
        fake.zipcode(),
        'lat':
        round(random.uniform(30, 40), 6),
        'long':
        round(random.uniform(-100, -90), 6),
        'city_pop':
        random.randint(1000, 1000000),
        'job':
        fake.job(),
        'dob':
        fake.date_of_birth(minimum_age=18,
                           maximum_age=70).strftime('%Y-%m-%d'),
        'trans_num':
        fake.uuid4(),
        'unix_time':
        int(time.mktime(fake.date_time().timetuple())),
        'merch_lat':
        round(random.uniform(30, 40), 6),
        'merch_long':
        round(random.uniform(-100, -90), 6),
        'is_fraud':
        0
    }
  else:
    # Simulate a fraud transaction
    transaction_data = {
        'index':
        i,
        'trans_date_trans_time':
        fake.date_time_between(start_date='-30d',
                               end_date='now').strftime('%Y-%m-%d %H:%M:%S'),
        'cc_num':
        fake.credit_card_number(card_type='mastercard'),
        'merchant':
        fake.company(),
        'category':
        fake.job(),
        'amt':
        round(random.uniform(400, 5000), 2),
        'first':
        fake.first_name(),
        'last':
        fake.last_name(),
        'gender':
        fake.random_element(elements=('M', 'F')),
        'street':
        fake.street_address(),
        'city':
        fake.city(),
        'state':
        fake.state(),
        'zip':
        fake.zipcode(),
        'lat':
        round(random.uniform(35, 45), 6),
        'long':
        round(random.uniform(-95, -85), 6),
        'city_pop':
        random.randint(1000, 1000000),
        'job':
        fake.job(),
        'dob':
        fake.date_of_birth(minimum_age=18,
                           maximum_age=70).strftime('%Y-%m-%d'),
        'trans_num':
        fake.uuid4(),
        'unix_time':
        int(time.mktime(fake.date_time().timetuple())),
        'merch_lat':
        round(random.uniform(35, 45), 6),
        'merch_long':
        round(random.uniform(-95, -85), 6),
        'is_fraud':
        1
    }

  # Push the data to Firebase in real-time
  ref.push(transaction_data)
  print(transaction_data)

  print(
      f"Transaction added to Firebase at time: {transaction_data['trans_date_trans_time']}"
  )

print("Data generation complete.")
