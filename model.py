"""Models for dashboard app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Powerdash User"""

    __tablename__ = 'users'

    #Define table columns
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String)
    password = db.Column(db.String)

    #Define relationships to other tables
    clients_for_user_id = db.relationship('Client', back_populates='user_id_for_clients')
    # pl_records_for_user_id = db.relationship('ProfitLoss', back_populates='user_id_for_profit_and_loss_records')
    reservations_for_user_id = db.relationship('Reservation', back_populates='user_id_for_reservations')

    def __repr__(self):
        return f"<User id = {self.user_id}, User email = {self.email}>"


class Client(db.Model):
    """Client information from Powerdash users' business. Pulled from CRM API or CSV Upload."""

    __tablename__ = 'clients'

    #Define table columns
    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_crm_id = db.Column(db.String)
    client_email = db.Column(db.String)
    client_fname = db.Column(db.String)
    client_lname = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    #Define relationships to other tables
    user_id_for_clients = db.relationship('User', back_populates='clients_for_user_id')
    reservations_for_client_id = db.relationship('Reservation', back_populates='client_id_for_reservations')
    sales_orders_for_client_id = db.relationship('SalesOrder', back_populates='client_id_for_sales_orders')
    
    def __repr__(self):
        return f"<Client email = {self.client_email}>"


class ProfitLoss(db.Model):
    """Profit and loss information for Powerdash users' business. Pulled from Accounting API or CSV Upload."""

    __tablename__ = 'profit_and_loss'

    #Define table columns
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    total_revenue = db.Column(db.Float)
    total_expenses = db.Column(db.Float)
    payroll_expenses = db.Column(db.Float)
    
    #Define relationships to other tables
    # user_id_for_profit_and_loss_records = db.relationship('User', back_populates='pl_records_for_user_id')

    def __repr__(self):
        return f"<Record id = {self.record_id}, user_id = {self.user_id}>"
    

class Reservation(db.Model):
    """Records for each reservation made by a Powerdash users' client at the business. Pulled from CRM API or CSV Upload ."""

    __tablename__ = 'reservation_data'

    #Define table columns
    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    client_crm_id = db.Column(db.String)
    class_date = db.Column(db.DateTime)
    class_name = db.Column(db.String)
    class_instructor = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    #Define relationships to other tables
    client_id_for_reservations = db.relationship('Client', back_populates='reservations_for_client_id')
    user_id_for_reservations = db.relationship('User', back_populates='reservations_for_user_id')

    def __repr__(self):
        return f"<Client id = {self.client_id}, Class name = {self.class_name}>"


class SalesOrder(db.Model):
    """Records for individual sales orders for Powerdash users' business. Pulled from CRM API."""

    __tablename__ = 'sales_orders'

    #Define table columns
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    item_name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    gross_sale = db.Column(db.Float)
    discount = db.Column(db.Float)
    net_sale = db.Column(db.Float)

    #Define relationships to other tables
    client_id_for_sales_orders = db.relationship('Client', back_populates='sales_orders_for_client_id')

    def __repr__(self):
        return f"<Order ID = {self.order_id}, Item name = {self.item_name}>"


def connect_to_db(flask_app, db_uri="postgresql:///powerdash", echo=True):
    """Connect to database. Referenced from Hackbright lab code."""

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    """Referenced from Hackbright lab code."""

    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app, echo=False)


