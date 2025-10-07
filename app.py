import os
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# Render এর Environment Variable থেকে API Key লোড হবে
ZYLA_API_KEY = os.getenv("ZYLA_API_KEY")

# Zylalabs API Endpoints
GET_COUNTRIES_URL = "https://zylalabs.com/api/1813/virtual+phone+number+generator+api/1466/get+countries"
GET_NUMBER_BASE_URL = "https://zylalabs.com/api/1813/virtual+phone+number+generator+api/1467/get+number+by+country+id"
CHECK_SMS_BASE_URL = "https://zylalabs.com/api/1813/virtual+phone+number+generator+api/1469/check+sms+history"

@app.route('/')
def index():
    return render_template('index.html')

# generate-number এবং get-countries ফাংশন দুটি আগের মতোই থাকছে
@app.route('/generate-number', methods=['POST'])
def generate_number():
    if not ZYLA_API_KEY:
        return jsonify({"success": False, "error": "API key not configured."}), 500
    data = request.get_json()
    country_code = data.get('countryCode')
    if not country_code:
        return jsonify({"success": False, "error": "Country code is required."}), 400
    headers = {'Authorization': f'Bearer {ZYLA_API_KEY}'}
    request_url = f"{GET_NUMBER_BASE_URL}?countryCode={country_code}"
    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        number_data = response.json()
        # API response format অনুযায়ী .get() পরিবর্তন হতে পারে
        # আমরা এখন পুরো ডেটাটাই পাঠাব, যাতে নম্বর ছাড়াও অন্য তথ্য (যেমন: নম্বর আইডি) ব্যবহার করা যায়
        return jsonify({"success": True, "data": number_data})
    except requests.exceptions.RequestException as e:
        print(f"API Error generating number: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-countries', methods=['GET'])
def get_countries_from_api():
    if not ZYLA_API_KEY:
        return jsonify({"success": False, "error": "API key not configured."}), 500
    headers = {'Authorization': f'Bearer {ZYLA_API_KEY}'}
    try:
        response = requests.get(GET_COUNTRIES_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"API Error fetching countries: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# --- get-messages ফাংশনটি নতুন করে আপডেট করা হয়েছে ---
@app.route('/get-messages', methods=['GET'])
def get_messages():
    """ Frontend থেকে পাঠানো countryCode ও phoneNumber ব্যবহার করে SMS history চেক করে। """
    if not ZYLA_API_KEY:
        return jsonify({"success": False, "error": "API key not configured."}), 500

    # Frontend থেকে Query Parameter হিসেবে ডেটা নেওয়া হচ্ছে
    country_code = request.args.get('countryCode')
    phone_number = request.args.get('phoneNumber')

    if not country_code or not phone_number:
        return jsonify({"success": False, "error": "Country code and phone number are required."}), 400

    headers = {
        'Authorization': f'Bearer {ZYLA_API_KEY}'
    }
    # URL এর সাথে Query Parameter যোগ করা
    request_url = f"{CHECK_SMS_BASE_URL}?countryCode={country_code}&phoneNumber={phone_number}"

    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        sms_data = response.json()
        
        # API থেকে পাওয়া SMS ডেটা Frontend-এ পাঠানো হচ্ছে
        return jsonify({"success": True, "messages": sms_data.get("messages", [])})

    except requests.exceptions.RequestException as e:
        print(f"API Error checking SMS: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
