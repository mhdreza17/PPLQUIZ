from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import time


@pytest.fixture(scope='module')
def driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope='module')
def base_url():
    return "http://127.0.0.1:8000"


def alert_text(driver):
    try:
        a = driver.find_element(By.CSS_SELECTOR, 'div.alert-danger')
        return a.text
    except Exception:
        pass
    try:
        p = driver.find_element(By.CSS_SELECTOR, 'p.text-danger')
        return p.text
    except Exception:
        return ''


def test_login_valid(driver, base_url):
    driver.get(base_url + '/login.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'username')))
    driver.find_element(By.ID, 'username').send_keys('existinguser')
    driver.find_element(By.ID, 'InputPassword').send_keys('TestPass1!')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(1)
    assert 'index.php' in driver.current_url


def test_login_empty_password(driver, base_url):
    driver.get(base_url + '/login.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'username')))
    driver.find_element(By.ID, 'username').send_keys('existinguser')
    driver.find_element(By.ID, 'InputPassword').clear()
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(0.5)
    assert 'Data tidak boleh kosong' in alert_text(driver) or alert_text(driver) != ''


def test_login_empty_username(driver, base_url):
    driver.get(base_url + '/login.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'username')))
    driver.find_element(By.ID, 'username').clear()
    driver.find_element(By.ID, 'InputPassword').send_keys('doesntmatter')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(0.5)
    assert 'Data tidak boleh kosong' in alert_text(driver) or alert_text(driver) != ''


def test_login_not_registered(driver, base_url):
    driver.get(base_url + '/login.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'username')))
    driver.find_element(By.ID, 'username').send_keys('no_such_user_123')
    driver.find_element(By.ID, 'InputPassword').send_keys('whatever')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(0.5)
    assert 'Register User Gagal' in alert_text(driver) or alert_text(driver) != ''


def test_login_wrong_password(driver, base_url):
    driver.get(base_url + '/login.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'username')))
    driver.find_element(By.ID, 'username').send_keys('existinguser')
    driver.find_element(By.ID, 'InputPassword').send_keys('WrongPassword')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(0.5)
    assert 'Register User Gagal' in alert_text(driver) or alert_text(driver) != ''


def test_register_password_mismatch(driver, base_url):
    driver.get(base_url + '/register.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'name')))
    driver.find_element(By.ID, 'name').send_keys('Tester')
    uniq = str(int(time.time()))
    driver.find_element(By.ID, 'InputEmail').send_keys(f'test{uniq}@example.com')
    driver.find_element(By.ID, 'username').send_keys(f'user{uniq}')
    driver.find_element(By.ID, 'InputPassword').send_keys('abc123')
    driver.find_element(By.ID, 'InputRePassword').send_keys('different')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(0.5)
    assert 'Password tidak sama' in alert_text(driver) or alert_text(driver) != ''


def test_register_valid(driver, base_url):
    driver.get(base_url + '/register.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'name')))
    driver.find_element(By.ID, 'name').send_keys('Tester')
    uniq = str(int(time.time()))
    username = f'autotest{uniq}'
    driver.find_element(By.ID, 'InputEmail').send_keys(f'{username}@example.com')
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'InputPassword').send_keys('SecurePass1!')
    driver.find_element(By.ID, 'InputRePassword').send_keys('SecurePass1!')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(1)
    assert 'index.php' in driver.current_url


def test_register_sql_injection(driver, base_url):
    driver.get(base_url + '/register.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'name')))
    driver.find_element(By.ID, 'name').send_keys("Injection Tester")
    payload = "injection' OR '1'='1"
    driver.find_element(By.ID, 'InputEmail').send_keys('inject@example.com')
    driver.find_element(By.ID, 'username').send_keys(payload)
    driver.find_element(By.ID, 'InputPassword').send_keys('whatever')
    driver.find_element(By.ID, 'InputRePassword').send_keys('whatever')
    driver.find_element(By.NAME, 'submit').click()
    time.sleep(0.5)
    # Should not silently redirect to index on successful injection
    assert 'index.php' not in driver.current_url


def test_ui_links(driver, base_url):
    driver.get(base_url + '/login.php')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Register')))
    link = driver.find_element(By.LINK_TEXT, 'Register')
    link.click()
    time.sleep(0.5)
    assert 'register.php' in driver.current_url
    driver.get(base_url + '/register.php')
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Login')))
    link2 = driver.find_element(By.LINK_TEXT, 'Login')
    link2.click()
    time.sleep(0.5)
    assert 'login.php' in driver.current_url
