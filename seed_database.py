"""Script to seed database. Heavily copied from Hackbright Movies Ratings lab."""

import os
import csv
from random import choice, randint
from datetime import datetime

import model
import crud
import server

os.system("dropdb powerdash")
os.system("createdb powerdash")

model.connect_to_db(server.app)
model.db.create_all()


"""Seed users"""
with open("csv_data/users.csv", newline='') as csv_file:
    csvreader = csv.DictReader(csv_file, quotechar='"')

    # Create users, store them in list
    users_in_db = []
    for user in csvreader:
        email,password = (
            user["email"],
            user["password"]
        )
        # release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d")

        db_user = crud.create_user(email,password)
        users_in_db.append(db_user)

model.db.session.add_all(users_in_db)
model.db.session.commit()


"""Seed clients"""
with open("csv_data/clients.csv", newline='') as csv_file:
    csvreader = csv.DictReader(csv_file, quotechar='"')

    # Create clients, store them in list
    clients_in_db = []
    for client in csvreader:
        client_email, client_fname, client_lname, client_crm_id, user_id = (
            client["client_email"],
            client["client_fname"],
            client["client_lname"],
            client["client_crm_id"],
            client["user_id"]
        )

        db_client = crud.create_client(client_fname, client_lname, client_email, client_crm_id, user_id)
        clients_in_db.append(db_client)

model.db.session.add_all(clients_in_db)
model.db.session.commit()


"""Seed profit and loss"""
with open("csv_data/profit_loss.csv", newline='') as csv_file:
    csvreader = csv.DictReader(csv_file, quotechar='"')

    # Create profit and loss records, store them in a list
    pl_in_db = []
    for pl_record in csvreader:
        user_id, period_start, period_end, total_revenue, total_expenses, payroll_expenses = (
            pl_record["user_id"],
            pl_record["period_start"],
            pl_record["period_end"],
            pl_record["total_revenue"],
            pl_record["total_expenses"],
            pl_record["payroll_expenses"]
        )

        db_pl_record = crud.create_profit_loss(
            user_id, period_start, period_end, total_revenue, total_expenses, payroll_expenses)
        pl_in_db.append(db_pl_record)

model.db.session.add_all(pl_in_db)
model.db.session.commit()


"""Seed reservations"""
with open("csv_data/reservations.csv", newline='') as csv_file:
    csvreader = csv.DictReader(csv_file, quotechar='"')

    # Create profit and loss records, store them in a list
    reservations_in_db = []
    for reservation in csvreader:
        client_id, class_date, class_name, class_instructor,user_id = (
            reservation["client_id"],
            reservation["class_date"],
            reservation["class_name"],
            reservation["class_instructor"],
            reservation["user_id"]
        )

        db_reservation = crud.create_reservation(
            client_id, class_date, class_name, class_instructor, user_id)
        reservations_in_db.append(db_reservation)

model.db.session.add_all(reservations_in_db)
model.db.session.commit()


"""Seed sales orders"""
with open("csv_data/sales_orders.csv", newline='') as csv_file:
    csvreader = csv.DictReader(csv_file, quotechar='"')

    # Create profit and loss records, store them in a list
    orders_in_db = []
    for order in csvreader:
        order_date, client_id, item_name, quantity, gross_sale, discount, net_sale = (
            order["order_date"],
            order["client_id"],
            order["item_name"],
            order["quantity"],
            order["gross_sale"],
            order["discount"],
            order["net_sale"]
        )

        db_order = crud.create_sales_order(
            order_date, client_id, item_name, quantity, gross_sale, discount, net_sale)
        orders_in_db.append(db_order)

model.db.session.add_all(orders_in_db)
model.db.session.commit()


