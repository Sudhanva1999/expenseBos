from flask import Flask, render_template, request, redirect, url_for, session, make_response
import pyrebase
from datetime import datetime
import random
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Dictionary for mapping email to username during login
users_emails = {
    "sid.paturkar@gmail.com": "sudhanva",
    "aadityakasbekar@gmail.com": "aaditya",
    "yesitsmefolks@gmail.com": "kartik",
    "sirsarthakanjikar@gmail.com": "sarthak",
    "sunny@gmail.com": "sunny",
}

config = {
    "apiKey": os.environ.get('API_KEY'),
    "authDomain": os.environ.get('AUTH_DOMAIN'),
    "projectId": os.environ.get('PROJECT_ID'),
    "storageBucket":os.environ.get('STORAGE_BUCKET'),
    "messagingSenderId": os.environ.get('MESSAGING_SENDER_ID'),
    "appId": os.environ.get('APP_ID'),
    "measurementId": os.environ.get('MEASUREMENT_ID'),
    "databaseURL":os.environ.get('DATABASE_URL')
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/dashboard")
def render_dashboard():
    user_name = session.get("user")
    all_data = db.child(user_name).get()
    debt_data = {}
    you_owe = 0
    you_are_owed = 0
    debt_summary = {}

    for item in all_data.each():
        debt_data[item.key()] = item.val()
        int_val = int(item.val())

        if int_val < 0:
            you_owe += abs(int_val)
        else:
            you_are_owed += int_val

    debt_summary["you_owe"] = you_owe
    debt_summary["you_are_owed"] = you_are_owed

    return render_template(
        "dashboard.html",
        debt_data=debt_data,
        user_name=user_name,
        debt_summary=debt_summary,
    )


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user = auth.refresh(user["refreshToken"])
        uid_variable = user["userId"]

        # Map email to username using the predefined dictionary
        session["user"] = users_emails.get(email)

        return redirect("/dashboard")
    except Exception as e:
        error_message = f"Error: {e}"
        return render_template("login.html", error_message=error_message)


@app.route("/add_expense")
def add_expense():
    # Use the predefined dictionary for users
    users = users_emails.values()
    return render_template("addExpense.html", users=users)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/submitExpense", methods=["POST"])
def submit_expense():
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%d/%m/%Y")
    formatted_date_id = current_datetime.strftime("%d%m%Y")
    item = request.form["item"]
    value = float(request.form["value"])
    paid_by = request.form["paidBy"]
    split_equally = "splitEqually" in request.form

    # Use a list comprehension to get the selected users
    splitArray = [user for user in users_emails.values() if f"checkbox_{user.lower()}" in request.form]
    count = len(splitArray)

    if split_equally:
        splitArray = list(users_emails.values())
        percentages = {user: round(value / 5, 2) for user in splitArray}
        percentages[paid_by] = 0
    else:
        percentages = {user: round(value / count, 2) for user in splitArray}

    log_id = formatted_date_id + item + paid_by + str(random.randint(100000, 999999))
    db.child("logs").update({
        log_id: {
            "date": formatted_date,
            "item": item,
            "paid_by": paid_by,
            "split_by": percentages,
            "value": value,
        }
    })

    # Update balances
    for user in splitArray:
        if user != paid_by:
            per_head_split = percentages[user]
            current_balance = db.child(user).child(paid_by).get().val() or 0
            new_balance = current_balance - per_head_split
            db.child(user).child(paid_by).set(new_balance)
            db.child(paid_by).child(user).set(-new_balance)

    return redirect("/dashboard")



@app.route("/reports", methods=["GET", "POST"])
def view_reports():
    user_name = session.get("user")
    if not user_name:
        return redirect(url_for("index"))

    if request.method == "POST":
        # Handle search functionality
        search_query = request.form.get("search_query")
        month_filter = request.form.get("month_filter")
        year_filter = request.form.get("year_filter")
        paid_by_filter = request.form.get("paid_by_filter")

        # Retrieve logs based on search, month filter, year filter, and paid by filter
        logs = retrieve_logs(
            user_name, search_query, month_filter, year_filter, paid_by_filter
        )
    else:
        # Retrieve all logs initially
        logs = retrieve_logs(user_name)

    return render_template("report.html", logs=logs)


# Function to retrieve logs based on filters
def retrieve_logs(
    user_name,
    search_query=None,
    month_filter=None,
    year_filter=None,
    paid_by_filter=None,
):
    # Retrieve all logs from the database
    logs_data = db.child("logs").get().val()

    # Process logs data and filter based on user, search_query, month_filter, year_filter, and paid_by_filter
    logs = [
        {
            "id": log_id,
            "date": log_details["date"],
            "item": log_details["item"],
            "value": log_details["value"],
            "paid_by": log_details["paid_by"],
            "split_by": list(log_details["split_by"].keys()),
        }
        for log_id, log_details in logs_data.items()
        if (
            (not search_query or search_query.lower() in log_details["item"].lower())
            and (
                not month_filter
                or month_filter.lower() == log_details["date"].split("/")[1].lower()
            )
            and (
                not year_filter
                or year_filter.lower() == log_details["date"].split("/")[2].lower()
            )
            and (
                not paid_by_filter
                or paid_by_filter.lower() == log_details["paid_by"].lower()
            )
        )
    ]

    # Sort logs by date in descending order
    logs.sort(key=lambda x: datetime.strptime(x["date"], "%d/%m/%Y"), reverse=True)

    return logs


@app.route("/delete_log/<log_id>", methods=["POST"])
def delete_log(log_id):
    user_name = session.get("user")
    if not user_name:
        return redirect(url_for("index"))

    deleted_log = db.child("logs").child(log_id).get().val()

    for user, amount in deleted_log["split_by"].items():
        if user != deleted_log["paid_by"]:
            current_balance = db.child(user).child(deleted_log["paid_by"]).get().val()
            if current_balance is not None:
                new_balance = current_balance + amount
                db.child(user).child(deleted_log["paid_by"]).set(new_balance)

    db.child("deleted_logs").update({log_id: deleted_log})
    db.child("logs").child(log_id).remove()

    return redirect(url_for("view_reports"))

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
