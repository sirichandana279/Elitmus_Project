from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from datetime import timedelta, datetime

app = Flask(__name__)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'Elitmus_2709')

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class LoginUser(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

def add_player(UserName, EmailId, PhoneNo, Age):
    con = sqlite3.connect("Database.db")
    c = con.cursor()
    try:
        x = (UserName, EmailId, PhoneNo, Age, 0, 0, 0)
        insert = """INSERT INTO database (UserName, EmailId, PhoneNo, Age, StartTime, StopTime, Score) VALUES (?,?,?,?,?,?,?);"""
        c.execute(insert, x)
    finally:
        con.commit()
        c.close()
        con.close()
        curr_user.set_user()

def get_new_player():
    con = sqlite3.connect("Database.db")
    c = con.cursor()
    try:
        sql_select_query = "select max(UserId) from database;"
        c.execute(sql_select_query)
        record = c.fetchall()
    finally:
        con.commit()
        c.close()
        con.close()
    return record[0]

def get_player(id):
    con = sqlite3.connect("Database.db")
    c = con.cursor()
    try:
        sql_select_query = "select * from database where UserId = ?;"
        c.execute(sql_select_query, (id,))
        record = c.fetchall()
    finally:
        con.commit()
        c.close()
        con.close()
    return record[0]

def update_player():
    con = sqlite3.connect("Database.db")
    c = con.cursor()
    try:
        x = (curr_user.start, curr_user.stop, curr_user.marks, curr_user.id)
        update = "UPDATE database SET StartTime = ?, StopTime = ?, Score = ? WHERE UserId = ?;"
        c.execute(update, x)
    finally:
        con.commit()
        c.close()
        con.close()
        
def get_players_played():
    con = sqlite3.connect("Database.db")
    c = con.cursor()
    try:
        sql_select_query = "select * from database where StartTime > 0 and StopTime > 0;"
        c.execute(sql_select_query)
        record = c.fetchall()
    finally:
        con.commit()
        c.close()
        con.close()
    return record

class Curr_User:
    def __init__(self):
        self.id = self.name = self.age = self.email = self.phno = self.start = self.stop = self.marks = False
    def set_user(self):
        self.id = get_new_player()[0]
        record = get_player(self.id)
        self.name = record[1]
        self.email = record[2]
        self.phno = record[3]
        self.age = record[4]
    def set_start(self):
        start = datetime.now()
        start = datetime.strftime(start, "%H:%M:%S")
        self.start = datetime.strptime(start, "%H:%M:%S")
    def set_stop(self):
        stop = datetime.now()
        stop = datetime.strftime(stop, "%H:%M:%S")
        self.stop = datetime.strptime(stop, "%H:%M:%S")
    def set_marks(self, score):
        self.marks = score
    def time(self):
        return self.stop - self.start
    
curr_user = Curr_User()

@app.route("/", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        user = request.form["name"]
        email = request.form["email"]
        phno = request.form["phno"]
        age = request.form["age"]
        add_player(user, email, phno, age)
        curr_user.set_start()
        return redirect(url_for("game"))
    return render_template("Index.html")

@app.route('/game', methods = ["POST", "GET"])
def game():
    if request.method == "POST":
        req = request.form
        score = 0
        for key in req.keys():
            if "answer" in key:
                score += 1      
        curr_user.set_stop()
        curr_user.set_marks(score)
        update_player()
        return redirect(url_for('score'))
    return render_template("Game.html")

@app.route('/score')
def score():
    return render_template("Score.html", time = curr_user.time(), score = curr_user.marks)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        req = request.form
        if req["username"] == "Admin" and req["password"] == "1234":
            logged_user = LoginUser("Admin" + "PWD")
            login_user(logged_user)
            return redirect(url_for("admin"))
        else:
            return render_template("Login.html", info = "Wrong Username or Password")
    return render_template("Login.html")

@app.route("/admin")
@login_required
def admin():
    records = get_players_played()
    new_records = []
    for record in records:
        record = list(record)
        start = record[5].split(" ")
        stop = record[6].split(" ")

        start, stop = datetime.strptime(start[1], "%H:%M:%S"), datetime.strptime(stop[1], "%H:%M:%S")
        record.append(stop - start)
        new_records.append(record)
    return render_template("Admin.html", records = new_records)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(userid):
    return LoginUser(userid)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True
    g.user = current_user

if __name__=='__main__':
    app.run(debug=True)