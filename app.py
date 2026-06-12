from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

import os


app = Flask(__name__)

app.secret_key = "IFS_SECRET_KEY"


# ==========================
# DATABASE CONFIG
# ==========================

database_url = os.getenv(
    "DATABASE_URL"
)

if database_url:

    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

else:
    database_url = (
        "sqlite:///ifs_local.db"
    )

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = database_url

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


db = SQLAlchemy(app)


# ==========================
# DATABASE MODEL
# ==========================

class Transaction(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    tanggal = db.Column(
        db.String(100)
    )

    jenis = db.Column(
        db.String(100)
    )

    kategori = db.Column(
        db.String(100)
    )

    nominal = db.Column(
        db.Integer
    )

    keterangan = db.Column(
        db.String(200)
    )


# ==========================
# CREATE DATABASE
# ==========================

with app.app_context():
    db.create_all()


# ==========================
# LOGIN
# ==========================

@app.route("/")
def login():

    return render_template(
        "login.html"
    )


@app.route(
    "/login",
    methods=["POST"]
)
def process_login():

    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )

    if (
        username == "Irvan"
        and
        password == "030904"
    ):

        session["user"] = username

        return redirect(
            "/dashboard"
        )

    return """
    <h2>Login gagal</h2>
    <a href='/'>Kembali</a>
    """


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/")

    transactions = (
        Transaction.query
        .order_by(
            Transaction.id.desc()
        )
        .all()
    )

    data = []

    masuk = 0
    keluar = 0

    for t in transactions:

        data.append([
            t.tanggal,
            t.jenis,
            t.kategori,
            t.nominal,
            t.keterangan,
            t.id
        ])

        if (
            t.jenis
            ==
            "Pemasukan"
        ):

            masuk += t.nominal

        else:

            keluar += t.nominal

    saldo = masuk - keluar
    return render_template(
        "dashboard.html",
        username=session["user"],
        data=data,
        saldo=saldo,
        pemasukan=masuk,
        pengeluaran=keluar
    )


# ==========================
# TAMBAH TRANSAKSI
# ==========================

@app.route(
    "/add",
    methods=["POST"]
)
def add_transaction():

    if "user" not in session:
        return redirect("/")

    jenis = request.form.get(
        "jenis"
    )

    kategori = request.form.get(
        "kategori"
    )

    nominal = request.form.get(
        "nominal"
    )

    keterangan = request.form.get(
        "keterangan"
    )

    transaksi = Transaction(

        tanggal=datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        ),

        jenis=jenis,

        kategori=kategori,

        nominal=int(nominal),

        keterangan=keterangan
    )

    db.session.add(
        transaksi
    )

    db.session.commit()

    return redirect(
        "/dashboard"
    )


# ==========================
# HAPUS SATU DATA
# ==========================

@app.route("/delete/<int:id>")
def delete_transaction(id):

    if "user" not in session:
        return redirect("/")

    transaksi = (
        Transaction.query
        .get(id)
    )

    if transaksi:

        db.session.delete(
            transaksi
        )

        db.session.commit()

    return redirect(
        "/dashboard"
    )


# ==========================
# CLEAR ALL DATA
# ==========================

@app.route("/clear")
def clear_data():

    if "user" not in session:
        return redirect("/")

    Transaction.query.delete()

    db.session.commit()

    return redirect(
        "/dashboard"
    )


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )