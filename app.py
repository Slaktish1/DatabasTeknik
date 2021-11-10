from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:LTU2021@51.38.126.58/maindb'
db = SQLAlchemy(app)

if __name__ == '__main__':
   app.run()

class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   dbname = db.Column(db.String(80), unique=True, nullable=False)
   dbStreet = db.Column(db.String(120), nullable=False)
   dbCity = db.Column(db.String(120), nullable=False)
   dbCountry = db.Column(db.String(120), nullable=False)
   dbEmail = db.Column(db.String(120), nullable=False)
   dbPw = db.Column(db.String(120), nullable=False)

@app.route('/')
def HomePage():
   return render_template('HomePage.html')