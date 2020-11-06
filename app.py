from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv
load_dotenv()


BASE_URI = os.getenv("BASE_URI")
PAYMENT_METHODS_EP = os.getenv("PAYMENT_METHODS_EP")
PAYMENT_EP = os.getenv("PAYMENTS_EP")
ADDITIONAL_DETAILS_EP = os.getenv("ADDITIONAL_DETAILS_EP")

API_KEY = os.getenv("API_KEY")
MERCHANT_ACCOUNT = os.getenv("MERCHANT_ACCOUNT")
CLIENT_KEY = os.getenv("CLIENT_KEY")

HEADERS = {
    "x-API-key": API_KEY,
    "Content-Type": "application/json"
}


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html', client_key = CLIENT_KEY)


@app.route('/api/getPaymentMethods', methods=["POST"])
def get_payment_methods():
    req = {
        "merchantAccount": MERCHANT_ACCOUNT,
        "channel": "Web",
        "countryCode": "SG",
        "amount": {
            "currency": "SGD",
            "value": 1500
        }
    }

    response = requests.post(BASE_URI + PAYMENT_METHODS_EP, headers = HEADERS, json = req)
    return response.json()

@app.route('/api/initiatePayment', methods=["POST"])
def initiate_payment():
    payment_info = request.get_json()
    req = {
        "amount": {
            "value": 1500,
            "currency": "SGD"
        },
        "channel": "Web",
        "reference": "test_12",
        "shopperReference": "Random Shopper",
        "shopperLocale": "en_US",
        "countryCode": "SG",
        "merchantAccount": MERCHANT_ACCOUNT,
        "additionalData": {
            "allow3DS2": "true"
        },
        "origin": "http://localhost:5000",
        "returnUrl": "http://localhost:5000/api/handleShopperRedirect"
    }

    req.update(payment_info)
    response = requests.post(BASE_URI + PAYMENT_EP, headers = HEADERS, json = req)
    return response.json()

@app.route('/api/submitAdditionalDetails', methods=["POST"])
def additional_details():
    req = request.get_json()
    response = requests.post(BASE_URI + ADDITIONAL_DETAILS_EP, headers = HEADERS, json = req)
    return response.json()

@app.route('/api/handleShopperRedirect', methods=["GET", "POST"])
def handle_redirect():
    incoming = request.json if request.is_json else request.values.to_dict()

    # Handle Alipay / Wechat

    if incoming['resultCode'] == 'authorised':
        return redirect(url_for('result', status='success'))
    elif incoming['resultCode'] == 'refused':
        return redirect(url_for('result', status='failure'))
    else:
        return redirect(url_for('result', status='pending'))
    
    # Handle normal flow

    if "paymentData" in incoming:
        response = requests.post(BASE_URI + ADDITIONAL_DETAILS_EP, headers = HEADERS, json = incoming)

        if response["resultCode"] == "Authorized":
            return redirect(url_for('result', status='success'))
        elif response["resultCode"] == "Received" or response["resultCode"] == "Pending":
            return redirect(url_for('result', status='pending'))
        else:
            return redirect(url_for('result', status='failure'))
    else:
        return render_template('process.html', incoming = incoming)

@app.route('/result/<status>')
def result(status):
    return render_template('result.html', status = status)



