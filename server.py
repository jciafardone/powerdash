from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db, User, Client, ProfitLoss, Reservation, SalesOrder

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    return render_template("index.html")


# can define routes and add pass so that you can map out where everything will go




if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)