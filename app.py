from flask import Flask, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField, EmailField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '\x13\xb2\xe4E\x0e\x03\x9da\x98\x8dg k\xa5\xa3\n\xf5!H\x08n\xc9\xabl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:LTU2021@51.38.126.58/maindb'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view ='login'

class LoginForm(FlaskForm):
   username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
   password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
   remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
   email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
   username = StringField('username', validators=[InputRequired(), Length(min=4 , max=15)])
   password = StringField('password', validators=[InputRequired(), Length(min=8 , max=80)])

class AccountForm(FlaskForm):
   Street = StringField('Street', validators=[InputRequired(), Length(max=50)])
   City = StringField('City', validators=[InputRequired(), Length(max=50)])
   Country = StringField('Country', validators=[InputRequired(), Length(max=50)])

class UserInformation(UserMixin, db.Model):
   id = db.Column(db.Integer, primary_key=True, unique=True)
   dbuserType = db.Column(db.String(120), nullable=False)
   dbname = db.Column(db.String(80), unique=True, nullable=False)
   dbStreet = db.Column(db.String(120), nullable=True)
   dbCity = db.Column(db.String(120), nullable=True)
   dbCountry = db.Column(db.String(120), nullable=True)
   dbEmail = db.Column(db.String(120), nullable=False)
   dbPw = db.Column(db.String(120), nullable=False)

class ProductAsset(db.Model):
   id = db.Column(db.Integer, primary_key=True, unique=True)
   prodName = db.Column(db.String(80), unique=True, nullable=False)
   prodPrice = db.Column(db.Float, unique=False, nullable=False)
   prodImage = db.Column(db.LargeBinary, unique=False, nullable=False)
   prodColor = db.Column(db.String(120), unique=False, nullable=False)

class ActiveOrder(db.Model):
   Productid = db.Column(db.Integer, primary_key=True, unique=True)
   Orderid = db.Column(db.Integer, primary_key=True, unique=True)
   dbname = db.Column(db.String(80), unique=False, nullable=False)
   dbLastname = db.Column(db.String(80), unique=False, nullable=False)
   dbStreet = db.Column(db.String(120), nullable=False)
   dbCity = db.Column(db.String(120), nullable=False)
   dbCountry = db.Column(db.String(120), nullable=False)
   dbUserID = db.Column(db.String(120), nullable=True)

@login_manager.user_loader
def load_user(user_id):
   return UserInformation.query.get(int(user_id))

@app.route('/')
def HomePage():
   return render_template('HomePage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
   form = RegisterForm()
   if form.validate_on_submit():
      hashed_PW = generate_password_hash(form.password.data, method='sha256')
      new_user = UserInformation(dbuserType = 'customer', dbname=form.username.data, dbEmail=form.email.data, dbPw=hashed_PW)
      db.session.add(new_user)
      db.session.commit()
   return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
   if(session["username"]):
      return redirect(url_for('address'))
   
   form = LoginForm()

   if form.validate_on_submit():
      user = UserInformation.query.filter_by(dbname=form.username.data).first()
      if user:
         if check_password_hash(user.dbPw, form.password.data):
            login_user(user, remember=form.remember.data)
            session['username'] = user.id
            return redirect(url_for('HomePage'))

      return '<h1> Error: Account with these credentials does not exist </h1>'
   return render_template('login.html', form=form)

@app.route('/address', methods=['GET', 'POST'])
@login_required
def address():
   form = AccountForm()

   userId = session["username"]
   user = UserInformation.query.filter_by(dbname=userId).first()
   
   if form.validate_on_submit():
      user.dbStreet = form.Street.data
      user.dbCity = form.City.data
      user.dbCountry = form.Country.data
      db.session.commit()
      'Successfully updated information'

   return render_template('address.html', form=form)


@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('HomePage'))

if __name__ == '__main__':
   app.run(debug=True)