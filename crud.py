from model import db, User, Client, ProfitLoss, Reservation, SalesOrder, connect_to_db
from sqlalchemy.sql import func

"""Database seed functions."""

def create_user(fname, lname, email):
    user = User(fname=fname, lname=lname, email=email)

    return user


def create_client(client_email, client_fname, client_lname, user_id):
    client = Client(
        client_email = client_email,
        client_fname = client_fname,
        client_lname = client_lname,
        user_id = user_id
    )

    return client


def create_profit_loss(
    user_id, period_start, period_end, total_revenue, total_expenses, payroll_expenses
):
    profit_loss = ProfitLoss(
        user_id = user_id,
        period_start = period_start,
        period_end = period_end,
        total_revenue = total_revenue,
        total_expenses = total_expenses,
        payroll_expenses = payroll_expenses
    )

    return profit_loss


def create_reservation(client_id, class_date, class_name, class_instructor):
    reservation = Reservation(
        client_id = client_id,
        class_date = class_date,
        class_name = class_name,
        class_instructor = class_instructor
    )

    return reservation


def create_sales_order(
    order_date, client_id, item_name, quantity, gross_sale, discount, net_sale
):
    sales_order = SalesOrder(
        order_date = order_date,
        client_id = client_id,
        item_name = item_name,
        quantity = quantity,
        gross_sale = gross_sale,
        discount = discount,
        net_sale = net_sale
    )

    return sales_order



"""KPI queries and calculation functions."""

def calc_net_sales_per_class():
    """Calculate net sales per class in selected period"""

    period_start = '2022-10-01 00:00:00'
    total_revenue = db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == period_start).first()[0]
    count_of_classes_in_period = db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()
    
    return f"${total_revenue/count_of_classes_in_period:.0f}"


def calc_expenses_per_class():
    """Calculcate expenses per class in selected period"""

    period_start = '2022-10-01 00:00:00'
    total_expenses = db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == period_start).first()[0]
    count_of_classes_in_period = db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()
    
    return f"${total_expenses/count_of_classes_in_period:.0f}"


def calc_payroll_per_class():
    """Calculate payroll expenses per class in selected period"""

    period_start = '2022-10-01 00:00:00'
    payroll_expenses = db.session.query(ProfitLoss.payroll_expenses).filter(
        ProfitLoss.period_start == period_start).first()[0]
    count_of_classes_in_period = db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()
    
    return f"${payroll_expenses/count_of_classes_in_period:.0f}"


def calc_total_discounts():
    """Calculate total discount % selected period"""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    total_discounts = db.session.query(func.sum(SalesOrder.discount).filter(
        SalesOrder.order_date >= period_start, SalesOrder.order_date <= period_end)).all()[0][0]
    total_revenue = db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == period_start).first()[0]
    
    return f"{(total_discounts/total_revenue) * 100:.2f}%"


def calc_profit_per_class():
    """Calculate profit per class for period"""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    total_revenue = db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == period_start).first()[0]
    total_expenses = db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == period_start).first()[0]
    count_of_classes_in_period = db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()
    
    return f"${(total_revenue - total_expenses) / count_of_classes_in_period:.0f}"


def calc_profit_margin():
    """Calculate profit margin for period"""

    period_start = '2022-10-01 00:00:00'
    total_revenue = db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == period_start).first()[0]
    total_expenses = db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == period_start).first()[0]
    
    return f"{((total_revenue - total_expenses) / total_revenue) * 100:.2f}%"


def calc_occupancy_rate():
    """Calculate occupancy rate for period"""
    #need to add date filters back in later

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    total_slots_in_period = (db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()) * 8
    attended_slots_in_period = db.session.query(Reservation.reservation_id).count()
    
    return f"{(attended_slots_in_period/total_slots_in_period) * 100:.0f}%"


def calc_average_bookings():
    """Calculate average bookings for period"""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    attended_slots_in_period = db.session.query(Reservation.reservation_id).count()
    count_of_classes_in_period = db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()
    
    return f"{attended_slots_in_period/count_of_classes_in_period:.0f}"


def calc_break_even_bookings():
    """Calculate break even bookings for period"""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    total_expenses = db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == period_start).first()[0]

    #hardcoded for now, need to figure out how to calculate this from crm api
    average_revenue_per_slot = 20 

    count_of_classes_in_period = db.session.query(Reservation).distinct(
        Reservation.class_name, Reservation.class_date, Reservation.class_instructor).count()
    
    return f"{total_expenses/(average_revenue_per_slot * count_of_classes_in_period):.0f}"


def calc_MOM_net_sales():
    """Calculate net sales growth compared to previous period"""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    #previous_period =
    #previous_end = 

    total_revenue = db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == period_start).first()[0]

    
    #hardcoded for now, need to pull from API later
    previous_period_revenue = 47000
    
    return f"{(total_revenue/previous_period_revenue) * 100:.0f}%"


def calc_MOM_expense_growth():
    """Calculate expense growth compared to previous period"""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'
    #previous_period =
    #previous_end = 

    total_expenses = db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == period_start).first()[0]

    
    #hardcoded for now, need to pull from API later
    previous_period_expenses = 47000
    
    return f"{(total_expenses/previous_period_expenses) * 100:.0f}%"


def calc_new_students():
    """Calculcate new students in current period."""

    period_start = '2022-10-01 00:00:00'
    period_end = '2022-10-31 00:00:00'

    all_clients = Client.query.all()
    all_previous_reservations = Reservation.query.filter(Reservation.class_date < period_start)
    current_period_reservations = Reservation.query.filter(
        Reservation.class_date >= period_start, Reservation.class_date <= period_end)
    
    new_clients = 0

    for client in all_clients:
        if client.client_id in current_period_reservations:
            if client.client_id not in all_previous_reservations:
                new_clients += 1
    
    return f"{new_clients:.0f}"


def calc_retention():
    """Calculate 90 day retention rate of clients."""

    period_start = '2022-10-01 00:00:00'
    period_end = '2023-01-31 00:00:00'

    # count_current_period_reservations = db.session.query(Reservation.reservation_id).count()

    #hardcoded for now

    clients_at_end_of_period = db.session.query(Reservation).distinct(
        Reservation.client_id).filter(
            Reservation.class_date >= period_start, Reservation.class_date <= period_end).count()
    clients_at_start_of_period = 20

    # clients_at_start_of_period = db.session.query(Reservation).distinct(
    #     Reservation.client_id).filter(
    #         Reservation.class_date <= period_start).count()

    
    all_clients = Client.query.all()
    all_previous_reservations = Reservation.query.filter(Reservation.class_date < period_start)
    current_period_reservations = Reservation.query.filter(
        Reservation.class_date >= period_start, Reservation.class_date <= period_end)
    
    new_clients = 0

    for client in all_clients:
        if client.client_id in current_period_reservations:
            if client.client_id not in all_previous_reservations:
                new_clients += 1
    
    return f"{((clients_at_end_of_period-new_clients)/clients_at_start_of_period) * 100:.0f}%"






    


   

