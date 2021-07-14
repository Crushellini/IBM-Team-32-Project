from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email,  DataRequired, ValidationError
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IBM_DB.db' # connect to db
app.config["SECRET_KEY"] = "123"

db = SQLAlchemy(app) #enable SQLAlchemy
login_manager = LoginManager(app)
login_manager.login_view = "login" # set login route if user trys to authorize login_require page send them back to login_page and display error.

@login_manager.user_loader # requried for login_user to work
def load_user(user_id):
    return User.query.get(int(user_id)) # turn user id into int

class User(db.Model, UserMixin): # SQL ORM Table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable = False, unique=True)
    email_address = db.Column(db.String(length=50), nullable = False, unique=True)
    password_hash  = db.Column(db.String(length=60), nullable = False)


class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check): # function is called like this becuase validate_ will auto look for a field named username and will validate it
        user = User.query.filter_by(username=username_to_check.data).first() # grab username and check it
        if user: #if user is NOT None if exits
            raise ValidationError("Username already exists ! ")


    def validate_email_address(self,email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first() # look in the db if input user matches with exiting user if they match is NOT NONE and if statement executes
        if email_address:
            raise ValidationError("Email already exists ! ")


    username = StringField(label="username", validators = [Length(min=2, max=30), DataRequired() ] )
    email_address = StringField(label="email", validators = [Email(), DataRequired()] ) # validate email
    password1 = PasswordField(label='password1', validators = [Length(min=6), DataRequired()] )
    password2 = PasswordField(label='Confirm password:', validators = [EqualTo("password1"), DataRequired()] ) # validate passwords match
    submit = SubmitField(label='submit')



class LoginForm(FlaskForm):
    username = StringField(label="Username", validators = [DataRequired()] )
    password = PasswordField(label="Password", validators = [DataRequired()] )
    submit = SubmitField(label='Login')



@app.route("/")
@app.route("/home") # can handle both routes
def home():
    return render_template("home.html")


@app.route("/about/<username>") #dynamic route /about/erik
def about(username): # pass in what the user types in url

    return f'This  is the about page of {username} '



@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")



@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit(): # when user clicks submit
        userCreated =  User(username = form.username.data, email_address = form.email_address.data, password_hash = form.password1.data ) # if is valid create user based on what the user inputed in the form

        db.session.add(userCreated) # add user that was created
        db.session.commit() # commit user that was added

        login_user(userCreated) # login user


        return redirect(url_for("profile")) # once user registers redirect him/she/them to market_page

    if form.errors != {}: #  from validators erros come in dictonary if dictonary NOT empty do this
        for err_msg in form.errors.values():
            flash(f'Error: {err_msg}', category="danger") # flash errors in base.html

    return render_template('signupuser.html', form=form)



@app.route('/login', methods =["GET","POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit(): # validate once user clicks login
        attempted_user = User.query.filter_by(username = form.username.data).first() #get user input and look it up in User db
        attempted_password = User.query.filter_by(password_hash = form.password.data).first()# look up in the db if what user inputed "form.password.data" equals password_hash in the db return that password if not return NONE

        if attempted_user and attempted_password: # if what the users inputed matches the data in db log them in

            login_user(attempted_user) # login user
            flash("You are logged in")
            return redirect(url_for("profile"))

        else:  #  what the user inputed does not match what is in the db return NONE objs

            flash("Username and Password does not match !")

    return render_template('loginuser.html', form=form)



@app.route('/logout', methods =["GET","POST"])
def logout():
    logout_user()
    flash("You have been logged out!", category="info")
    return redirect(url_for("home"))