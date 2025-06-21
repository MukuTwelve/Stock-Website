from flask import Blueprint, render_template, redirect, url_for
from .forms import SignupForm, LoginForm
from .models import User
from . import db, bcrypt
from flask_login import login_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    global user
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user:
            global user_id
            user_id = int(user.id)
            print(user.password)  
            #print(datetime.date.today)
            print(form.password.data)
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('routes.index'))
            else:
                return render_template('login.html', form=form, error='Invalid password')
    return render_template('login.html', form=form)

            

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form2 = SignupForm()
    if form2.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form2.password.data).decode('utf-8')
        new_user = User(username=form2.username.data, password=hashed_password)
        print(new_user)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html', form2=form2)