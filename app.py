from flask import Flask , render_template,make_response,jsonify,request,url_for , flash , session , redirect
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from wtforms.fields.html5 import EmailField

from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:0184738437@localhost:5432/flaskapp";
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
# print("a")

class User(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,

    )
    name = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )  
    email = db.Column(
        db.String(120),
        unique=False,
        nullable=False
    )  
    password = db.Column(
        db.String(120),
        unique=False,
        nullable=False
    )  
    age=db.Column(db.Integer)

    def __init__(self,name,age,password,email):
        self.name = name
        self.email = email
        self.age=age
        self.password=password

db.create_all()
app.config['SECRET_KEY'] = "Yossef"

class SimpleForm(FlaskForm):
    name = StringField("Enter Your Name: ",description="Enter Your Name")
    age = StringField("Enter Your Age: ",description="Enter Your Age")
    email=EmailField("Enter Your Email",description="Enter Your Email..")
    submit = SubmitField("Submit")
    delete = SubmitField("Delete")
    password=PasswordField("Enter Your Password :",description="Password..")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not "name" in session:
        return redirect(url_for('index'))
    if session["name"]:
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie(app.session_cookie_name, expires=0)
        return resp


@app.route('/users', methods=['GET', 'POST'])
def users():
    if not "name" in session:
        return redirect(url_for("login"))
    all_users = User.query.all()
    return render_template("users.html" , all_users=all_users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if "name" in session:
        return redirect(url_for("home"))
    form = SimpleForm()

    if form.validate_on_submit():
        if not ( form.email.data and form.password.data):
            flash(f"Please Fill All The Fields")
            return redirect(url_for("login"))
        else:
            emailFiltered = User.query.filter_by(email=form.email.data).first()
            if not emailFiltered:
                flash("Wrong Email Or Password")
                return redirect(url_for("login"))

            if emailFiltered.password == form.password.data:
                session["name"] = emailFiltered.name;
                return redirect(url_for("login"))

    return render_template("login.html" , form = form)

    




@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    if not "name" in session:
        return redirect(url_for("login"))
    form = SimpleForm()
    user = User.query.get(user_id)
    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(user)
            db.session.commit()
            if user.name == session["name"]:
                resp = make_response(redirect(url_for('login')))
                resp.set_cookie(app.session_cookie_name, expires=0)
                return resp
            return redirect("users")
        user.name=form.name.data;
        user.age=form.age.data;
        user.email=form.email.data;
        user.password=form.password.data;
        db.session.commit()
        return redirect(url_for("users"))

    return render_template("edit_user.html",form=form,user=user)

@app.route('/signup', methods=['GET', 'POST'])
def index():
    try:
        form = SimpleForm()
        if form.validate_on_submit():
            if not (form.name.data and form.age.data and form.password.data):
                flash(f"Please Fill All The Fields")
                return redirect(url_for('index'))

            try:
                age =int(form.age.data)
            except:
                flash(f"Enter Your Valide Age")
                return redirect(url_for('index'))        
        
            else:
                emailFiltered = User.query.filter_by(email=form.email.data).first()
                if emailFiltered:
                    flash(f"{form.email.data} is exist !!")
                    return redirect(url_for('index'))        

                flash(f"Welcome back {form.name.data}")
                    # def __init__(self,name,age,password,email):
    
                new_user = User(form.name.data,age,form.password.data,form.email.data)
                db.session.add(new_user)
                db.session.commit()
                session["name"] = form.name.data
            # resp.set_cookie('email',"name")  
                return redirect('/users')
    except:
      print('An exception occurred')
 
    return render_template("index.html" , form = form)




@app.errorhandler(404)
def page_not_found(e):
    return render_template("thanks.html" ),404

app.run(debug=True)


# export FLASK_ENV=development
# flask run

# url_for("view") || url_for('static' , filename='yossef.jpg')
# session : just start it and the it will be in the cookies always
# FlaskForms: we make a class from it then define our wtforms instances inputs 
# and then make an instance from the class i the view and use form.validate_on_submit() function to detect wheather the user submit it or not
# app.config['SECRET_KEY'] = "Yossef" for the forms
# errorhandling: @app.errorhandler(404)
# def page_not_found(e):
#     return render_template("thanks.html" ),404
