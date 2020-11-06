from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv
load_dotenv()


BASE_URI = os.getenv("BASE_URI")
PAYMENT_METHODS_EP = os.getenv("PAYMENT_METHODS_EP")
PAYMENT_EP = os.getenv("PAYMENT_EP")
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