from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user

#My DB Connection
local_server=True
app = Flask(__name__)
app.secret_key='shashidhar'

#this is for getting unique user acces
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



#Connection to backend database
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/electronics'
db=SQLAlchemy(app)

#db tabels
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Orders(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    pname=db.Column(db.String(50))
    quantity=db.Column(db.Integer)
    address=db.Column(db.String(50))
    email=db.Column(db.String(50))
    phone=db.Column(db.String(20))


# all the endpoints and the functions
@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/products")
@login_required
def products():
    return render_template('products.html')




@app.route("/orders", methods=['POST','GET'])
@login_required
def orders():
    if request.method=="POST":
        pname=request.form.get('pname')
        quantity=request.form.get('quantity')
        address=request.form.get('address')
        email=request.form.get('email')
        phone=request.form.get('phone')
        query=db.engine.execute(f"INSERT INTO `orders` (`pname`,`quantity`,`address`,`email`,`phone`) VALUES ('{pname}','{quantity}','{address}','{email}','{phone}')")
        flash("Order is placed", "info")

    return render_template('orders.html')



@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Orders.query.filter_by(pid=pid).first()
    if request.method=="POST":
        pname=request.form.get('pname')
        quantity=request.form.get('quantity')
        address=request.form.get('address')
        email=request.form.get('email')
        phone=request.form.get('phone')
        db.engine.execute(f"UPDATE `orders` SET `pname` = '{pname}', `quantity` = '{quantity}', `address` = '{address}', `email` = '{email}',`phone` = '{phone}' WHERE `orders`.`pid` = {pid}")
        flash("order is Updated","success")
        return redirect('/cart')
    
    return render_template('edit.html',posts=posts)



@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    db.engine.execute(f"DELETE FROM `orders` WHERE `orders`.`pid`={pid}")
    flash("order is delete successfully","danger")
    return redirect('/cart')



@app.route("/cart")
@login_required
def cart():
    em=current_user.email
    query=db.engine.execute(f"SELECT * FROM  `Orders` WHERE email='{em}'")
    return render_template('cart.html',query=query)



@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    query=request.form.get('search')
    pname=Orders.query.filter_by(pname=query).first()
    if pname:
        flash("Order is available","info")
    else:
        flash("Order is not available","danger")

    return render_template('index.html')
    






@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()


        if user:
            flash("Email alredy Exists","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)
        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")
        return render_template('login.html')

    return render_template('signup.html')


@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == "POST":

        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Succes","primary")
            return render_template('index.html')
        else:
            flash("Invalid user","danger")
            return render_template('login.html')

    return render_template('login.html')





@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("logout Succes","success")
    return redirect(url_for('login'))


@app.route("/test")
def test():
    try:
        Test.query.all()
        return 'MY Database is connected'
    except:
        return 'My Database is not connected'



@app.route("/home")
def home():
    return 'this is my home page'

app.run(debug=True)

username=current_user.username