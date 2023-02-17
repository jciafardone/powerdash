from model import db, User, Client, ProfitLoss, Reservation, SalesOrder, connect_to_db 
from sqlalchemy.sql import func
from dateutil.relativedelta import *
from dateutil.parser import parse
import csv
from datetime import datetime


"""

Database seed functions. 

These functions are used to create new records in the database tables.

Most of these functions are used below in the API and CSV functions.
create_user is used in server.py in the /users route.

"""

def create_user(email, password):
    """
    Creates a new Powerdash user. Used with 'Create Account' on homepage. 
    In server.py this is the /users route.
    """

    user = User(email=email, password=password)

    return user


def create_guest_user(user_id):
    user = User(user_id=user_id, email=None, password=None)

    return user


def create_client(client_email, client_fname, client_lname, client_crm_id, user_id):
    """Creates a new Powerdash users' client/customer."""

    client = Client(
        client_email = client_email,
        client_fname = client_fname,
        client_lname = client_lname,
        client_crm_id = client_crm_id,
        user_id = user_id
    )

    return client


def create_profit_loss(
    user_id=0, period_start=0, period_end=0, total_revenue=0, total_expenses=0, payroll_expenses=0
):
    #Create a new profit and loss record for a Powerdash users' business.
    profit_loss = ProfitLoss(
        user_id = user_id,
        period_start = period_start,
        period_end = period_end,
        total_revenue = total_revenue,
        total_expenses = total_expenses,
        payroll_expenses = payroll_expenses
    )

    return profit_loss


def create_reservation(client_id, client_crm_id, class_date, class_name, class_instructor, user_id):
    #Create a new reservation record for a Powerdash users' client.
    reservation = Reservation(
        client_id = client_id,
        client_crm_id = client_crm_id,
        class_date = class_date,
        class_name = class_name,
        class_instructor = class_instructor,
        user_id = user_id
    )

    return reservation


def create_sales_order(
    order_date, client_id, item_name, quantity, gross_sale, discount, net_sale, user_id
):
    #Create a new sales order record of a Powerdash users' client.
    sales_order = SalesOrder(
        order_date = order_date,
        client_id = client_id,
        item_name = item_name,
        quantity = quantity,
        gross_sale = gross_sale,
        discount = discount,
        net_sale = net_sale,
        user_id = user_id
    )

    return sales_order



"""
Database query functions.

These functions query data from database tables. They are used in the KPI
calculation functions below.

"""

def get_user_by_email(email):
    """Returns a user by email. Used in the /login route in server.py."""

    return User.query.filter(User.email == email).first()


def get_user_id_by_email(email):
    """
    Returns a user's id using their email as a lookup. 
    
    Used in the /date route in server.py. 
    Used when a session is active to match database entries to
    the correct user id. 
    
    """
    try:
        user = User.query.filter(User.email == email).first()
        id = user.user_id
        return id
    except:
        pass


def query_total_revenue(start_date, end_date, user_id):
    """Queries total revenue for a period."""

    return db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == start_date, 
        ProfitLoss.period_end == end_date,
        ProfitLoss.user_id == user_id).first()[0]
        


def query_total_expenses(start_date, end_date, user_id):
    """Queries total expenses for a period."""

    return db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == start_date, 
        ProfitLoss.period_end == end_date,
        ProfitLoss.user_id == user_id).first()[0]


def query_payroll_expenses(start_date, end_date, user_id):
    """Queries total payroll expenses for period."""

    return db.session.query(ProfitLoss.payroll_expenses).filter(
        ProfitLoss.period_start == start_date, 
        ProfitLoss.period_end == end_date,
        ProfitLoss.user_id == user_id).first()[0]


def query_discounts(start_date, end_date, user_id):
    """Queries total discount amount on sales orders for period."""

    return db.session.query(func.sum(SalesOrder.discount).filter(
        SalesOrder.order_date >= start_date, 
        SalesOrder.order_date <= end_date,
        # SalesOrder.user_id == user_id)
        )
        ).all()[0][0]


def query_count_of_classes_in_period(start_date, end_date, user_id):
    """Queries number of unique classes in a period."""

    return db.session.query(Reservation).filter(
        Reservation.user_id == user_id,
        Reservation.class_date.between(start_date, end_date)).distinct(
        Reservation.class_name, 
        Reservation.class_date, 
        Reservation.class_instructor).count()


def query_total_slots_in_period(start_date, end_date, user_id, max_slots_per_class=8):
    """Queries total possible client slots in period."""

    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)
    
    return class_count * max_slots_per_class


def query_attended_slots(start_date, end_date, user_id):
    """Queries total attended slots in period."""

    return db.session.query(Reservation.reservation_id).filter(
        Reservation.class_date >= start_date, 
        Reservation.class_date <= end_date,
        Reservation.user_id == user_id).count()


def query_for_profit_margins_chart(user_id):
    """
    Queries and returns a list of tuples where each tuple 
    contains the period start date and the profit margin
    for that period.

    Used to generate profit margin line chart in chart.js.
    """

    profit_margins = []

    rows = ProfitLoss.query.filter(ProfitLoss.user_id == user_id).all()

    for row in rows:
        total_revenue = row.total_revenue
        total_expenses = row.total_expenses
        start_date = row.period_start.isoformat()
        profit_margin = (total_revenue - total_expenses) / total_revenue
        profit_margin_chart_point = tuple([start_date, profit_margin])
        profit_margins.append(profit_margin_chart_point)

    return profit_margins


def query_revenue_for_revexp_chart(user_id):
    """
    Queries and returns a list of tuples that contains 
    the period start date and total revenue for that
    period.

    Used to generate rev and expense bar chart in chart.js.
    """

    revenues = []

    rows = ProfitLoss.query.filter(ProfitLoss.user_id == user_id).all()

    for row in rows:
        total_revenue = row.total_revenue
        start_date = row.period_start.isoformat()
        revenue_chart_point = tuple([start_date, total_revenue])
        revenues.append(revenue_chart_point)

    return revenues


def query_expenses_for_revexp_chart(user_id):
    """
    Queries and returns a list of tuples that contains 
    the period start date and total expenses for that
    period.
    
    Used to generate rev and expense bar chart in chart.js.
    """

    expenses = []

    rows = ProfitLoss.query.filter(ProfitLoss.user_id == user_id).all()

    for row in rows:
        total_expenses = row.total_expenses
        start_date = row.period_start.isoformat()
        expenses_chart_point = tuple([start_date, total_expenses])
        expenses.append(expenses_chart_point)

    return expenses



"""
KPI Calculation Functions.

These functions use the above query functions to calculate
metrics for the KPI table in the report that is generated
using Powerdash users' business information.

These are used in /date route in server.py where start_date
and end_date are pulled in via an AJAX request.

"""

def calc_net_sales_per_class(start_date, end_date, user_id):
    """Calculate net sales per class in selected period"""

    total_revenue = query_total_revenue(start_date, end_date, user_id)
    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)
    
    return f"${total_revenue/class_count:.0f}"


def calc_expenses_per_class(start_date, end_date, user_id):
    """Calculcate expenses per class in selected period"""

    total_expenses = query_total_expenses(start_date, end_date, user_id)
    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)

    return f"${total_expenses/class_count:.0f}"


def calc_payroll_per_class(start_date, end_date, user_id):
    """Calculate payroll expenses per class in selected period"""

    payroll_expenses = query_payroll_expenses(start_date, end_date, user_id)
    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)

    return f"${payroll_expenses/class_count:.0f}"


def calc_total_discounts(start_date, end_date, user_id):
    """Calculate total discount % selected period"""

    total_discounts = query_discounts(start_date, end_date, user_id)
    total_revenue = query_total_revenue(start_date, end_date, user_id)
    
    return f"{(total_discounts/total_revenue) * 100:.2f}%"


def calc_profit_per_class(start_date, end_date, user_id):
    """Calculate profit per class for period"""

    total_revenue = query_total_revenue(start_date, end_date, user_id)
    total_expenses = query_total_expenses(start_date, end_date, user_id)
    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)
    # class_count = 20

    return f"${(total_revenue - total_expenses) / class_count:.0f}"


def calc_profit_margin(start_date, end_date, user_id):
    """Calculate profit margin for period"""

    total_revenue = query_total_revenue(start_date, end_date, user_id)
    total_expenses = query_total_expenses(start_date, end_date, user_id)
    
    return f"{((total_revenue - total_expenses) / total_revenue) * 100:.2f}%"


def calc_occupancy_rate(start_date, end_date, user_id):
    """Calculate occupancy rate for period"""

    total_slots_in_period = query_total_slots_in_period(start_date, end_date, user_id, max_slots_per_class=8)
    attended_slots_in_period = query_attended_slots(start_date, end_date, user_id)
    
    return f"{(attended_slots_in_period/total_slots_in_period) * 100:.0f}%"


def calc_average_bookings(start_date, end_date, user_id):
    """Calculate average bookings for period"""

    attended_slots_in_period = query_attended_slots(start_date, end_date, user_id)
    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)
    
    return f"{attended_slots_in_period/class_count:.0f}"


def calc_break_even_bookings(start_date, end_date, user_id):
    """Calculate break even bookings for period"""

    total_expenses = query_total_expenses(start_date, end_date, user_id)
    class_count = query_count_of_classes_in_period(start_date, end_date, user_id)
    average_revenue_per_slot = 20 #hardcoded for now, need to figure out how to calculate this from crm api

    return f"{total_expenses/(average_revenue_per_slot * class_count):.0f}"


def calc_MOM_net_sales(start_date, end_date, user_id):
    """Calculate net sales growth compared to previous period"""

    previous_start = parse(start_date) - relativedelta(month=1)
    previous_end = parse(end_date) - relativedelta(month=1)

    total_revenue = query_total_revenue(start_date, end_date, user_id)
    previous_period_revenue = query_total_revenue(previous_start, previous_end, user_id)
    
    return f"{(total_revenue/previous_period_revenue) * 100:.0f}%"


def calc_MOM_expense_growth(start_date, end_date, user_id):
    """Calculate expense growth compared to previous period"""

    previous_start = parse(start_date) - relativedelta(month=1)
    previous_end = parse(end_date) - relativedelta(month=1)

    total_expenses = query_total_expenses(start_date, end_date, user_id)
    previous_period_expenses = query_total_expenses(previous_start, previous_end, user_id)
    
    return f"{(total_expenses/previous_period_expenses) * 100:.0f}%"


def calc_new_students(start_date, end_date):
    """Calculcate new students in current period."""

    all_clients = Client.query.all()
    all_previous_reservations = Reservation.query.filter(
        Reservation.class_date < start_date)
    current_period_reservations = Reservation.query.filter(
        Reservation.class_date >= start_date, 
        Reservation.class_date <= end_date)
    
    new_clients = 0

    for client in all_clients:
        if client.client_id not in all_previous_reservations:
            new_clients += 1
    
    return f"{new_clients:.0f}"


def calc_retention(start_date, end_date):
    """Calculate 90 day retention rate of clients."""

    clients_at_end_of_period = db.session.query(Reservation).distinct(
        Reservation.client_id).filter( 
            Reservation.class_date <= end_date).count()
    clients_at_start_of_period = db.session.query(Reservation).distinct(
            Reservation.client_id).filter(
            Reservation.class_date <= start_date).count()
    clients_at_start_of_period = 20

    new_clients = int(calc_new_students(start_date, end_date))
    
    return f"{((clients_at_end_of_period - new_clients) / clients_at_start_of_period) * 100:.0f}%"


"""
API Functions.

These functions translate data from API pulls to match 
the format of database tables. Then the newly created
rows are added and committed to the database.
"""

def push_accounting_data(data, user_id, start_date, end_date):
    """
    Takes in Acconting API data and creates new profit and loss records in the 
    profit_and_loss table.
    """

    profit_loss_query = db.session.query(ProfitLoss).filter(
        ProfitLoss.user_id == user_id).all()
    
    try:
        total_revenue, total_expenses, payroll_expenses = (
            data['Rows']['Row'][0]['Summary']['ColData'][1]['value'],
            data['Rows']['Row'][3]['Summary']['ColData'][1]['value'],
            data['Rows']['Row'][3]['Rows']['Row'][7]['ColData'][1]['value'])

        profit_loss_record = create_profit_loss(
            user_id, start_date, end_date, total_revenue, total_expenses, payroll_expenses)

        if profit_loss_query == []:
            db.session.add(profit_loss_record)
            db.session.commit()

        in_database = False

        for row in profit_loss_query:
            if (
                row.start_date == profit_loss_record.start_date 
                and row.end_date == profit_loss_record.end_date 
                and row.total_revenue == profit_loss_record.total_revenue 
                and row.total_expenses == profit_loss_record.total_expenses 
                and row.payroll_expenses == profit_loss_record.payroll_expenses
              ):
                in_database = True
            
        if in_database == False:
            db.session.add(profit_loss_record)
            db.session.commit()
    except:
        pass


def push_customer_data(data, user_id):
    """
    Takes in CRM API data and creates new client records in the clients table.
    """

    client_query = db.session.query(Client).filter(
        Client.user_id == user_id).all()

    try: 
        for customer in data['customers']:
            client_fname, client_lname, client_email, client_crm_id = (
                customer['given_name'],
                customer['family_name'],
                customer['email_address'],
                customer['id']
                )
            
            customer_record = create_client(
                client_email, client_fname, client_lname, client_crm_id, user_id)

            if client_query == []:
                db.session.add(customer_record)
                db.session.commit()

            in_database = False

            for row in client_query:
                if (
                    row.client_fname == customer_record.client_fname
                    and row.client_lname == customer_record.client_lname 
                    and row.client_email == customer_record.client_email 
                    and row.client_crm_id == customer_record.client_crm_id
                ):
                    in_database = True
                
            if in_database == False:
                db.session.add(customer_record)
                db.session.commit()
    except:
        pass


def push_bookings_data(data, user_id):
    """
    Takes in CRM API data and creates new reservation records in the 
    reservation_data table.
    """

    reservation_query = db.session.query(Reservation).filter(
        Reservation.user_id == user_id).all()

    try:
        for booking in data['bookings']:
            user_id_tuple = db.session.query(Client.client_id).filter_by(client_crm_id=booking["customer_id"]).first()
            
            client_id,client_crm_id, class_date, class_name, class_instructor = (
                user_id_tuple[0],
                booking["customer_id"],
                booking["start_at"],
                booking["appointment_segments"][0]["service_variation_id"],
                booking["appointment_segments"][0]["team_member_id"]
                )

            booking_record = create_reservation(
                client_id,client_crm_id, class_date, class_name, class_instructor, user_id)
            
            if reservation_query == []:
                db.session.add(booking_record)
                db.session.commit()
            
            in_database = False

            #need to correct for difference in datetime formats
            booking_record_date = str(booking_record.class_date)[:10]+' '+str(booking_record.class_date)[11:-1]

            for row in reservation_query:
                if (
                    row.client_id == booking_record.client_id
                    and row.client_crm_id == booking_record.client_crm_id
                    and str(row.class_date) == booking_record_date
                    and row.class_name == booking_record.class_name
                    and row.class_instructor == booking_record.class_instructor
                ):
                    in_database = True

            if in_database == False:
                db.session.add(booking_record)
                db.session.commit()
    except:
        pass


"""
CSV CRUD Functions.

These functions translate data from CSV uploads to match the format of database 
tables. Then the newly created rows are added and committed to the database.

"""

def pull_reservation_data_from_csv(crm_csv, user_id):
    """
    Takes in a CSV and creates new reservation records in the 
    reservation_data table.
    """
    try: 
        reservation_query = db.session.query(Reservation).filter(
            Reservation.user_id == user_id).all()

        with open(crm_csv, newline='') as csv_file:
            
            csvreader = csv.DictReader(csv_file, quotechar='"')

            for reservation in csvreader:
                client_id,client_crm_id, class_date, class_name, class_instructor = (
                    reservation["client_id"],
                    reservation["client_crm_id"],
                    reservation["class_date"],
                    reservation["class_name"],
                    reservation["class_instructor"],
                )

                booking_record = create_reservation(
                    client_id,client_crm_id, class_date, class_name, class_instructor, user_id)

                if reservation_query == []:
                    db.session.add(booking_record)
                    db.session.commit()
                
                in_database = False

                for row in reservation_query:
                    if (
                        row.client_id == booking_record.client_id
                        and row.client_crm_id == booking_record.client_crm_id
                        and str(row.class_date) == str(booking_record.date)
                        and row.class_name == booking_record.class_name
                        and row.class_instructor == booking_record.class_instructor
                    ):
                        in_database = True

                if in_database == False:
                    db.session.add(booking_record)
                    db.session.commit()
    except:
        pass


def pull_pl_data_from_csv(accounting_csv, user_id):
    """
    Takes in a CSV and creates new profit and loss records in the 
    profit_and_loss table.
    """
    try: 
        profit_loss_query = db.session.query(ProfitLoss).filter(
            ProfitLoss.user_id == user_id).all()

        with open(accounting_csv, newline='') as csv_file:

            csvreader = csv.DictReader(csv_file, quotechar='"')

            for pl_record in csvreader:
                period_start, period_end, total_revenue, total_expenses, payroll_expenses = (
                    pl_record["period_start"],
                    pl_record["period_end"],
                    pl_record["total_revenue"],
                    pl_record["total_expenses"],
                    pl_record["payroll_expenses"]
                )

                profit_loss_record = create_profit_loss(
                    user_id, period_start, period_end, total_revenue, total_expenses, payroll_expenses)

                if profit_loss_query == []:
                    db.session.add(profit_loss_record)
                    db.session.commit()

                in_database = False

                for row in profit_loss_query:
                    if (
                        row.start_date == profit_loss_record.start_date 
                        and row.end_date == profit_loss_record.end_date 
                        and row.total_revenue == profit_loss_record.total_revenue 
                        and row.total_expenses == profit_loss_record.total_expenses 
                        and row.payroll_expenses == profit_loss_record.payroll_expenses
                    ):
                        in_database = True
                    
                if in_database == False:
                    db.session.add(profit_loss_record)
                    db.session.commit()
    except:
        pass


"""Delete function for guest users."""
def delete_guest_info(user_id):
    Client.query.filter(Client.user_id == user_id).delete()
    Reservation.query.filter(Reservation.user_id == user_id).delete()
    SalesOrder.query.filter(SalesOrder.user_id == user_id).delete()
    ProfitLoss.query.filter(ProfitLoss.user_id == user_id).delete()
    User.query.filter(User.user_id == user_id).delete()
    db.session.commit()



if __name__ == "__main__":
    """Copied from Hackbright Movie Ratings Lab."""

    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app, echo=False)




    




