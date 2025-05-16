import time
import psycopg2
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# ---------- Configuration ----------
batch_id = datetime.now().strftime("%Y%m%d%H%M%S")
DB_CONFIG = {
    "host": "localhost",
    "port": 5434,
    "database": "webapp_db",
    "user": "postgres",
    "password": "ruchi123"
}

# ---------- DB Logger ----------
def log_behaviour_result(username, behavior, status, details):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO behaviour_test_results (username, behavior, result, details, batch_id) VALUES (%s, %s, %s, %s, %s) ", (username, behavior, status, details, batch_id))
    conn.commit()
    cur.close()
    conn.close()

# ---------- Headless Chrome Config ----------
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

if '--headless' in sys.argv:
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

# ---------- Browser Setup ----------
driver = webdriver.Chrome(options=options)
driver.get("http://127.0.0.1:5000/")
time.sleep(1)

# ---------- Simulate Login ----------
try:
    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(1)

    if "/form" in driver.current_url:
        log_behaviour_result("admin", "Login", "PASS", "Successfully navigated to form page.")
    else:
        raise Exception("Login redirection failed")
except Exception as e:
    log_behaviour_result("admin", "Login", "FAIL", str(e))
    driver.quit()
    sys.exit(1)

# ---------- Simulate Hover Action ----------
try:
    actions = ActionChains(driver)
    nav_element = driver.find_element(By.TAG_NAME, "nav")  # Adjust as per actual UI
    actions.move_to_element(nav_element).perform()
    time.sleep(1)
    log_behaviour_result("admin", "Hover Navigation", "PASS", "Hover over navbar simulated.")
except Exception as e:
    log_behaviour_result("admin", "Hover Navigation", "FAIL", str(e))

# ---------- Simulate Inactivity Timeout ----------
try:
    time.sleep(5)  # Simulate user idle time (can increase to test session expiry)
    driver.find_element(By.NAME, "comments").send_keys("Test comment after idle.")
    log_behaviour_result("admin", "Idle Input", "PASS", "Successfully interacted after idle.")
except Exception as e:
    log_behaviour_result("admin", "Idle Input", "FAIL", str(e))

# ---------- Clean up ----------
driver.quit()
print("✅ User behaviour simulation complete. Results saved to DB.")
