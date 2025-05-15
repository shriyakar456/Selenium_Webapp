from flask import Flask, render_template
import psycopg2
import csv
from flask import make_response, request
import io

app = Flask(__name__)

def get_results():
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute("SELECT batch_id FROM test_results WHERE batch_id IS NOT NULL ORDER BY timestamp DESC LIMIT 1")
    result = cur.fetchone()
    if not result:
        return []
    latest_batch_id = result[0]
    cur.execute("SELECT username, expected, actual, result, timestamp FROM test_results WHERE batch_id = %s ORDER BY id", (latest_batch_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
    
def get_latest_form_results():
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute("SELECT batch_id FROM form_test_results WHERE batch_id IS NOT NULL ORDER BY timestamp DESC LIMIT 1")
    result = cur.fetchone()
    if not result:
        return []
    latest_batch_id = result[0]
    cur.execute("SELECT username, name, email, rating, category, product, comments, result, timestamp FROM form_test_results WHERE batch_id = %s ORDER BY id", (latest_batch_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
   
def get_all_batches(table_name):
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT batch_id FROM {table_name} WHERE batch_id IS NOT NULL ORDER BY batch_id DESC")
    batches = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return batches
    
def get_results_by_batch(table, batch_id):
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE batch_id = %s ORDER BY id", (batch_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.route("/")
def dashboard():
    selected_login_batch = request.args.get("login_batch")
    selected_form_batch = request.args.get("form_batch")

    login_batches = get_all_batches("test_results")
    form_batches = get_all_batches("form_test_results")

    login_results = get_results_by_batch("test_results", selected_login_batch or login_batches[0])
    form_results = get_results_by_batch("form_test_results", selected_form_batch or form_batches[0])

    return render_template("report.html", login_results=login_results, form_results=form_results,
                           login_batches=login_batches, form_batches=form_batches,
                           selected_login_batch=selected_login_batch or login_batches[0],
                           selected_form_batch=selected_form_batch or form_batches[0])
    
@app.route("/download/<report_type>")
def download_report(report_type):
    conn = psycopg2.connect(
        host="localhost", port=5434, database="webapp_db", user="postgres", password="ruchi123"
    )
    cur = conn.cursor()

    if report_type == "login":
        cur.execute("SELECT * FROM test_results ORDER BY id DESC")
        headers = ["id", "username", "expected", "actual", "result", "timestamp", "batch_id"]
    elif report_type == "form":
        cur.execute("SELECT * FROM form_test_results ORDER BY id DESC")
        headers = ["id", "username", "name", "email", "rating", "category", "product", "comments", "expected", "actual", "result", "timestamp", "batch_id"]
    else:
        return "Invalid report type", 400

    rows = cur.fetchall()
    cur.close()
    conn.close()

    output_stream = io.StringIO()
    writer = csv.writer(output_stream)

    writer.writerow(headers)
    writer.writerows(rows)

    # Reset pointer and pass as response
    output_stream.seek(0)
    response = make_response(output_stream.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={report_type}_test_report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

if __name__ == "__main__":
    app.run(port=5001, debug=True)
