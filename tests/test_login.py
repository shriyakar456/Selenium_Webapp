import json
import time
import psycopg2
import tempfile
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# Unique batch ID
batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

# Load users
with open('users.json', 'r') as file:
    all_users = json.load(file)

# Add invalid test cases
test_users = all_users + [
    {"username": "fake1", "password": "wrong1"},
    {"username": "admin", "password": "wrongpass"}
]

# Save result to DB
def log_result(username, expected, actual, result):
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO test_results (username, expected, actual, result, batch_id) VALUES (%s, %s, %s, %s, %s)", 
                (username, expected, actual, result, batch_id))
    conn.commit()
    cur.close()
    conn.close()

# Main test loop
for user in test_users:
    username = user['username']
    password = user['password']
    expected = "Success" if any(u['username'] == username and u['password'] == password for u in all_users) else "Failure"

    # Create isolated temp profile
    temp_profile_dir = tempfile.mkdtemp()

    # Chrome options
    options = Options()
    options.add_argument(f"--user-data-dir={temp_profile_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-features=PasswordManagerEnabled,AutofillServerCommunication")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-translate")
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.automatic_downloads": 1
    })

    if '--headless' in sys.argv:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    try:
        # Logout before fresh login
        driver.get("http://127.0.0.1:5000/logout")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))
        
        driver.get("http://127.0.0.1:5000/")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        time.sleep(1)

        if "/form" in driver.current_url:
            actual = "Success"
        elif "Invalid username or password" in driver.page_source:
            actual = "Failure"
        else:
            actual = "Unknown"

        result = "PASS" if expected == actual else "FAIL"
        print(f"{username}: {result} (Expected: {expected}, Actual: {actual})")
        log_result(username, expected, actual, result)

    except Exception as e:
        print(f"❌ Error in test for {username}: {e}")
        log_result(username, expected, "Unknown", "FAIL")

    finally:
        driver.quit()
        shutil.rmtree(temp_profile_dir, ignore_errors=True)

print("✅ All login tests complete. Test results saved to database.")
