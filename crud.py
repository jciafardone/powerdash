from model import User, Client, ProfitLoss, Reservation, SalesOrder

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
