from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Donations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity TEXT NOT NULL,
        date TEXT NOT NULL,
        pickup_time TEXT NOT NULL,
        location TEXT NOT NULL,
        suggestions TEXT,
        contact TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        ngo_status TEXT DEFAULT 'Pending',
        volunteer_name TEXT,
        volunteer_status TEXT DEFAULT 'Pending',
        delivery_status TEXT DEFAULT 'Pending'
    )
    """)

    # Volunteers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        contact TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")

# -----------------------------
# DONOR FORM PAGE
# -----------------------------
@app.route("/donor", methods=["GET", "POST"])
def donor():
    if request.method == "POST":
        name = request.form.get("name")
        quantity = request.form.get("quantity")
        date = request.form.get("date")
        pickup_time = request.form.get("pickup_time")
        location = request.form.get("location")
        suggestions = request.form.get("suggestions")
        contact = request.form.get("contact")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO donations
        (name, quantity, date, pickup_time, location, suggestions, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, quantity, date, pickup_time, location, suggestions, contact))

        conn.commit()
        conn.close()

        return render_template("success.html")

    return render_template("donor_form.html")

# -----------------------------
# DONOR DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations ORDER BY id DESC")
    donations = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", donations=donations)

# -----------------------------
# DONATION DETAILS
# -----------------------------
@app.route("/details/<int:id>")
def details(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations WHERE id=?", (id,))
    donation = cursor.fetchone()
    conn.close()
    return render_template("detail.html", donation=donation)

# -----------------------------
# NGO DASHBOARD
# -----------------------------
@app.route("/ngo_dashboard")
def ngo_dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations WHERE ngo_status='Pending'")
    requests = cursor.fetchall()
    conn.close()
    return render_template("ngo_dashboard.html", requests=requests)

# -----------------------------
# NGO ACTION (ACCEPT/REJECT)
# -----------------------------
@app.route("/ngo_action/<int:id>/<action>")
def ngo_action(id, action):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if action == "accept":
        cursor.execute("""
            UPDATE donations 
            SET status='Accepted by NGO',
                ngo_status='Accepted'
            WHERE id=?
        """, (id,))
        message = "Donation Accepted Successfully!"
        color = "success"

    elif action == "reject":
        cursor.execute("""
            UPDATE donations 
            SET status='Rejected by NGO',
                ngo_status='Rejected'
            WHERE id=?
        """, (id,))
        message = "Donation Rejected"
        color = "danger"

    conn.commit()
    conn.close()

    return render_template("ngo_result.html", message=message, color=color)

# -----------------------------
# ASSIGN VOLUNTEER
# -----------------------------
@app.route("/assign_volunteer/<int:id>", methods=["GET", "POST"])
def assign_volunteer(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        selected_vol = request.form.get("volunteer_name")

        cursor.execute("""
            UPDATE donations 
            SET volunteer_name=?,
                volunteer_status='Pending'
            WHERE id=?
        """, (selected_vol, id))

        conn.commit()
        conn.close()

        return render_template("ngo_result.html",
                               message="Volunteer Assigned Successfully!",
                               color="primary")

    cursor.execute("SELECT * FROM volunteers")
    volunteers = cursor.fetchall()
    conn.close()

    return render_template("assign_volunteer.html",
                           donation_id=id,
                           volunteers=volunteers)

# -----------------------------
# VOLUNTEER DASHBOARD
# -----------------------------
@app.route("/volunteer_dashboard")
def volunteer_dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations WHERE volunteer_status='Pending'")
    assignments = cursor.fetchall()
    conn.close()
    return render_template("volunteer_dashboard.html", assignments=assignments)

# -----------------------------
# VOLUNTEER ACTION
# -----------------------------
@app.route("/volunteer_action/<int:id>/<action>")
def volunteer_action(id, action):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if action == "accept":
        cursor.execute("""
            UPDATE donations 
            SET volunteer_status='Accepted',
                delivery_status='In Delivery'
            WHERE id=?
        """, (id,))
        message = "Volunteer Accepted the Delivery!"
        color = "success"

    elif action == "reject":
        cursor.execute("""
            UPDATE donations 
            SET volunteer_status='Rejected',
                delivery_status='Pending'
            WHERE id=?
        """, (id,))
        message = "Volunteer Rejected the Delivery!"
        color = "danger"

    conn.commit()
    conn.close()

    return render_template("ngo_result.html", message=message, color=color)

# -----------------------------
# MARK AS DELIVERED
# -----------------------------
@app.route("/mark_delivered/<int:id>")
def mark_delivered(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE donations 
        SET delivery_status='Delivered'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return render_template("ngo_result.html",
                           message="Donation Delivered Successfully!",
                           color="success")

# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
