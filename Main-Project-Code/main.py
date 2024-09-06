from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import xgboost as xgb
import time
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase import firebase
from sklearn.metrics import accuracy_score, confusion_matrix

firebase_1 = firebase.FirebaseApplication(
    'https://login-and-signu-default-rtdb.firebaseio.com/', None)


def sms(num, amount, date):
  result = firebase_1.get('/users', None)

  # Sort the data based on 'index' field
  sorted_result = sorted(result.items(), key=lambda x: x[1]['index'])

  # Get the last added data
  last_data = sorted_result[-1][1]

  account_sid = 'ACed72ecfedefbe154311ac8c4dffd551d'
  auth_token = 'd988b05d69e79545e3a8cc27eb412c40'
  client = Client(account_sid, auth_token)
  twilio_phone_number = '+12293608117'
  a = '+91'
  b = last_data['Phone']
  recipient_phone_number = a + b
  message = client.messages.create(
      body=
      "We have detected fraud in your credit card transaction.\n Transaction number: "
      + str(num) + "\n Amount: " + str(amount) + "\n Date and Time: " +
      str(date),
      from_=twilio_phone_number,
      to=recipient_phone_number)
  print("Message SID:", message.sid)


def email(num, amount, date):
  result = firebase_1.get('/users', None)

  # Sort the data based on 'index' field
  sorted_result = sorted(result.items(), key=lambda x: x[1]['index'])

  # Get the last added data
  last_data = sorted_result[-1][1]
  sender_email = "armymoaengene@gmail.com"
  receiver_email = last_data['email']
  password = "xnmf wltu olzx ueuo"

  # Create a message
  subject = "Fraud Detected"
  message = "We have detected fraud in your credit card transaction.\n Transaction number: " + str(
      num) + "\n Amount: " + str(amount) + "\n Date and Time: " + str(date)
  msg = MIMEMultipart()
  msg['From'] = sender_email
  msg['To'] = receiver_email
  msg['Subject'] = subject
  msg.attach(MIMEText(message, 'plain'))
  try:
    server = smtplib.SMTP("smtp.gmail.com",
                          587)  # SMTP server and port for Gmail
    server.starttls()
    server.login(sender_email, password)

    # Send the email
    server.sendmail(sender_email, receiver_email, msg.as_string())

    # Quit the SMTP server
    server.quit()
    print("Email sent successfully")

  except Exception as e:
    print(f"Error sending email: {str(e)}")


processed_transactions = set()


def initialize_firebase():
  cred = credentials.Certificate(
      "credit-card-702af-firebase-adminsdk-a6zts-c3571dc809.json")
  firebase_admin.initialize_app(cred, {
      'databaseURL':
      'https://credit-card-702af-default-rtdb.firebaseio.com/'
  })


def load_historical_data():
  ref = db.reference('/credit_card_transactions')
  historical_data = ref.get()
  historical_transactions = np.array(
      [transaction['amt'] for transaction in historical_data.values()])
  labels = np.array(
      [transaction['is_fraud'] for transaction in historical_data.values()])
  return historical_transactions, labels


def train_xgboost(historical_data, labels):
  model = xgb.XGBClassifier()
  model.fit(historical_data.reshape(-1, 1), labels)
  return model


def calculate_outlier_status(model, real_time_data):
  real_time_transactions = np.array(
      [transaction['amt'] for transaction in real_time_data.values()])
  ref12 = db.reference('/outliers')
  ref11 = db.reference('/not_outliers')
  ref13 = db.reference('/messages')
  for i, transaction in enumerate(real_time_data.values()):
    if transaction['trans_num'] not in processed_transactions:
      print("Transaction Details:")
      print("Amount:", transaction['amt'])
      is_outlier = model.predict(real_time_transactions[i].reshape(1, -1))
      print("XGBoost - Outlier Status:",
            "Outlier" if is_outlier == 1 else "Not an outlier")
      if is_outlier == 1:
        ref12.push(transaction)
        body1 = "We have detected fraud in your credit card transaction.\n Transaction number: " + str(
            transaction['trans_num']) + "\n Amount: " + str(
                transaction['amt']) + "\n Date and Time: " + str(
                    transaction['trans_date_trans_time'])
        ref13.push({'message': body1})
        email(transaction['trans_num'], transaction['amt'],
              transaction['trans_date_trans_time'])
        sms(transaction['trans_num'], transaction['amt'],
            transaction['trans_date_trans_time'])
      else:
        ref11.push(transaction)
      processed_transactions.add(transaction['trans_num'])
      print("")
      


def process_real_time_data(model, labels):
  ref = db.reference('/credit_card_transactions_other')
  while True:
    real_time_data = ref.get()
    if real_time_data:
      calculate_outlier_status(model, real_time_data)
    time.sleep(3)  # Adjust the sleep duration as needed


def main():
  initialize_firebase()
  historical_data, labels = load_historical_data()
  xgboost_model = train_xgboost(historical_data, labels)

  process_real_time_data(xgboost_model, labels)


if __name__ == "__main__":
  main()
