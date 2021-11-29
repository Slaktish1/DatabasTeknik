from typing import Type
from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField, EmailField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms.widgets import NumberInput

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
   password = PasswordField('password', validators=[InputRequired(), Length(min=8 , max=80)])

class AccountForm(FlaskForm):
   Street = StringField('Street', validators=[InputRequired(), Length(max=50)])
   City = StringField('City', validators=[InputRequired(), Length(max=50)])
   Country = StringField('Country', validators=[InputRequired(), Length(max=50)])

class shoppingcartForm(FlaskForm):
   quantity = IntegerField('', validators=[InputRequired()], widget=NumberInput(), default=1)

class addingForm(FlaskForm):
   productName = StringField('productName', validators=[InputRequired(), Length(max=50)])
   productPrice = StringField('productPrice', validators=[InputRequired(), Length(max=50)])
   productImg = StringField('productImg', validators=[InputRequired(), Length(max=50)])
   productDesc = StringField('productDesc', validators=[InputRequired(), Length(max=50)])
   productQty = IntegerField('productQty', validators=[InputRequired()], widget=NumberInput(), default=1)

class UserInformation(UserMixin, db.Model):
   id = db.Column(db.Integer, primary_key=True, unique=True)
   dbuserType = db.Column(db.String(120), nullable=False)
   dbname = db.Column(db.String(80), unique=True, nullable=False)
   dbStreet = db.Column(db.String(120), nullable=True)
   dbCity = db.Column(db.String(120), nullable=True)
   dbCountry = db.Column(db.String(120), nullable=True)
   dbEmail = db.Column(db.String(120), nullable=False)
   dbPw = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(64), index = True)
    product_price = db.Column(db.Float, index=True)
    product_img = db.Column(db.String(200), index=True)
    product_description = db.Column(db.String(200), index=True)
    product_qty = db.Column(db.Integer, index=True)
    
class ActiveOrder(db.Model):
   oID = db.Column(db.Integer, primary_key=True, unique=True)
   UserID = db.Column(db.Integer, nullable=False)
   Status = db.Column(db.String(120), nullable=True, default='Ordered')

class prodInOrder(db.Model):
   Orderid = db.Column(db.Integer, primary_key=True,unique=False)
   productID = db.Column(db.Integer, nullable=False)
   Quantity = db.Column(db.Integer, nullable=False)
   
class Cart(db.Model):
   cartUID = db.Column(db.Integer, primary_key=False,unique=False)
   cartPID = db.Column(db.Integer, nullable=False)
   cartQuantity = db.Column(db.Integer, nullable=False)
   cartID = db.Column(db.Integer, primary_key=True,unique=False)

@login_manager.user_loader
def load_user(user_id):
   return UserInformation.query.get(int(user_id))

@app.route('/')
def HomePage():
   products = Product.query.all()
   return render_template('HomePage.html', products = products)

@app.route('/About')
def About():
   return render_template('About.html')

@app.route('/Contact')
def Contact():
   return render_template('Contact.html')

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
   
   form = LoginForm()

   try:
      if session['username']:
         user = UserInformation.query.filter_by(id=session['username']).first()
         if user.dbuserType == 'admin':
            return redirect(url_for('address'))
         if user.dbuserType == 'customer':
            return redirect(url_for('address'))
      
   except KeyError:
      if form.validate_on_submit():
         user = UserInformation.query.filter_by(dbname=form.username.data).first()
         if user:
            if check_password_hash(user.dbPw, form.password.data):
               login_user(user, remember=form.remember.data)
               session['username'] = user.id
               return redirect(url_for('HomePage'))
      
      return render_template('login.html', form=form)
   

@app.route('/address', methods=['GET', 'POST'])
@login_required
def address():
   form = AccountForm()
   products = []
   quantity = []
   OrderProd = []
   userId = session["username"]
   Order = ActiveOrder.query.filter_by(UserID=userId).all()
   user = UserInformation.query.filter_by(id=userId).first()
   if Order == None:
      

      if form.validate_on_submit():
         user.dbStreet = form.Street.data
         user.dbCity = form.City.data
         user.dbCountry = form.Country.data
         db.session.commit()

      return render_template('address.html', form=form, Street=user.dbStreet, City = user.dbCity, Country = user.dbCountry, Name = user.dbname, UT = user.dbuserType)
   else:
      if user.dbuserType == 'customer':
         for items in Order:
            OrderProd = OrderProd + prodInOrder.query.filter_by(Orderid=items.oID).all()
            print('CUSTOMER ORDER!!!!!',OrderProd)
         for prod in OrderProd:
            products = products + Product.query.filter_by(id=prod.productID).all()
         
         for quan in OrderProd:
            quantity = quantity + [quan.Quantity]
            
         if form.validate_on_submit():
            user.dbStreet = form.Street.data
            user.dbCity = form.City.data
            user.dbCountry = form.Country.data
            db.session.commit()
         return render_template('address.html', form=form, Street=user.dbStreet, City = user.dbCity, Country = user.dbCountry, Name = user.dbname, products = products, quantity = quantity, Order = Order, UT = user.dbuserType )
      
      elif user.dbuserType == 'admin':
         Order = ActiveOrder.query.all()
         OrderProd = prodInOrder.query.all()
         print('ADMIN ORDER!!!!!',OrderProd)
         for prod in OrderProd:
            products = products + Product.query.filter_by(id=prod.productID).all()
         
         for quan in OrderProd:
            quantity = quantity + [quan.Quantity]
            
         if form.validate_on_submit():
            user.dbStreet = form.Street.data
            user.dbCity = form.City.data
            user.dbCountry = form.Country.data
            db.session.commit()
         return render_template('address.html', form=form, Street=user.dbStreet, City = user.dbCity, Country = user.dbCountry, Name = user.dbname, products = products, quantity = quantity, Order = Order, UT = user.dbuserType )
   

@app.route('/logout')
@login_required
def logout():
   session.pop("username", None)
   session.pop("cart", None)
   logout_user()
   return redirect(url_for('HomePage'))

@app.route('/products')
def products():
   products = Product.query.all()
   return render_template("products.html",title="Products",products=products)

@app.route('/product')
def get_product():
   pID = request.args.get('pID')
   print(type(pID))
   prod_id = Product.query.filter_by(id=int(pID)).first()
   return render_template("product_page.html",prod_id=prod_id,product_qty=prod_id.product_qty)

@app.route('/order', methods=['GET', 'POST'])
def order():
   testID = int(session['username'])
   testUser = UserInformation.query.filter_by(id=testID).first()
   cartItems = Cart.query.filter_by(cartUID=testID).all()
   
   if testUser.dbStreet == None or testUser.dbCity == None or testUser.dbCountry == None:
      flash('Please submit your shipping information!')
      return redirect(url_for('address'))

   else:
      for item in cartItems:
         QP = Product.query.filter_by(id=item.cartPID).first()
         if QP.product_qty >= item.cartQuantity:
            new_order = ActiveOrder(UserID= session['username'])
            db.session.add(new_order)
            db.session.commit()
            newQTY = QP.product_qty - item.cartQuantity
            QP.product_qty = newQTY
            new_prodInOrder = prodInOrder(Orderid = new_order.oID, productID = QP.id, Quantity = item.cartQuantity)
            db.session.add(new_prodInOrder)
            db.session.commit()
         elif QP.product_qty == 0:
            flash('The item is out of stock.')
            return redirect(url_for('shoppingCart'))
         elif QP.product_qty < item.cartQuantity:
            flash('The specified quantity for the item is not available. Not enough stock.')
            return redirect(url_for('shoppingCart'))
         
      Cart.query.filter_by(cartUID = testID).delete()
      db.session.commit()
   return 'Order recived!'

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def shoppingCart():
   form = shoppingcartForm()
   products = []

   localcartUID = int(session['username'])
   cartITEMS = Cart.query.filter_by(cartUID=localcartUID).all()
   if cartITEMS != False:
      for items in cartITEMS:
         print("ITEMS: ", items)
         products.append(Product.query.filter_by(id = items.cartPID).first())
      print("PROD: ", products)

   return render_template("shoppingcart.html", products=products, carts=cartITEMS, plen = len(products), form = form)  
   



@app.route('/quick-add', methods=['GET'])
def quick_add():
       
   id = request.args.get('id', '')
   try:
      testID = int(session['username'])
   except:
      return redirect(url_for('login'))
   print("TESTTESTTESTTEST",testID)
   cartItems = Cart.query.filter_by(cartUID=testID).all()
   
   if len(cartItems) != 0:
      for items in cartItems:
         product = Product.query.filter_by(id=items.cartPID).first()
         if items.cartPID  == int(id):
            items.cartQuantity = items.cartQuantity + 1
            db.session.commit()
            return redirect(url_for('shoppingCart'))
         else:
            continue
   new_prodInCart = Cart(cartUID = testID, cartPID = id, cartQuantity = 1)
   db.session.add(new_prodInCart)
   db.session.commit()

   return redirect(url_for('shoppingCart'))
                                             
if __name__ == '__main__':
   app.run(debug=True)


@app.route('/updatecart',methods=['GET', 'POST'])
def updatecart():
   id = request.args.get('code')
   jallaquantity = request.form['jallaquantity']
   testID = int(session['username'])
   cartItems = Cart.query.filter_by(cartUID=testID).all()
   for items in cartItems:
      if items.cartPID == int(id):
         items.cartQuantity = int(jallaquantity)
         db.session.commit()

   return redirect(url_for('shoppingCart'))

@app.route('/remove',methods=['GET'])
def remove():
   Rid = request.args.get('id', '')
   testID = int(session['username'])
   Rid = int(Rid)
   cartItems = Cart.query.filter_by(cartUID=testID).all()
   for item in cartItems:
      if Rid == item.cartPID:
         Cart.query.filter_by(cartPID=Rid).delete()
         db.session.commit()
   return redirect(url_for('shoppingCart'))

@app.route('/addProd', methods=['GET', 'POST'])
def addProd():
   form = addingForm()