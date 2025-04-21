from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, url

# create the app
app = Flask(__name__)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
# Create the extension
db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)
# --------- BELOW ADDED FOR BOOTSTRAP 5 ---------
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
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


# ------------- FORM VALIDATION -------------
class CafeForm(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('Map URL', validators=[DataRequired(), url()])
    img_url = StringField('Image URL', validators=[DataRequired(), url()])
    location = StringField('Location', validators=[DataRequired()])
    has_sockets = SelectField('Has sockets?',
                              choices=[(1, '✔'), (0, '✘')],
                              validators=[DataRequired()])
    has_toilet = SelectField('Has toilet?',
                             choices=[(1, '✔'), (0, '✘')],
                             validators=[DataRequired()])
    has_wifi = SelectField('Has wifi?',
                           choices=[(1, '✔'), (0, '✘')],
                           validators=[DataRequired()])
    can_take_calls = SelectField('Can take calls?',
                                 choices=[(1, '✔'), (0, '✘')],
                                 validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    coffee_price = StringField('Coffee price', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    return render_template("index.html")


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
    return render_template("cafes.html", cafes=all_cafes)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        print("True")
        new_cafe = Cafe(
            name=request.form["name"],
            map_url=request.form["map_url"],
            img_url=request.form["img_url"],
            location=request.form["location"],
            has_sockets=bool(int(request.form["has_sockets"])),
            has_toilet=bool(int(request.form["has_toilet"])),
            has_wifi=bool(int(request.form["has_wifi"])),
            can_take_calls=bool(int(request.form["can_take_calls"])),
            seats=request.form["seats"],
            coffee_price=request.form["coffee_price"]
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html")


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
        cafe_to_update.has_sockets = bool(int(request.form["has_sockets"]))
        cafe_to_update.has_toilet = bool(int(request.form["has_toilet"]))
        cafe_to_update.has_wifi = bool(int(request.form["has_wifi"]))
        cafe_to_update.can_take_calls = bool(int(request.form["can_take_calls"]))
        cafe_to_update.seats = seats=request.form["seats"]
        cafe_to_update.coffee_price = coffee_price=request.form["coffee_price"]
        db.session.commit()
        return redirect(url_for('home'))
    cafe_id = request.args.get('id')
    cafe_selected = db.get_or_404(Cafe, cafe_id)
    return render_template("edit_cafe.html", cafe=cafe_selected)


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
