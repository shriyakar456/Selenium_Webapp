import csv
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5434,
    database="webapp_db",
    user="postgres",
    password="ruchi123"
)
cur = conn.cursor()

def export_table_to_csv(table_name, filename):
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]

    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerows(rows)

    print(f"✅ Exported {table_name} to {filename}")

export_table_to_csv("test_results", "login_report.csv")
export_table_to_csv("form_test_results", "form_report.csv")
export_table_to_csv("behaviour_test_results","behaviour_report.csv")

cur.close()
conn.close()
