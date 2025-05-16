import json
import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import sys

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
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5434,
            database="webapp_db",
            user="postgres",
            password="ruchi123"
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO test_results (username, expected, actual, result, batch_id) VALUES (%s, %s, %s, %s, %s)",
            (username, expected, actual, result, batch_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error inserting result for {username}: {e}")

# --- Setup Chrome options ---
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-features=PasswordManagerEnabled,AutofillServerCommunication")
options.add_argument("--disable-save-password-bubble")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-extensions")
options.add_argument("--disable-translate")

options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.default_content_setting_values.notifications": 2,  # blocks popups/notifications
    "profile.default_content_setting_values.automatic_downloads": 1
})

driver = webdriver.Chrome(options=options)

for user in test_users:
    username = user['username']
    password = user['password']
    expected = "Success" if any(u['username'] == username and u['password'] == password for u in all_users) else "Failure"

    try:
        # Logout before fresh login
        driver.get("http://127.0.0.1:5000/logout")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))

        # Load login page
        driver.get("http://127.0.0.1:5000/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

        # Fill login form
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")

        username_input.clear()
        username_input.send_keys(username)

        password_input.clear()
        password_input.send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Wait for either form page or error message
        WebDriverWait(driver, 5).until(
            lambda d: "/form" in d.current_url or "Invalid username or password" in d.page_source
        )

        if "/form" in driver.current_url:
            actual = "Success"
            result = "PASS" if expected == "Success" else "FAIL"
        elif "Invalid username or password" in driver.page_source:
            actual = "Failure"
            result = "PASS" if expected == "Failure" else "FAIL"
        else:
            actual = "Unknown"
            result = "FAIL"

    except Exception as e:
        actual = "Unknown"
        result = "FAIL"
        print(f"❌ Error in test for {username}: {e}")

    log_result(username, expected, actual, result)
    print(f"{username}: {result} (Expected: {expected}, Actual: {actual})")

driver.quit()
print("✅ All login tests complete. Test results saved to database.")
