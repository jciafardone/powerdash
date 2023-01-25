from flask import Flask, render_template, request, flash, session, redirect, jsonify
from model import connect_to_db, db, User, Client, ProfitLoss, Reservation, SalesOrder
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    net_sales_per_class = crud.calc_net_sales_per_class()
    expenses_per_class = crud.calc_expenses_per_class()
    payroll_per_class = crud.calc_payroll_per_class()
    discounts_percentage = crud.calc_total_discounts()
    profit_per_class = crud.calc_profit_per_class()
    profit_margin = crud.calc_profit_margin()
    occupancy_rate = crud.calc_occupancy_rate()
    average_bookings = crud.calc_average_bookings()
    break_even_bookings = crud.calc_break_even_bookings()
    MOM_sales_growth = crud.calc_MOM_net_sales()
    MOM_expense_growth = crud.calc_MOM_expense_growth()
    new_students = crud.calc_new_students()
    retention = crud.calc_retention()

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


# can define routes and add pass so that you can map out where everything will go

@app.route('/date', methods=['POST'])
def get_date_range():
    start_date = request.json.get('startDate')
    end_date = request.json.get('endDate')

    return jsonify({'startDate': start_date,'endDate': end_date})



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)