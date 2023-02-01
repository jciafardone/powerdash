from flask import Flask, render_template, request, flash, session, redirect, jsonify, url_for
from model import connect_to_db, db, User, Client, ProfitLoss, Reservation, SalesOrder
from jinja2 import StrictUndefined
from authlib.integrations.flask_client import OAuth
import crud
import requests
import json
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
from base64 import b64encode

#App configuration
app = Flask(__name__)

#Session configuration
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

#OAuth configuration
oauth = OAuth(app)
wave = oauth.register(
    name='powerdash',
    client_id='6z9C5rIqMonNqvKVAMG8bM_aB0_KMYFwf6M0aKTb',
    client_secret='Sd89gYiEIvPqUdwfnmwDPgCSA4dRgxCHivEV8i8LQgVHcZJzV9ZAKpeSCHWef5z7H9LiWxltTYa56uCSI15v75d5UAFhBRaUmxV4wOWlbbkqJRNA8exnDmMWJin8LT9x',
    access_token_url='https://api.waveapps.com/oauth2/token/',
    access_token_params=None,
    authorize_url='https://api.waveapps.com/oauth2/authorize/',
    authorize_params=None,
    api_base_url='https://gql.waveapps.com/graphql/public/',
    client_kwargs={'scope': 'account:read business:read user:read'}
)

#global variables
start_date = None
end_date = None
accounting_data = None
crm_data = None


@app.route("/")
def homepage():
    """View homepage."""
    start_date = '2022-10-01 00:00:00'
    end_date = '2022-10-31 00:00:00'

    net_sales_per_class = crud.calc_net_sales_per_class(start_date, end_date)
    expenses_per_class = crud.calc_expenses_per_class(start_date, end_date)
    payroll_per_class = crud.calc_payroll_per_class(start_date, end_date)
    discounts_percentage = crud.calc_total_discounts(start_date, end_date)
    profit_per_class = crud.calc_profit_per_class(start_date, end_date)
    profit_margin = crud.calc_profit_margin(start_date, end_date)
    occupancy_rate = crud.calc_occupancy_rate(start_date, end_date)
    average_bookings = crud.calc_average_bookings(start_date, end_date)
    break_even_bookings = crud.calc_break_even_bookings(start_date, end_date)
    MOM_sales_growth = crud.calc_MOM_net_sales(start_date, end_date)
    MOM_expense_growth = crud.calc_MOM_expense_growth(start_date, end_date)
    new_students = crud.calc_new_students(start_date, end_date)
    retention = crud.calc_retention(start_date, end_date)

    return render_template(
        "index.html", 
        net_sales_per_class=net_sales_per_class, 
        expenses_per_class=expenses_per_class, 
        payroll_per_class=payroll_per_class,
        discounts_percentage=discounts_percentage,
        profit_per_class=profit_per_class,
        profit_margin=profit_margin,
        occupancy_rate=occupancy_rate,
        average_bookings=average_bookings,
        break_even_bookings=break_even_bookings,
        MOM_sales_growth=MOM_sales_growth,
        MOM_expense_growth=MOM_expense_growth,
        new_students=new_students,
        retention=retention)


@app.route('/date', methods=['POST'])
def get_date_range():
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')

    net_sales_per_class = crud.calc_net_sales_per_class(start_date, end_date)
    expenses_per_class = crud.calc_expenses_per_class(start_date, end_date)
    payroll_per_class = crud.calc_payroll_per_class(start_date, end_date)
    discounts_percentage = crud.calc_total_discounts(start_date, end_date)
    profit_per_class = crud.calc_profit_per_class(start_date, end_date)
    profit_margin = crud.calc_profit_margin(start_date, end_date)
    occupancy_rate = crud.calc_occupancy_rate(start_date, end_date)
    average_bookings = crud.calc_average_bookings(start_date, end_date)
    break_even_bookings = crud.calc_break_even_bookings(start_date, end_date)
    MOM_sales_growth = crud.calc_MOM_net_sales(start_date, end_date)
    MOM_expense_growth = crud.calc_MOM_expense_growth(start_date, end_date)
    new_students = crud.calc_new_students(start_date, end_date)
    retention = crud.calc_retention(start_date, end_date)
    total_revenue = crud.query_total_revenue(start_date, end_date)
    class_count = crud.query_count_of_classes_in_period(start_date, end_date)

    return jsonify({'startDate': start_date,
        'endDate': end_date,
        'net_sales_per_class': net_sales_per_class,
        'expenses_per_class': expenses_per_class,
        'payroll_per_class': payroll_per_class,
        'discounts_percentage': discounts_percentage,
        'profit_per_class': profit_per_class,
        'profit_margin': profit_margin,
        'occupancy_rate': occupancy_rate,
        'average_bookings': average_bookings,
        'break_even_bookings': break_even_bookings,
        'MOM_sales_growth': MOM_sales_growth,
        'MOM_expense_growth': MOM_expense_growth,
        'new_students': new_students,
        'retention': retention,
        'total_revenue': total_revenue,
        'class_count': class_count})


@app.route('/accounting')
def render_accounting():
    return render_template('accounting.html')


@app.route('/crm')
def render_crm():
    return render_template('crm.html')


@app.route('/date-range')
def render_date_range():
    return render_template('date-range.html')


@app.route('/wave_login')
def get_wave_data():
    return redirect(('https://appcenter.intuit.com/connect/oauth2'
        '?client_id=ABqvERIi2PV5RFCrmU19uJZPQ3dvTRxpmhEkWmAD3CusCCl8hC'
        '&response_type=code'
        '&scope=com.intuit.quickbooks.accounting'
        '&redirect_uri=http://localhost:5000/authorize'
        '&state=abcde'))

@app.route('/authorize')
def authorize():
    code = request.args['code']
    state = request.args['state']
    realm_id = request.args['realmId']

    client = 'ABqvERIi2PV5RFCrmU19uJZPQ3dvTRxpmhEkWmAD3CusCCl8hC:mXbnjKc4fhLHS6ZB3S8VS741ZOyTy8zU1b1hEIvK'.encode("utf-8")
    client = b64encode(client)
    client = client.decode("utf-8")

    url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
    headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic ' + client,
        }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost:5000/authorize',
    }

    token_info = requests.post(url, headers=headers, data=data)
    token_info = token_info.json()
    access_token = token_info['access_token']

    accounting_data = requests.get(f'https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/reports/ProfitAndLoss',
        headers={
            'Authorization': f'Bearer {access_token}',
            })

    return render_template('crm.html')


@app.route('/crm_login')
def get_crm_data():
    #redirect to Square OAuth authorization; will automatically redirect to /crm_authorize route
    return redirect(('https://connect.squareup.com/oauth2/authorize'
        '?client_id=sq0idp-oFiVzZcWnbGU4Z0iPhvwNA'
        '&scope=CUSTOMERS_WRITE+CUSTOMERS_READ'
        '&session=False'
        '&state=82201dd8d83d23cc8a48caf52b'
        'redirect_uri=http://localhost:5000/crm_authorize'
        ))

@app.route('/crm_authorize')
def crm_authorize():
    #get OAuth authorization code
    code = request.args['code']

    #prepare POST request to exchange code for access token
    #converted curl to python
    headers = {
    'Square-Version': '2023-01-19',
    'Content-Type': 'application/json',
     }

    json_data = {
        'client_id': 'sq0idp-oFiVzZcWnbGU4Z0iPhvwNA',
        'client_secret': 'sq0csp-Eu05X81ztEMDh9-2k_rFG-ax_XHVagdWvA_YiJqCdb8',
        'code': code,
        'grant_type': 'authorization_code',
    }

    #send POST request and collect access token
    response = requests.post('https://connect.squareup.com/oauth2/token', headers=headers, json=json_data)
    response = response.json()
    access_token = response['access_token']

    #GET requests for API pulls
    crm_data = requests.get('https://connect.squareup.com/v2/customers',
        headers={
            'Square-Version': '2023-01-19',
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
            })
    
    return redirect('/report')

@app.route('/report')
def render_report():
    start_date = '2022-10-01 00:00:00'
    end_date = '2022-10-31 00:00:00'

    net_sales_per_class = crud.calc_net_sales_per_class(start_date, end_date)
    expenses_per_class = crud.calc_expenses_per_class(start_date, end_date)
    payroll_per_class = crud.calc_payroll_per_class(start_date, end_date)
    discounts_percentage = crud.calc_total_discounts(start_date, end_date)
    profit_per_class = crud.calc_profit_per_class(start_date, end_date)
    profit_margin = crud.calc_profit_margin(start_date, end_date)
    occupancy_rate = crud.calc_occupancy_rate(start_date, end_date)
    average_bookings = crud.calc_average_bookings(start_date, end_date)
    break_even_bookings = crud.calc_break_even_bookings(start_date, end_date)
    MOM_sales_growth = crud.calc_MOM_net_sales(start_date, end_date)
    MOM_expense_growth = crud.calc_MOM_expense_growth(start_date, end_date)
    new_students = crud.calc_new_students(start_date, end_date)
    retention = crud.calc_retention(start_date, end_date)

    return render_template(
        "date-range.html", 
        net_sales_per_class=net_sales_per_class, 
        expenses_per_class=expenses_per_class, 
        payroll_per_class=payroll_per_class,
        discounts_percentage=discounts_percentage,
        profit_per_class=profit_per_class,
        profit_margin=profit_margin,
        occupancy_rate=occupancy_rate,
        average_bookings=average_bookings,
        break_even_bookings=break_even_bookings,
        MOM_sales_growth=MOM_sales_growth,
        MOM_expense_growth=MOM_expense_growth,
        new_students=new_students,
        retention=retention)




if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)