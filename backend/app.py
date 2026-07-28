from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import mysql.connector
import os
import uuid

# =====================================================
# Flask Configuration
# =====================================================

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

app.permanent_session_lifetime = timedelta(days=7)

# =====================================================
# Upload Folder Configuration
# =====================================================

UPLOAD_FOLDER = "static/uploads/profile"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =====================================================
# MySQL Configuration
# =====================================================

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "polytechnic_hub"
}

def get_db():
    return mysql.connector.connect(**db_config)

# =====================================================
# Image Validation
# =====================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS
    )

# =====================================================
# Home
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")

# =====================================================
# Login + Register Page
# =====================================================

@app.route("/login")
def login_page():

    return render_template("login.html")

# =====================================================
# Dashboard
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user_name=session.get("name")
    )

# =====================================================
# Logout
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =====================================================
# API Status
# =====================================================

@app.route("/api/status")
def api_status():

    return jsonify({

        "status": "running",

        "backend": "Python Flask",

        "database": "MySQL",

        "project": "POLYTECHNIC HUB"

    })
    # =====================================================
# USER REGISTRATION
# =====================================================

@app.route("/register", methods=["POST"])
def register():

    try:

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # -----------------------------
        # Get Form Data
        # -----------------------------

        full_name = request.form.get("name")
        username = request.form.get("username")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        state = request.form.get("state")
        district = request.form.get("district")
        college = request.form.get("college")
        course = request.form.get("course")
        branch = request.form.get("branch")
        semester = request.form.get("semester")
        bio = request.form.get("bio")
        password = request.form.get("password")

        # -----------------------------
        # Check Username
        # -----------------------------

        cursor.execute(
            "SELECT id FROM users WHERE username=%s",
            (username,)
        )

        if cursor.fetchone():

            return jsonify({
                "success": False,
                "message": "Username already exists."
            })

        # -----------------------------
        # Check Mobile
        # -----------------------------

        cursor.execute(
            "SELECT id FROM users WHERE mobile=%s",
            (mobile,)
        )

        if cursor.fetchone():

            return jsonify({
                "success": False,
                "message": "Mobile number already registered."
            })

        # -----------------------------
        # Check Email
        # -----------------------------

        if email:

            cursor.execute(
                "SELECT id FROM users WHERE email=%s",
                (email,)
            )

            if cursor.fetchone():

                return jsonify({
                    "success": False,
                    "message": "Email already exists."
                })

        # -----------------------------
        # Password Hash
        # -----------------------------

        hashed_password = generate_password_hash(password)

        # -----------------------------
        # Upload Profile Photo
        # -----------------------------

        photo_name = ""

        if "photo" in request.files:

            photo = request.files["photo"]

            if photo.filename != "" and allowed_file(photo.filename):

                extension = photo.filename.rsplit(".",1)[1].lower()

                photo_name = str(uuid.uuid4()) + "." + extension

                photo.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        photo_name
                    )
                )

        # -----------------------------
        # Insert User
        # -----------------------------

        sql = """
        INSERT INTO users
        (
            name,
            username,
            mobile,
            email,
            dob,
            gender,
            state,
            district,
            college,
            course,
            branch,
            semester,
            bio,
            profile_photo,
            password
        )

        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
        """

        values = (
            full_name,
            username,
            mobile,
            email,
            dob,
            gender,
            state,
            district,
            college,
            course,
            branch,
            semester,
            bio,
            photo_name,
            hashed_password
        )

        cursor.execute(sql, values)

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({

            "success": True,

            "message": "Registration Successful"

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        })

# =====================================================
# USER LOGIN
# =====================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        mobile = request.form.get("mobile")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE mobile=%s",
            (mobile,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user is None:

            return jsonify({

                "success": False,

                "message": "Mobile number not registered."

            })

        if not check_password_hash(
            user["password"],
            password
        ):

            return jsonify({

                "success": False,

                "message": "Wrong password."

            })

        session.permanent = True

        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["username"] = user["username"]
        session["mobile"] = user["mobile"]
        session["photo"] = user["profile_photo"]

        return jsonify({

            "success": True,

            "message": "Login Successful",

            "redirect": "/dashboard"

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        })


# =====================================================
# CHECK LOGIN
# =====================================================

@app.route("/check-login")
def check_login():

    if "user_id" in session:

        return jsonify({

            "logged_in": True,

            "name": session["name"],

            "username": session["username"],

            "photo": session["photo"]

        })

    return jsonify({

        "logged_in": False

    })


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(

        "dashboard.html",

        name=session["name"],

        username=session["username"],

        photo=session["photo"]

    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =====================================================
# API STATUS
# =====================================================

@app.route("/api/status")
def api_status():

    return jsonify({

        "status": "running",

        "backend": "Python Flask",

        "database": "MySQL",

        "project": "POLYTECHNIC HUB"

    })


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )
