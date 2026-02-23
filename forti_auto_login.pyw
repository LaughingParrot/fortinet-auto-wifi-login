from dotenv import load_dotenv
import os
import subprocess
import sys
import traceback
import time
import ctypes
# import requests
from win11toast import toast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ---------- SAFE ENV LOADING (works for EXE & script) ----------
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
ENV_PATH = os.path.join(BASE_DIR, "fortinet.config")

if os.path.isfile(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    load_dotenv()
# ================== CREDENTIALS ===================
def get_credentials():
    import tkinter as tk

    result = {"user": "", "pwd": ""}

    root = tk.Tk()
    root.title("BITS WIFI Login")
    root.iconbitmap(os.path.join(BASE_DIR, "_internal", "app.ico"))
    root.resizable(False, False)

    root.geometry("320x190")
    root.eval('tk::PlaceWindow . center')

    tk.Label(root, text="Enter your Fortinet credentials").pack(pady=(8, 2))

    tk.Label(root, text="Username").pack()
    user_entry = tk.Entry(root, width=30)
    user_entry.pack()

    tk.Label(root, text="Password").pack(pady=(6, 0))
    pwd_entry = tk.Entry(root, show="*", width=30)
    pwd_entry.pack()

    # Guidance line
    tk.Label(
        root,
        text="Change Configurations in Fortinet.config",
        fg="black"
    ).pack(pady=(8, 0))

    def submit():
        result["user"] = user_entry.get().strip()
        result["pwd"]  = pwd_entry.get().strip()
        root.destroy()

    tk.Button(root, text="OK", width=10, command=submit).pack(pady=8)

    user_entry.focus()
    root.mainloop()

    return result["user"], result["pwd"]

# ===================== CONFIG =====================
def fix_config(data):
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for key, value in data.items():
            if value is None:
                value = ""
            f.write(f'{key}="{value}"\n')

config = {
    "TARGET_SSID": "BITS-STUDENT",
    "PORTAL_URL": "https://fw.bits-pilani.ac.in:8090/login?",
    "INTERNET_TEST_URL": "https://fw.bits-pilani.ac.in:8090/keepalive?",
    # "ICON_PNG": "FortinetLogo.png",
    "APP_ID": "Fortinet Auto Login",
    "WAIT_TIME": "4",
    "MAX_RETRIES": "3"
}
def load_and_fix_config():
    update=False
    for key, default in config.items():
        val = os.getenv(key)
        if not val or not val.strip():
            val = default
            update=True
        config[key]=val
    user = os.getenv("W_USERNAME")
    pwd = os.getenv("W_PASSWORD")
    if(user is None or pwd is None or not user.strip() or not pwd.strip()):
        (user,pwd)=get_credentials()
        update=True
    config["W_USERNAME"] = user
    config["W_PASSWORD"] = pwd
    if update:
        fix_config(config)

load_and_fix_config()

TARGET_SSID = config["TARGET_SSID"]
PORTAL_URL = config["PORTAL_URL"]
INTERNET_TEST_URL = config["INTERNET_TEST_URL"]
APP_ID = config["APP_ID"]

# ICON_PNG= None
# if ICON_PNG:
#     if not os.path.isabs(ICON_PNG):
#         ICON_PNG = os.path.join(BASE_DIR, ICON_PNG)
        
WAIT_TIME = int(config["WAIT_TIME"])
MAX_RETRIES = int(config["MAX_RETRIES"])

USERNAME = config["W_USERNAME"]
PASSWORD = config["W_PASSWORD"]

# ==================================================
CREATE_NO_WINDOW = 0x08000000

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

# ---------- SAFE NOTIFY ----------
import threading
import queue

_notify_queue = queue.Queue()
_notify_thread_started = False

TAG = "fortinet_status"
GROUP = "fortinet_group"
def _notify_worker():
    while True:
        title, message = _notify_queue.get()

        if title is None:
            break  # shutdown signal

        try:
            kwargs = {
                "app_id": APP_ID,
                "tag": TAG,
                "group": GROUP,
                "duration": "short"
            }

            # if ICON_PNG and os.path.isfile(ICON_PNG):
            #     kwargs["image"] = ICON_PNG

            toast(title, message, **kwargs)

        except Exception as e:
            print("Toast error:", e)

def notify(title, message):
    global _notify_thread_started

    # Start worker only once
    if not _notify_thread_started:
        threading.Thread(target=_notify_worker, daemon=True).start()
        _notify_thread_started = True

    # Remove any pending notifications (latest wins)
    while not _notify_queue.empty():
        try:
            _notify_queue.get_nowait()
        except queue.Empty:
            break

    _notify_queue.put((title, message))

# def notify(title, message):

#     # def _show():
#         try:
#             if ICON_PNG and os.path.isfile(ICON_PNG):
#                 toast(title, message, app_id=APP_ID, image=ICON_PNG, duration="short")
#             else:
#                 toast(title, message, app_id=APP_ID, duration="short")
#         except Exception as e:
#             print("Toast error:", e)
#     # threading.Thread(target=_show, daemon=True).start()


# ---------- VALIDATION ----------
def validate_config():
    if not TARGET_SSID:
        notify("Configuration Error", "TARGET_SSID not set in .env")
        return False
    if not PORTAL_URL:
        notify("Configuration Error", "PORTAL_URL not set in .env")
        return False
    if not USERNAME or not PASSWORD:
        notify("Configuration Error", "Username or Password missing")
        return False
    return True


# ---------- SSID CHECK ----------
def connected_to_target():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            creationflags=CREATE_NO_WINDOW
        ).stdout

        for line in result.splitlines():
            if line.strip().startswith("SSID") and "BSSID" not in line:
                current_ssid = line.split(":", 1)[1].strip()
                return current_ssid == TARGET_SSID

        return False

    except Exception as e:
        notify("WiFi Error", f"SSID detection failed:\n{str(e)}")
        return False
#==========INTERNET CONNNECTION CHECK=============
# def net_check(driver):
#     try:
#         driver.get(INTERNET_TEST_URL)
#         state = driver.execute_script("return document.readyState")

#         if state != "complete":
#             notify("Internet Status", "Page did not load properly")
#             return False
#         current = driver.current_url.lower()
#         title = driver.title.lower()
#         source = driver.page_source.lower()

#         if "err_empty_response" in source:
#             return False
#         if "site can’t be reached" in title or "can't be reached" in title:
#             return False
#         if "connection reset" in source or "timed out" in source:
#             return False
#         if INTERNET_TEST_URL in current:
#             return True
#         else:
#             return False
#     except TimeoutException:
#         current_url = driver.current_url.lower()
#         if current_url.startswith(INTERNET_TEST_URL.lower()):
#             return True
#         else:
#             # Likely wrong credentials or portal failure
#             return False
        
def new_driver():
    driver = None
    options = Options()
    options.add_argument("--headless=new")
    options.page_load_strategy = "eager"
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-features=msEdgeAccountConsistency")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")
    try:
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(15)
        return driver
    except Exception as e:
        notify("Driver Error", str(e))
        return None
    

# ---------- LOGIN ----------
def login(driver,start_time):


    wait = WebDriverWait(driver, WAIT_TIME+5)

    try:
        driver.get(PORTAL_URL)

        wait.until(EC.presence_of_element_located((By.ID, "ft_pd")))

        driver.find_element(By.ID, "ft_un").clear()
        driver.find_element(By.ID, "ft_un").send_keys(USERNAME)

        driver.find_element(By.ID, "ft_pd").clear()
        driver.find_element(By.ID, "ft_pd").send_keys(PASSWORD)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        total_time = round(time.perf_counter() - start_time, 2)
        current_url = driver.current_url.lower()
        if current_url.startswith(INTERNET_TEST_URL.lower()):

            total_time = round(time.perf_counter() - start_time, 2)

            notify(
                "Login Successful",
                f"Connected to {TARGET_SSID}\nTime: {total_time} seconds"
            )
            # driver.delete_all_cookies()
            return True

        else:
            # Wrong credentials or portal rejected
            # driver.delete_all_cookies()
            return False

    except TimeoutException:

        current_url = driver.current_url.lower()

        if current_url.startswith(INTERNET_TEST_URL.lower()):

            total_time = round(time.perf_counter() - start_time, 2)

            notify(
                "Already Authenticated",
                f"Time: {total_time} seconds"
            )

            return True

        else:
            # Likely wrong credentials or portal failure
            return False

    except Exception:
        total_time = round(time.perf_counter() - start_time, 2)
        notify("Selenium Error",
               f"{traceback.format_exc()[:250]}\nTime: {total_time}s")
        return None

def login_with_retries(start_time):
    global USERNAME, PASSWORD
    driver=None
    try:
        driver = new_driver()
        # if net_check(driver):
        #     total_time = round(time.perf_counter() - start_time, 2)
        #     notify("WiFi Status",
        #         f"Already connected to {TARGET_SSID}\nTime: {total_time} seconds")
        #     return True
        


        for attempt in range(1, MAX_RETRIES + 1):
            result = login(driver,start_time)

            if result is True:
                return True
            # ERROR → stop immediately
            if result is None:
                notify("Login Error", "Driver or unexpected failure.")
                return False
            # FAILED LOGIN (likely wrong credentials)
            if attempt < MAX_RETRIES:

                notify(
                    "Login Failed",
                    f"Attempt {attempt}/{MAX_RETRIES}\nPlease re-enter credentials."
                )

                # Ask new credentials (GUI or console)
                new_user, new_pwd = get_credentials()

                if not new_user or not new_pwd:
                    notify("Login Cancelled", "No credentials provided.")
                    return False

                # Update runtime credentials
                USERNAME = new_user
                PASSWORD = new_pwd

                # Update config file
                config["W_USERNAME"] = new_user
                config["W_PASSWORD"] = new_pwd
                fix_config(config)

            else:
                # Final failure
                notify(
                    "Login Failed",
                    f"Maximum attempts reached ({MAX_RETRIES})."
                )
                return False
        return False

    except Exception as e:
        notify("Driver Error", str(e))
        return None
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ===================== MAIN =====================

if __name__ == "__main__":
    start_time = time.perf_counter()

    if not validate_config():
        sys.exit(1)

    if not connected_to_target():
        total_time = round(time.perf_counter() - start_time, 2)
        notify("WiFi Status",
               f"Not connected to {TARGET_SSID}\nTime: {total_time} seconds")
        sys.exit(0)
    # if net_check():
    #     total_time = round(time.perf_counter() - start_time, 2)
    #     notify("Internet Status",
    #             f"Already connected to Internet\nTime: {total_time} seconds")
    #     os._exit(0)

    login_with_retries(start_time)
    time.sleep(2)
    # fortinet_login()
    sys.exit(0)
