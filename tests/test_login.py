import json
import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime

batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

# --- Load users ---
with open('users.json', 'r') as file:
    all_users = json.load(file)

# Add invalid cases
test_users = all_users + [
    {"username": "fake1", "password": "wrong1"},
    {"username": "admin", "password": "wrongpass"}
]

def log_result(username, expected, actual, result):
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO test_results (username, expected, actual, result, batch_id) VALUES (%s, %s, %s, %s, %s) ", (username, expected, actual, result, batch_id))
    conn.commit()
    cur.close()
    conn.close()

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-features=PasswordCheck")
options.add_argument("--disable-save-password-bubble")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-extensions")
options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
})

driver = webdriver.Chrome(options=options)

for user in test_users:
    username = user['username']
    password = user['password']
    expected = "Success" if any(u['username'] == username and u['password'] == password for u in all_users) else "Failure"

    driver.get("http://127.0.0.1:5000/")  # Force reload
    time.sleep(1)

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(1)

    if "/form" in driver.current_url:
        actual = "Success"
        result = "PASS" if expected == "Success" else "FAIL"
    elif "Invalid username or password" in driver.page_source:
        actual = "Failure"
        result = "PASS" if expected == "Failure" else "FAIL"
    else:
        actual = "Unknown"
        result = "FAIL"

    log_result(username, expected, actual, result)
    print(f"{username}: {result} (Expected: {expected}, Actual: {actual})")

driver.quit()
print("✅ All login tests complete. Test results saved to database.")
