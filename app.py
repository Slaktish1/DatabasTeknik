import re
from typing import Type
from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import send_file
from wtforms import StringField, PasswordField, BooleanField, EmailField, FloatField, RadioField,TextAreaField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms.widgets import NumberInput, TextArea

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
   productPrice = IntegerField('productPrice', validators=[InputRequired()], widget=NumberInput(), default=1000)
   productImg = StringField('productImg', validators=[InputRequired(), Length(max=50)])
   productDesc = StringField('productDesc', validators=[InputRequired(), Length(max=50)])
   productQty = IntegerField('productQty', validators=[InputRequired()], widget=NumberInput(), default=1)
   productDesc = StringField('productDesc', validators=[InputRequired(), Length(max=50)])
   productQty = IntegerField('productQty', validators=[InputRequired()],)
   productTag = StringField('productTag', validators=[InputRequired(), Length(max=64)])
   productCategory = StringField('productCategory', validators=[InputRequired(), Length(max=64)])
class supportForm(FlaskForm):
   title = StringField('Title', validators=[InputRequired(), Length(min=4 , max=40)])
   description = StringField('Description', validators=[InputRequired()], widget=TextArea())
   category = RadioField('Category',validators =[InputRequired()], choices=[('Help'), ('Return')], default='1')
   oID = RadioField('oID',validators =[InputRequired('Choose a order')], coerce=int)

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
    product_tag = db.Column(db.String(64), index = True)
    product_category = db.Column(db.String(64), index = True)
    
class ActiveOrder(db.Model):
   oID = db.Column(db.Integer, primary_key=True, unique=True)
   Total = db.Column(db.String(120), nullable=False)
   UserID = db.Column(db.Integer, nullable=False)
   Status = db.Column(db.String(120), nullable=True, default='Ordered')

class prodInOrder(db.Model):
   IDK_ID = db.Column(db.Integer, primary_key=True, unique=True) 
   Orderid = db.Column(db.Integer, primary_key=False,unique=False)
   productID = db.Column(db.Integer, nullable=False)
   Quantity = db.Column(db.Integer, nullable=False)
   
class Cart(db.Model):
   cartUID = db.Column(db.Integer, primary_key=False,unique=False)
   cartPID = db.Column(db.Integer, nullable=False)
   cartQuantity = db.Column(db.Integer, nullable=False)
   cartID = db.Column(db.Integer, primary_key=True,unique=False)

class Support(db.Model):
   ticketID = db.Column(db.Integer, primary_key=True,unique=True)
   ticketUID = db.Column(db.Integer, nullable=False)
   ticketOID = db.Column(db.Integer, nullable=False)
   ticketTitle = db.Column(db.String(120), nullable=False)
   ticketDesc = db.Column(db.String(120), nullable=False)
   ticketCategory = db.Column(db.String(120), nullable=False)

class ProductReviews(db.Model):
   reviewID = db.Column(db.Integer, primary_key=True,unique=True)
   product_id = db.Column(db.Integer, nullable=False)
   user_id = db.Column(db.Integer, nullable=False)
   review_text = db.Column(db.String(4000), nullable=False)
   Rating = db.Column(db.Integer, nullable=False)

class ReviewForm(FlaskForm):
   Review = StringField('What do you think of the product?', validators=[InputRequired()], widget=TextArea())
   ReviewRating = RadioField('What would you rate the product?', choices = ["1","2","3","4","5"], validators = [InputRequired()])

@login_manager.user_loader
def load_user(user_id):
   return UserInformation.query.get(int(user_id))



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

@app.route('/products', methods=['GET', 'POST'])
def products():
   catINF = request.args.get('cat')
   if catINF == 'Sports' or catINF == 'Alpine' or catINF == 'Clothes':
      products = Product.query.filter_by(product_category=catINF).all()
   else:
      products = Product.query.all()
   return render_template("products.html",title="Products",products=products)

@app.route('/product', methods=['GET', 'POST'])
def get_product():
   users = []
   visited_users = []
   pID = request.args.get('pID')
   prod_id = Product.query.filter_by(id=int(pID)).first()
   customerReviews = ProductReviews.query.filter_by(product_id=pID).all()
   for items in customerReviews:  
      if items.user_id not in visited_users:
         users = users + [UserInformation.query.filter_by(id=items.user_id).first()]
      if items.user_id not in visited_users:
             visited_users =  visited_users + [items.user_id]
   return render_template("product_page.html",prod_id=prod_id,product_qty=prod_id.product_qty, customerReviews = customerReviews, users = users )

@app.route('/review', methods=['GET', 'POST'])
def review():
   userID = int(session['username'])
   form = ReviewForm()
   pID = request.args.get('pID')
   pID2 = request.form.get('pID2')
   print(pID2)
   if form.validate_on_submit():
      print("VALID!!! PRODUCT REVIEW")
      new_review = ProductReviews(product_id = int(pID2), user_id = userID, review_text = str(form.Review.data), Rating = int(form.ReviewRating.data))
      db.session.add(new_review)
      db.session.commit()
      return redirect(url_for('address'))
   prod_id = Product.query.filter_by(id=int(pID)).first()
   return render_template("review.html", form = form, prod_id = prod_id)

@app.route('/order', methods=['GET', 'POST'])
def order():
   testID = int(session['username'])
   total = request.args.get('Total')
   testUser = UserInformation.query.filter_by(id=testID).first()
   cartItems = Cart.query.filter_by(cartUID=testID).all()
   look = 0
   if testUser.dbStreet == None or testUser.dbCity == None or testUser.dbCountry == None:
      flash('Please submit your shipping information!')
      return redirect(url_for('address'))

   else:
      for item in cartItems:
         QP = Product.query.filter_by(id=item.cartPID).first()
         if QP.product_qty >= item.cartQuantity:
            if look == 0:    
               new_order = ActiveOrder(UserID= session['username'], Total = total)
               db.session.add(new_order)
               db.session.commit()
               look = 1
            if look == 1:
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
   if form.validate_on_submit():
      if Product.query.filter_by(product_name=form.productName.data).first():
         print('IT exist')
         prod = Product.query.filter_by(product_name=form.productName.data).first()
         prod.product_price = float(form.productPrice.data)
         prod.product_img = form.productImg.data
         prod.product_description = form.productDesc.data
         prod.product_qty = form.productQty.data
         db.session.commit()
         return redirect(url_for('address'))
      else:
         print('Does not exist')
         new_prod = Product(product_name = form.productName.data, product_price = float(form.productPrice.data), product_img = form.productImg.data, product_description = form.productDesc.data , product_qty = form.productQty.data)
         db.session.add(new_prod)
         db.session.commit()
         return redirect(url_for('address'))
   return render_template("addProd.html", form = form)

@app.route('/seeOrders', methods=['GET', 'POST'])
def seeOrders():
   oID = request.args.get('oID', '')
   oID = int(oID)
   orders = prodInOrder.query.filter_by(Orderid=oID).all()
   total = ActiveOrder.query.filter_by(oID=oID).first()
   total = total.Total
   print('LOOOOOOKKKKKK',orders)
   prods =  Product.query.all()
   return render_template("Orders.html", orders = orders, prods = prods, oID = oID,Total = total)

@app.route('/support', methods=['GET', 'POST'])
def support():
   form = supportForm()
   testID = int(session['username'])
   form.oID.choices = [(items.oID) for items in ActiveOrder.query.filter_by(UserID=testID).all()]
   if form.validate_on_submit():
      new_ticket = Support(ticketUID = testID, ticketOID = int(form.oID.data), ticketTitle = str(form.title.data), ticketDesc = str(form.description.data) , ticketCategory = str(form.category.data))
      db.session.add(new_ticket)
      db.session.commit()
      return redirect(url_for('address'))
   return render_template("Support.html", form = form)

@app.route('/search', methods=['GET', 'POST'])
def search():
   sTerm = request.args.get('sTerm')
   prods =  Product.query.all()
   name = [items for items in prods if str(sTerm) in items.product_name]  
   tag = [items for items in prods if str(sTerm) in items.product_tag] 
   new = set(tag) - set(name)
   res1 = name + list(new)
   desc = [items for items in prods if str(sTerm) in items.product_description]
   new2 = set(desc) - set(res1)
   results = res1 + list(new2)
   return render_template("Search.html", results = results, Lresults = len(results))

@app.route('/')
def HomePage():
   return render_template('HomePage.html')