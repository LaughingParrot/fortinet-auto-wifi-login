import os
import subprocess
import tempfile
import ctypes
import sys

CREATE_NO_WINDOW = 0x08000000
TASK_NAME = "Fortinet Auto Login"


# -------------------------------------------------
# Check if script is running as Administrator
# -------------------------------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# -------------------------------------------------
# Install / Update Scheduled Task
# -------------------------------------------------
def install_scheduled_task():

    # ---- 1) Require admin privileges ----
    if not is_admin():
        print("Please run this installer as Administrator.")
        return

    # ---- 2) Locate EXE in current folder ----
    exe_name = "Fortinet Auto Login.exe"
    exe_path = os.path.join(os.getcwd(), exe_name)

    if not os.path.isfile(exe_path):
        print("EXE not found:", exe_path)
        return

    base_dir = os.path.dirname(exe_path)

    # ---- 3) Locate XML template ----
    def resource_path(filename):
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS   # temp extraction folder
        else:
            base = os.path.dirname(__file__)
        return os.path.join(base, filename)
    template_path = resource_path("FortinetTaskTemplate.xml")

    if not os.path.isfile(template_path):
        print("XML template not found:", template_path)
        return

    # ---- 4) Load XML template ----
    try:
        with open(template_path, "r", encoding="utf-16") as f:
            xml_data = f.read()
    except Exception as e:
        print("Failed to read XML template:", e)
        return

    # ---- 5) Replace placeholders with real paths ----
    xml_data = xml_data.replace("__EXE_PATH__", exe_path)
    xml_data = xml_data.replace("__WORK_DIR__", base_dir)

    if "__EXE_PATH__" in xml_data:
        print("Placeholder replacement failed.")
        return

    # ---- 6) Write temporary XML file ----
    temp_xml = os.path.join(tempfile.gettempdir(), "FortinetTask.xml")

    try:
        with open(temp_xml, "w", encoding="utf-16") as f:
            f.write(xml_data)
    except Exception as e:
        print("Failed to write temp XML:", e)
        return

    # ---- 7) Check if task already exists ----
    query = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    task_exists = (query.returncode == 0)

    if task_exists:
        # ---- Stop running instance (if any) ----
        subprocess.run(
            ["schtasks", "/End", "/TN", TASK_NAME],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # ---- Delete old task ----
        subprocess.run(
            ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # ---- 8) Create the new task ----
    result = subprocess.run(
        ["schtasks", "/Create", "/TN", TASK_NAME, "/XML", temp_xml, "/F"],
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW
    )

    if result.returncode != 0:
        print("Task creation failed:")
        print(result.stderr.strip())
        return

    # ---- 9) Verify installation ----
    verify = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if verify.returncode != 0:
        print("Task not found after installation.")
        return

    print("Scheduled task installed successfully.")


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    install_scheduled_task()