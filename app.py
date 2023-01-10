from flask import Flask,  render_template , request , flash , redirect , url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_migrate import Migrate
from webforms import loginForm, registerForm
from datetime import datetime


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres:hari1412@localhost/nevarSystems'
app.config['SECRET_KEY'] = "SECRET KEY"


db = SQLAlchemy(app)
migrate = Migrate(app , db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model , UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False , unique=True)
    password = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %%r>' % self.name


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register' , methods=('GET' , 'POST'))
def register():

    email = None
    password = None
    RegisterForm = registerForm()

    if RegisterForm.validate_on_submit():

        user = User.query.filter_by(email=RegisterForm.email.data).first()

        if user is None:
            
            email = RegisterForm.email.data
            psw = RegisterForm.password.data

            hashed_pw = generate_password_hash(psw  , "sha256")
            
            user = User(email=email , password=hashed_pw)
            db.session.add(user)
            db.session.commit()
        
        RegisterForm.email.data = ''
        RegisterForm.password.data = ''

    return render_template("register.html" , RegisterForm=RegisterForm )

@app.route('/logout' , methods=('GET' , 'POST'))
@login_required
def logout():
    logout_user()
    flash(" Loged Out Succesfully !! ")
    return redirect(url_for('login'))



@app.route('/login' , methods=('GET' , 'POST'))
def login():

    email = None
    password = None
    LoginForm = loginForm()

    if LoginForm.validate_on_submit():

        email = LoginForm.email.data
        password = LoginForm.password.data

        LoginForm.email.data = ''
        LoginForm.password.data = ''

        user = User.query.filter_by(email=email).first()

        if user is not None:
            
            if check_password_hash(user.password, password):
                
                login_user(user)
                flash(" Loged in Succesfully !! ")
                return redirect(url_for('dashboard'))
            
            else:
                flash("Wrong password !! ")
        
        else:
            flash(" Email doesn't exist !! ")
        

    return render_template("login.html" , LoginForm=LoginForm)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/users')
def users():

    users = User.query.order_by(User.date_added).all()

    return render_template('users.html', users=users)


@app.route('/update/<int:id>' , methods=('GET','POST'))
def update(id):

    RegisterForm = registerForm()
    name_to_update = User.query.get_or_404(id)

    if RegisterForm.validate_on_submit():

        name_to_update.email =  RegisterForm.email.data
        hashed_pw = generate_password_hash(RegisterForm.password.data  , "sha256")

        name_to_update.password = hashed_pw

        RegisterForm.email.data = ''
        RegisterForm.password.data = ''

        try:

            db.session.commit()
            flash("User updated successfully")

            return redirect(url_for('users'))

        except:
            
            flash(" ERROR !!! ")
            return render_template('users.html',RegisterForm=RegisterForm, user=name_to_update)

    else:
        return render_template('update.html',RegisterForm=RegisterForm, user=name_to_update)


@app.route('/delete/<int:id>' , methods=('GET','POST'))
def delete(id):

    user_to_delete = User.query.get_or_404(id)
    print("USER TO DELETE: " , user_to_delete.email , user_to_delete.id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted successfully")
        return redirect(url_for('users'))

    except:
        return redirect(url_for('users'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)