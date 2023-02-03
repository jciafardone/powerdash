"""Models for dashboard app."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Powerdash User"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String)
    lname = db.Column(db.String)
    email = db.Column(db.String)

    clients_info = db.relationship('Client', back_populates="user_client")
    pl_records = db.relationship('ProfitLoss', back_populates="user_profit_and_loss")

    def __repr__(self):
        return f"<User id = {self.user_id}, User email = {self.email}>"


class Client(db.Model):
    """Client information; will pull from CRM API."""

    __tablename__ = "clients"

    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_crm_id = db.Column(db.String)
    client_email = db.Column(db.String)
    client_fname = db.Column(db.String)
    client_lname = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user_client = db.relationship('User', back_populates='clients_info')
    client_reservations = db.relationship('Reservation', back_populates='client_id_for_reservation')
    client_orders = db.relationship('SalesOrder', back_populates='client_id_for_sales_orders')
    
    def __repr__(self):
        return f"<Client email = {self.client_email}>"


class ProfitLoss(db.Model):
    """Profit and loss information; will pull from accounting API."""

    __tablename__ = "profit_and_loss"

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    total_revenue = db.Column(db.Float)
    total_expenses = db.Column(db.Float)
    payroll_expenses = db.Column(db.Float)
    
    user_profit_and_loss = db.relationship('User', back_populates="pl_records")

    def __repr__(self):
        return f"<Record id = {self.record_id}, user_id = {self.user_id}>"
    

class Reservation(db.Model):
    """Individual reservations for classes; will pull from CRM API."""

    __tablename__ = "reservation_data"

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    class_date = db.Column(db.DateTime)
    class_name = db.Column(db.String)
    class_instructor = db.Column(db.String)
    # total_slots = db.Column(db.Integer) this needs to be removed and calculated elsewhere
    # slots_attended = db.Column(db.Integer) this needs to be removed and calculated elsewhere
    #user_id needs to be added?

    client_id_for_reservation = db.relationship('Client', back_populates='client_reservations')

    def __repr__(self):
        return f"<Client id = {self.client_id}, Class name = {self.class_name}>"


class SalesOrder(db.Model):
    """Records for individual sales orders; will pull from CRM API."""

    __tablename__ = "sales_orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    item_name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    gross_sale = db.Column(db.Float)
    discount = db.Column(db.Float)
    net_sale = db.Column(db.Float)

    client_id_for_sales_orders = db.relationship('Client', back_populates='client_orders')

    def __repr__(self):
        return f"<Order id = {self.order_id}, Item name = {self.item_name}>"


def connect_to_db(flask_app, db_uri="postgresql:///powerdash", echo=True):
    """Copied from Hackbright Movie Ratings Lab. Connect to database."""

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    """Copied from Hackbright Movie Ratings Lab."""

    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)


