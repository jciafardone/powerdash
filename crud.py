from model import db, User, Client, ProfitLoss, Reservation, SalesOrder, connect_to_db
from sqlalchemy.sql import func
from server import get_start_date

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



"""Query Functions"""

def query_total_revenue(start_date, end_date):
    """Queries total revenue for a period"""
    return db.session.query(ProfitLoss.total_revenue).filter(
        ProfitLoss.period_start == start_date, 
        ProfitLoss.period_end == end_date).first()[0]


def query_total_expenses(start_date, end_date):
    """Queries total expenses for a period"""
    return db.session.query(ProfitLoss.total_expenses).filter(
        ProfitLoss.period_start == start_date, 
        ProfitLoss.period_end == end_date).first()[0]


def query_payroll_expenses(start_date, end_date):
    """Queries total payroll expenses for period"""
    return db.session.query(ProfitLoss.payroll_expenses).filter(
        ProfitLoss.period_start == start_date, 
        ProfitLoss.period_end == end_date).first()[0]


def query_discounts(start_date, end_date):
    """Queries total discount amount for period"""
    return db.session.query(func.sum(SalesOrder.discount).filter(
        SalesOrder.order_date >= start_date, 
        SalesOrder.order_date <= end_date)).all()[0][0]


def query_count_of_classes_in_period(start_date, end_date):
    """Queries number of unique classes in a period"""
    return db.session.query(Reservation).filter(
        Reservation.class_date.between(start_date, end_date)).distinct(
        Reservation.class_name, 
        Reservation.class_date, 
        Reservation.class_instructor).count()


def query_total_slots_in_period(start_date, end_date, max_slots_per_class=8):
    """Queries total possible client slots in period"""
    class_count = query_count_of_classes_in_period(start_date, end_date)
    
    return class_count * max_slots_per_class


def query_attended_slots(start_date, end_date):
    """Queries total attended slots in period"""
    return db.session.query(Reservation.reservation_id).filter(
        Reservation.class_date >= start_date, 
        Reservation.class_date <= end_date).count()




"""KPI Calculation Functions"""

def calc_net_sales_per_class(start_date, end_date):
    """Calculate net sales per class in selected period"""
    total_revenue = query_total_revenue(start_date, end_date)
    class_count = query_count_of_classes_in_period(start_date, end_date)
    
    return f"${total_revenue/class_count:.0f}"


def calc_expenses_per_class(start_date, end_date):
    """Calculcate expenses per class in selected period"""
    total_expenses = query_total_expenses(start_date, end_date)
    class_count = query_count_of_classes_in_period(start_date, end_date)

    return f"${total_expenses/class_count:.0f}"


def calc_payroll_per_class(start_date, end_date):
    """Calculate payroll expenses per class in selected period"""
    payroll_expenses = query_payroll_expenses(start_date, end_date)
    class_count = query_count_of_classes_in_period(start_date, end_date)

    return f"${payroll_expenses/class_count:.0f}"


def calc_total_discounts(start_date, end_date):
    """Calculate total discount % selected period"""
    total_discounts = query_discounts(start_date, end_date)
    total_revenue = query_total_revenue(start_date, end_date)
    
    return f"{(total_discounts/total_revenue) * 100:.2f}%"


def calc_profit_per_class(start_date, end_date):
    """Calculate profit per class for period"""
    total_revenue = query_total_revenue(start_date, end_date)
    total_expenses = query_total_expenses(start_date, end_date)
    class_count = query_count_of_classes_in_period(start_date, end_date)
    class_count = 20

    return f"${(total_revenue - total_expenses) / class_count:.0f}"


def calc_profit_margin(start_date, end_date):
    """Calculate profit margin for period"""
    total_revenue = query_total_revenue(start_date, end_date)
    total_expenses = query_total_expenses(start_date, end_date)
    
    return f"{((total_revenue - total_expenses) / total_revenue) * 100:.2f}%"


def calc_occupancy_rate(start_date, end_date):
    """Calculate occupancy rate for period"""
    total_slots_in_period = query_total_slots_in_period(start_date, end_date, max_slots_per_class=8)
    attended_slots_in_period = query_attended_slots(start_date, end_date)
    
    return f"{(attended_slots_in_period/total_slots_in_period) * 100:.0f}%"


def calc_average_bookings(start_date, end_date):
    """Calculate average bookings for period"""
    attended_slots_in_period = query_attended_slots(start_date, end_date)
    class_count = query_count_of_classes_in_period(start_date, end_date)
    
    return f"{attended_slots_in_period/class_count:.0f}"


def calc_break_even_bookings(start_date, end_date):
    """Calculate break even bookings for period"""
    total_expenses = query_total_expenses(start_date, end_date)
    class_count = query_count_of_classes_in_period(start_date, end_date)
    average_revenue_per_slot = 20 #hardcoded for now, need to figure out how to calculate this from crm api

    return f"{total_expenses/(average_revenue_per_slot * class_count):.0f}"


def calc_MOM_net_sales(start_date, end_date):
    """Calculate net sales growth compared to previous period"""
    previous_start = '2022-12-01 00:00:00'
    previous_end = '2022-12-31 00:00:00'

    total_revenue = query_total_revenue(start_date, end_date)
    previous_period_revenue = query_total_revenue(previous_start, previous_end)
    
    return f"{(total_revenue/previous_period_revenue) * 100:.0f}%"


def calc_MOM_expense_growth(start_date, end_date):
    """Calculate expense growth compared to previous period"""
    previous_start = '2022-12-01 00:00:00'
    previous_end = '2022-12-31 00:00:00'

    total_expenses = query_total_expenses(start_date, end_date)
    previous_period_expenses = query_total_expenses(previous_start, previous_end)
    
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






    


   

