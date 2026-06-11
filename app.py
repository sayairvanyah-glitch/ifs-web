from flask import Flask, render_template, request, redirect, session
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ifs_secret"

CSV_FILE = "transaksi.csv"

# INIT CSV
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tanggal","Jenis","Kategori","Nominal","Keterangan"])

def hitung():
    masuk = 0
    keluar = 0

    with open(CSV_FILE) as f:
        r = csv.DictReader(f)
        for i in r:
            if i["Nominal"].isdigit():
                if i["Jenis"] == "Pemasukan":
                    masuk += int(i["Nominal"])
                else:
                    keluar += int(i["Nominal"])

    return masuk, keluar, masuk - keluar


@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u == "Irvan" and p == "030904":
            session["user"] = u
            return redirect("/dashboard")

        return "Login gagal!"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    data = []
    with open(CSV_FILE) as f:
        r = csv.reader(f)
        next(r)
        for i in r:
            data.append(i)

    masuk, keluar, saldo = hitung()

    return render_template(
        "dashboard.html",
        data=data,
        masuk=masuk,
        keluar=keluar,
        saldo=saldo
    )


@app.route("/add", methods=["POST"])
def add():
    jenis = request.form["jenis"]
    kategori = request.form["kategori"]
    nominal = request.form["nominal"]
    ket = request.form["keterangan"]

    tgl = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([tgl, jenis, kategori, nominal, ket])

    return redirect("/dashboard")
@app.route("/clear")
def clear():

    with open(
        CSV_FILE,
        "w",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "Tanggal",
            "Jenis",
            "Kategori",
            "Nominal",
            "Keterangan"
        ])

    return redirect("/dashboard")


@app.route("/delete/<int:index>")
def delete(index):

    rows = []

    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)

        header = next(reader)

        for row in reader:
            rows.append(row)

    if index < len(rows):
        rows.pop(index)

    with open(
        CSV_FILE,
        "w",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow(header)
        writer.writerows(rows)

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)