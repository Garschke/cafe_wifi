from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_bootstrap import Bootstrap5
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# create the app
app = Flask(__name__)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URI')
# Create the extension
db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)
# --------- BELOW ADDED FOR BOOTSTRAP 5 ---------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)


# CREATE TABLE
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=False)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


def current_year():
    date = f"{datetime.now().strftime('%Y')}"
    print(date)
    return date


@app.route('/')
def home():
    return render_template("index.html", year=current_year())


@app.route('/cafes')
def cafes():
    with app.app_context():
        # READ ALL RECORDS
        # Construct a query to select from the database.
        # Returns the rows in the database
        result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
        # Use .scalars() to get the elements rather than entire rows
        # from the database
        all_cafes = result.scalars().all()
    return render_template("cafes.html", cafes=all_cafes, year=current_year())


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        print(request.form)  # Debugging: Print form data
        new_cafe = Cafe(
            name=request.form["name"],
            map_url=request.form["map_url"],
            img_url=request.form["img_url"],
            location=request.form["location"],
            has_sockets=bool(request.form["has_sockets"] == 'on'),
            has_toilet=bool(request.form["has_toilet"] == 'on'),
            has_wifi=bool(request.form["has_wifi"] == 'on'),
            can_take_calls=bool(request.form["can_take_calls"] == 'on'),
            seats=request.form["seats"],
            coffee_price=request.form["coffee_price"]
        )
        if Cafe.query.filter_by(name=new_cafe.name).first():
            flash(f"{new_cafe.name} already exists, please try again!")
            return render_template('add.html', year=current_year())
        try:
            with app.app_context():
                db.session.add(new_cafe)
                db.session.commit()
                flash(f"{new_cafe.name} is added successfully!")
                return redirect(url_for('home'))
        except IntegrityError:
            flash("Failed to add the new cafe. Please try again.")
            return render_template('add.html', year=current_year())
    return render_template('add.html', year=current_year())


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # UPDATE RECORD
        cafe_id = request.form["id"]
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
        cafe_to_update.name = name=request.form["name"]
        cafe_to_update.map_url = map_url=request.form["map_url"]
        cafe_to_update.img_url = img_url=request.form["img_url"]
        cafe_to_update.location = location=request.form["location"]
        cafe_to_update.has_sockets = bool(
            request.form["has_sockets"] == 'on')
        cafe_to_update.has_toilet = bool(
            request.form["has_toilet"] == 'on')
        cafe_to_update.has_wifi = bool(
            request.form["has_wifi"] == 'on')
        cafe_to_update.can_take_calls = bool(
            request.form["can_take_calls"] == 'on')
        cafe_to_update.seats = seats=request.form["seats"]
        cafe_to_update.coffee_price = coffee_price=request.form["coffee_price"]
        db.session.commit()
        return redirect(url_for('home'))
    cafe_id = request.args.get('id')
    cafe_selected = db.get_or_404(Cafe, cafe_id)
    return render_template(
        "edit_cafe.html", cafe=cafe_selected, year=current_year())


@app.route("/delete")
def delete():
    # DELETE RECORD
    cafe_id = request.args.get('id')
    # DELETE A RECORD BY ID
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
