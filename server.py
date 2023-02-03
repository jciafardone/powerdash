from flask import Flask, render_template, request, flash, session, redirect, jsonify, url_for
from model import connect_to_db, db, User, Client, ProfitLoss, Reservation, SalesOrder
from jinja2 import StrictUndefined
import crud
import requests
import json
import os
from base64 import b64encode

#App configuration
app = Flask(__name__)

#Session configuration
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

#global variables
start_date = None
end_date = None
accounting_data = None
crm_customer_data = None
crm_bookings_data = None
accounting_realm_id = None
accounting_access_token = None
crm_access_token = None


"""Routes and functions to render pages and user flow"""

@app.route("/")
def homepage():
    """View homepage."""
    return render_template(
        "index.html")


@app.route('/accounting')
def render_accounting():
    """Render accounting API login page"""
    return render_template('accounting.html')


@app.route('/crm')
def render_crm():
    """Render crm API login page"""
    return render_template('crm.html')


@app.route('/report')
def render_report():
    """Renders report page"""
    net_sales_per_class = ""
    expenses_per_class = ""
    payroll_per_class = ""
    discounts_percentage = ""
    profit_per_class = ""
    profit_margin = ""
    occupancy_rate = ""
    average_bookings = ""
    break_even_bookings = ""
    MOM_sales_growth = ""
    MOM_expense_growth = ""
    new_students = ""
    retention = ""

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


"""Route and function to update KPI report based on selected date range"""

@app.route('/date', methods=['POST'])
def get_date_range():
    """Update KPI table and data visulaizations based on date filters"""
    global start_date
    global end_date
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')

    #Accounting API GET request and push to database
    global accounting_data
    accounting_data = requests.get((f'https://sandbox-quickbooks.api.intuit.com/v3/company/{accounting_realm_id}/reports/ProfitAndLoss'
        '?start_date={start_date}&end_date={end_date}'),
        headers={
            'Authorization': f'Bearer {accounting_access_token}',
            })

    accounting_data = accounting_data.json()
    crud.push_accounting_data(accounting_data)

    #CRM API GET request for customers and push to database
    global crm_customer_data
    crm_customer_data = requests.get('https://connect.squareup.com/v2/customers',
        headers={
            'Square-Version': '2023-01-19',
            'Authorization': f'Bearer {crm_access_token}',
            'Content-Type': 'application/json'
        })
    
    crm_customer_data = crm_customer_data.json()
    crud.push_customer_data(crm_customer_data)

    #CRM API GET request for bookings and push to database
    global crm_bookings_data
    crm_bookings_data = requests.get('https://connect.squareup.com/v2/bookings', 
        headers = {
            'Square-Version': '2023-01-19',
            'Authorization': f'Bearer {crm_access_token}',
            'Content-Type': 'application/json',
        })
    crm_bookings_data = crm_bookings_data.json()
    crud.push_bookings_data(crm_bookings_data, start_date, end_date)

    #Update KPI table based on date range filter
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

    #Prepare data for profit margins chart
    profit_margin_query = crud.query_for_profit_margins_chart()

    profit_margins = []

    for date, margin in profit_margin_query:
        profit_margins.append({'date': date,
                                'profit_margin': margin})
    
    #Prepare revenue data for revenue and expense bar chart
    revenue_chart_query = crud.query_revenue_for_revexp_chart()

    revenues = []

    for date, revenue in revenue_chart_query:
        revenues.append({'date': date,
                        'revenue': revenue})

    #Prepare expense data for revenue and expense bar chart
    expense_chart_query = crud.query_expenses_for_revexp_chart()

    expenses = []

    for date, expense in expense_chart_query:
        expenses.append({'date': date,
                        'expense': expense})


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
        'class_count': class_count,
        'profit_margin_chart_data': profit_margins,
        'revenue_chart_data': revenues,
        'expense_chart_data': expenses})


"""Routes for API Calls"""

@app.route('/wave_login')
def get_wave_data():
    """Redirects to accounting API OAuth"""
    return redirect(('https://appcenter.intuit.com/connect/oauth2'
        '?client_id=ABqvERIi2PV5RFCrmU19uJZPQ3dvTRxpmhEkWmAD3CusCCl8hC'
        '&response_type=code'
        '&scope=com.intuit.quickbooks.accounting'
        '&redirect_uri=http://localhost:5000/authorize'
        '&state=abcde'))


@app.route('/authorize')
def authorize():
    """Continues accounting API code/token exchange"""
    code = request.args['code']
    
    global accounting_realm_id
    accounting_realm_id = request.args['realmId']

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

    global accounting_access_token
    accounting_access_token = token_info['access_token']

    return render_template('crm.html')


@app.route('/crm_login')
def get_crm_data():
    """redirect to Square OAuth authorization; will automatically redirect to /crm_authorize route"""

    return redirect(('https://connect.squareup.com/oauth2/authorize'
        '?client_id=sq0idp-oFiVzZcWnbGU4Z0iPhvwNA'
        '&scope=CUSTOMERS_READ+APPOINTMENTS_READ+ORDERS_READ'
        '&session=False'
        '&state=82201dd8d83d23cc8a48caf52b'
        'redirect_uri=http://localhost:5000/crm_authorize'
        ))


@app.route('/crm_authorize')
def crm_authorize():
    """Continues crm API code/token exchange"""

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

    global crm_access_token
    crm_access_token = response['access_token']
    
    return redirect('/report')





if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)