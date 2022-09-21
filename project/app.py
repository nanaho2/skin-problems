from unicodedata import name
from flask import Flask, render_template, request, redirect, session
import re
from PIL import Image
import pyocr
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os
from werkzeug.utils import secure_filename
import werkzeug
from datetime import datetime

from helpers import login_required


app = Flask(__name__)
db = SQL("sqlite:///cause.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# OCRエンジンを取得
path_tesseract = "/usr/share/doc/Tesseract-ocr"
if path_tesseract not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + path_tesseract
tools = pyocr.get_available_tools()
tool = tools[0]

# 受け取るデータサイズを1MBに制限
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# ファイルの保存場所を指定
UPLOAD_DIR = os.getenv("/workspaces/106944027/FP/uploadfiles/")

@app.route("/", methods=["GET"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/form", methods=["GET", "POST"])
@login_required
def form():
    if request.method == "GET":
        return render_template("form.html")

    if request.method == "POST":
        if not request.form.get("bad"):
            return render_template("apology.html", error = "荒れたほうの成分を入力してください")

        elif not request.form.get("good"):
            return render_template("apology.html", error = "大丈夫だったほうの成分を入力してください")

        bad_str = request.form.get("bad")
        good_str = request.form.get("good")

        bad = re.split('[,、　 ]', bad_str)
        good = re.split('[,、　 ]', good_str)

        results = set(bad) - set(good)

        db.execute("insert into history(user_id, date, bad, good, result) values(?, CURRENT_TIMESTAMP, ?, ?, ?);", session["user_id"], bad, good, results)

        return render_template("result.html", results = results)

    else:
        return redirect("/login")

@app.route("/image", methods=["GET", "POST"])
@login_required
def image():
    if request.method == "GET":
        return render_template("ocr.html")

    if request.method == "POST":
        if 'ocr_bad' not in request.files:
            return render_template("apology.html", error = "成分の画像を添付してください")

        if 'ocr_good' not in request.files:
            return render_template("apology.html", error = "成分の画像を添付してください")

        builder = pyocr.builders.TextBuilder(tesseract_layout=6)

        ocr_bad = request.files['ocr_bad']
        ocr_good= request.files['ocr_good']

        fileName_bad = ocr_bad.filename
        if '' == fileName_bad:
            return render_template("apology.html", error = "ファイルの名前は必須です")

        fileName_good = ocr_good.filename
        if '' == fileName_good:
            return render_template("apology.html", error = "ファイルの名前は必須です")

        saveFileName_bad = "bad" + datetime.now().strftime("%Y%m%d_%H%M%S_") + werkzeug.utils.secure_filename(fileName_bad)
        saveFileName_good = "good" + datetime.now().strftime("%Y%m%d_%H%M%S_") + werkzeug.utils.secure_filename(fileName_good)
        ocr_bad.save(os.path.join("/workspaces/106944027/project/uploadfiles", saveFileName_bad))
        ocr_good.save(os.path.join("/workspaces/106944027/project/uploadfiles", saveFileName_good))

        path_bad = "/workspaces/106944027/project/uploadfiles/" + saveFileName_bad
        path_good = "/workspaces/106944027/project/uploadfiles/" + saveFileName_good
        bad_str = tool.image_to_string(Image.open(path_bad), lang="jpn", builder=builder)
        good_str = tool.image_to_string(Image.open(path_good), lang="jpn", builder=builder)

        bad = re.split('[,、　 ]', bad_str)
        good = re.split('[,、　 ]', good_str)

        results = set(bad) - set(good)
        results_list = list(results)
        results_str = "".join(results_list)

        db.execute("insert into history(user_id, date, bad, good, result) values(?, CURRENT_TIMESTAMP, ?, ?, ?);", session["user_id"], bad_str, good_str, results_str)

        return render_template("result.html", results = results, bad = bad_str, good = good_str)

    else:
        return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", error = "ユーザーネームを入力してください")

        elif not request.form.get("password"):
            return render_template("apology.html", error = "パスワードを入力してください")

        elif not request.form.get("confirmation"):
            return render_template("apology.html", error = "確認用パスワードを入力してください")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) == 1:
            return render_template("apology.html", error = "入力されたユーザーネームはすでに使用されています")

        if not (request.form.get("password") == request.form.get("confirmation")):
            render_template("apology.html", error = "パスワードが一致しません")

        hash_pass = generate_password_hash(request.form.get("password"))

        db.execute("insert into users(username, password_hash) values(?, ?);", (request.form.get("username")), hash_pass)

        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", error = "ユーザーネームを入力してください")

        elif not request.form.get("password"):
            return render_template("apology.html", error = "パスワードを入力してください")

        rows = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))

        if len(rows) != 1:
            return render_template("apology.html", error = "入力されたユーザーネームは登録されていません")

        if check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            session["user_id"] = rows[0]["id"]
            return render_template("index.html")

        else:
            return render_template("apology.html", error = "パスワードまたはユーザーネームが間違っています")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/history", methods=["GET"])
@login_required
def history():
    if request.method == "GET":
        data = db.execute("SELECT date, bad, good, result FROM history WHERE user_id = ?;", session["user_id"])
        return render_template("history.html", datas = data)
