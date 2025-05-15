import csv
import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import sys
from selenium.webdriver.chrome.options import Options

def log_form_result(username, name, email, rating, category, product, comments, expected, actual, result):
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="webapp_db",
        user="postgres",
        password="ruchi123"
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO form_test_results (username, name, email, rating, category, product, comments, expected, actual, result, batch_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ", (username, name, email, rating, category, product, comments, expected, actual, result, batch_id))
    conn.commit()
    cur.close()
    conn.close()

# --- Load CSV ---
with open("form_test_data.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    test_data = list(reader)

options = Options()
if '--headless' in sys.argv:
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
driver.get("http://127.0.0.1:5000/")
time.sleep(1)

# --- Login first ---
driver.find_element(By.NAME, "username").send_keys("admin")
driver.find_element(By.NAME, "password").send_keys("1234")
driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
time.sleep(1)

assert "/form" in driver.current_url, "❌ Login failed. Cannot proceed to form."

# --- Submit feedbacks from CSV ---

batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

for entry in test_data:
    try:
        name = entry["name"]
        email = entry["email"]
        rating = entry["rating"]
        category = entry["category"]
        product = entry["product"]
        comments = entry["comments"]

        driver.find_element(By.NAME, "name").clear()
        driver.find_element(By.NAME, "email").clear()
        driver.find_element(By.NAME, "rating").clear()
        driver.find_element(By.NAME, "comments").clear()

        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "rating").send_keys(rating)
        Select(driver.find_element(By.NAME, "category")).select_by_visible_text(category)
        Select(driver.find_element(By.NAME, "product")).select_by_visible_text(product)
        driver.find_element(By.NAME, "comments").send_keys(comments)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(1)

        if "Your feedback has been submitted" in driver.page_source:
            actual = "Success"
            result = "PASS"
        else:
            actual = "Failure"
            result = "FAIL"

        log_form_result("admin", name, email, rating, category, product, comments,
                        expected="Success", actual=actual, result=result)
        print(f"{name}: {result} (Expected: Success, Actual: {actual})")

    except Exception as e:
        print(f"❌ Error in test for {entry.get('name', '?')}: {e}")
    driver.get("http://127.0.0.1:5000/form")
    time.sleep(1)

driver.quit()
print("✅ All feedback submissions tested and logged.")
