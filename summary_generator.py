import psycopg2

def print_summary(table_name, label):
    conn = psycopg2.connect(
        host="localhost", port=5434,
        database="webapp_db",
        user="postgres", password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*), SUM(CASE WHEN result='PASS' THEN 1 ELSE 0 END) FROM {table_name}")
    total, passed = cur.fetchone()
    print(f"\n🧪 {label} Summary\n✅ Total: {total} | ✅ Passed: {passed or 0} | ❌ Failed: {(total - (passed or 0))}")
    cur.close()
    conn.close()

print_summary("test_results", "Login Test")
try:
    print_summary("form_test_results", "Feedback Form Test")
except:
    print("🧪 Feedback Form Test Summary\nNo form results found.")
try:
    print_summary("behaviour_test_results", "User Behaviour Simulation")
except Exception:
    print("🧪 User Behaviour Simulation Summary\nNo simulation results found.")
