from flask import Flask, render_template, request, redirect, url_for, flash
import qrcode
import os

from models import User
from forms import register_form
from app import db, bcrypt

from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash


from forms import login_form, register_form

app = Flask(__name__)


@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")
    return render_template('login.html', form=form)


@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data

            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )

            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(e, "danger")

    return render_template('register.html', form=form)


@app.route('/qr-code', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,  # Задайте здесь желаемый размер пикселя
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Удаляем старый QR-код перед сохранением нового
        if os.path.exists("static/qrcode.png"):
            os.remove("static/qrcode.png")

        img.save("static/qrcode.png")
        return render_template('main.html', link=link)
    return render_template('main.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
