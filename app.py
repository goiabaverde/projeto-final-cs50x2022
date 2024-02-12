import sqlite3
from flask import Flask, render_template, request, session, redirect, session, url_for
from datetime import datetime
import cs50
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

db = cs50.SQL("sqlite:///users.db")

@app.route("/register", methods=["POST", "GET"])
def register():
    con=sqlite3.connect("users.db")
    c=con.cursor()
    if request.method == 'POST':
        if(request.form["name"] != "" and request.form["password"]!= ""):
            global name
            name = request.form["name"]
            password= request.form["password"]
            conpassword = request.form["conpassword"]
            if conpassword != password:
                return render_template("fail-conpas.html")
            password = generate_password_hash(password)
            statatments = f"SELECT * FROM users WHERE name = '{name}'"
            c.execute(statatments)
            data=c.fetchone()
            if data:
                return render_template("fail-register.html")
            else:
                if not data:
                    c.execute("INSERT INTO users (name, hash) VALUES(?,?)", (name,password))
                    con.commit()
                    con.close()
                    return render_template("login.html")
    elif request.method == 'GET':
        return render_template("register.html")
    

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        #get the info from input
        na = request.form['name']
        session["na"] = na
        pa = request.form['password']
        con = sqlite3.connect('users.db')
        c = con.cursor()

        #check with user exists
        statement = f"SELECT name FROM users WHERE name = '{na}' "
        c.execute(statement)
        data =c.fetchone()
        if not data:
            return render_template("fail-login.html")
        ##check hash password
        password = db.execute("SELECT * FROM users WHERE name = ?", ((na,)))
        if not check_password_hash(password[0]["hash"], pa):
            return render_template("fail-login.html")
        else:
            na = session["na"]
            return render_template('index.html', na = na)
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    #end a session
    session.pop("na", None)
    return redirect(url_for("login"))

@app.route("/", methods=["POST", "GET"])
def home():
    if "na" in session:
        global na
        na = session["na"]
    else:
        return redirect(url_for("login"))
    return render_template("index.html")
   


@app.route("/results", methods=["POST", "GET"])
def results():
    if request.method=="POST":
            a = request.form.get("a")
            b = request.form.get("b")
            c = request.form.get("c")
            na = session["na"]
            now = datetime.now()
            date = now.strftime("%m/%d %I:%M:%p")
            con = sqlite3.connect("historic.db")
            cur=con.cursor()
            cur.execute("INSERT INTO historic (user_id, a, b, c, date) VALUES(?, ?, ?, ?, ?)", (na ,a, b, c, date))
            con.commit()
            con.close()
            return render_template("results.html", na = na)
    else:
        return render_template("results.html")
@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        try:
            der = sqlite3.connect("historic.db")
            dlr=der.cursor()
            dlr.execute("DELETE FROM historic WHERE user_id = ?", na)
            der.commit()
            return render_template("historic.html")
        except:    
            return render_template("historic.html")
        finally:
            der.close()
    elif request.method == "GET":
        return render_template("historic.html")
        
@app.route("/explanation")
def explanation():
    if request.method == "GET":
        return render_template("explanation.html")
    else:
        return render_template("fail.html")


@app.route("/historic")
def historic():
    if request.method == "GET":
        if "na" in session:
            global na
            na = session["na"]
        else:
            return redirect(url_for("login"))
        rer = sqlite3.connect("historic.db")
        rer.row_factory = sqlite3.Row
        dur=rer.cursor()
        dur.execute("SELECT * FROM historic WHERE user_id = ?", ((na,)))
        results = dur.fetchall()
        return render_template("historic.html", historic=results)

   


