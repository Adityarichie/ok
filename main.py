from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


api_key = "50937dde67fd5edf95bc06a63669b569"
api_movie_search_url = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's"
#                 " sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads"
#                 " to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def haha():
    return render_template("else.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    name = request.form["name"]
    if name == "movies":
        return render_template("index.html")
    elif name == "people":
        return render_template("People-search.html")
    elif name == "random-search":
        return render_template("images.html")
    else:
        return render_template("else.html")


@app.route("/people_search", methods=["GET", "POST"])
def people_search():

    url = f"https://google-search3.p.rapidapi.com/api/v1/search/q={request.form['fname']}+{request.form['lname']}"

    headers = {
        "X-User-Agent": "desktop",
        "X-Proxy-Location": "EU",
        "X-RapidAPI-Key": "66aa600985msh4067d6e2e6fae29p1a5c43jsnf81667e417a7",
        "X-RapidAPI-Host": "google-search3.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    data = response.json()

    name = f"NAME - {data['results'][0]['title']}"
    description = f"Description - {data['results'][0]['description']}"
    link = f"Link - {data['results'][0]['link']}"
    return f"<h3>{name},<br><br>{description} <br> <br><a href={data['results'][0]['link']}>{link}</a></h3>"



@app.route("/search-random", methods=["GET", "POST"])
def images():
    url = f"https://google-search3.p.rapidapi.com/api/v1/video/q={request.form['search-random']}"

    headers = {
    	"X-User-Agent": "desktop",
    	"X-Proxy-Location": "EU",
    	"X-RapidAPI-Key": "66aa600985msh4067d6e2e6fae29p1a5c43jsnf81667e417a7",
    	"X-RapidAPI-Host": "google-search3.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    data = response.json()

    name = f"NAME - {data['results'][0]['title']}"
    description = f"Description - {data['results'][0]['description']}"
    link = f"Link - {data['results'][0]['link']}"
    return f"<h3>{name},<br><br>{description} <br> <br><a href={data['results'][0]['link']}>{link}</a></h3>"


@app.route("/home")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        print(all_movies[i].ranking)
        print(len(all_movies) - i)

    return render_template("index.html", movies=all_movies)


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovie(FlaskForm):
    title = StringField("Move Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = AddMovie()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(api_movie_search_url, params={"api_key": api_key, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": api_key, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True, port=1581)

