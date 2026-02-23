# Fortinet Auto Wi-Fi-Login
Automatically detects disconnection and regularly sign-in on Fortinet Firewall as used by BITS Pilani

## Features
1) Removes the need to manually open and sign in on the Firewall using browser.
2) Has various checks already in place to have smooth login experience in background with notifications.
3) The file is small, efficient and configurable without code reviewing using configurable file.

## Disclaimer
This project is an independent tool and is not affiliated with,
endorsed by, or associated with Fortinet, Inc.
Fortinet is a trademark of Fortinet, Inc.

## Background
The new Fortinet Firewall requires user to manually sign-in in every 4 hours again and again in order to stay connected. This hinders user experience especially when streaming videos, attending some meet, etc. Moreover; sometimes, there isn't any option to reconnect immediately after disconnection.

This project is built completely in python with knowledge base of chatgpt and provides both the executables and code files for further development.
The project is sincerely debugged to ensure the user faces no problem at anytime during the usage of the application in background.

Internally, it works on Windows Task Scheduler with custom event trigger, having specific event for which Wi-Fi connection to captive portal fails to reconnect immediately as action required notification comes. The login application run on selenium web-driver without console which simulates the user action of posting the request to the login webpage to get access to internet.
The code detects the ssid of the network in order to only run on specified network settings. Further, the code is protected from infinite loop in events of failure, the repetitions are limited by default. The configurable file is created and read after first run in order to have some manual changes (if needed) by the user. GUI is basic and is based on tkinter python standard library. It uses separate thread for win 11 style notifications using win11toast. Comments are intentionally provided or left for the understanding of developer. At last, also displays the total time taken in the execution of program to inspect if any vulnerabilities present. The file runs in less than 10 seconds on average with size of approx. 50 MB.

## Installation (Executable)
Prerequisite: Windows 11
### Steps
1) Download the .zip file
2) Extract it at the place you want to run it from.
3) Open task scheduler as administrator to schedule it on Task Scheduler.
4) Run the application for first time. A gui asking user credentials will occur.
5) If credentials will fail to login, it will show attempt failure and will again ask to submit credentials.
6) If the file will run and show login succeeded with time taken in case of good event or post error in case of any unknown event.
7) One fortinet.config file is made available to tweak with the waiting time and other stuff later.

## Development Prerequisites
- Windows 11 (Used: Windows 11 25H2)
- Python 3.10+ (Used: Python 3.14)
- Git
- Libraries used:
    1) Pyinstaller 6.19.0
    2) Selenium 4.40.0
    3) Win11Toast 0.36.3
    4) python-dotenv 1.2.1

*requirements.txt is intentionally version-less to have latest python libs to use as changes are subtle, code probably will work.


## Development Setup
1. Clone the repository:
```bash
git clone https://github.com/LaughingParrot/fortinet-auto-Wi-Fi-login.git Fortinet-BITS-Wi-Fi-Login
cd Fortinet-BITS-Wi-Fi-Login
```
2.  Make the virtual environment (preferred, otherwise can be skipped)
```bash
python -m venv forti_env
```
3. Install the required libraries
```bash
pip install -r requirements.txt
```
4. Run the applications:
```bash
python LoginScheduler.py
```
and
```bash
pythonw forti_auto_login.pyw

## Notes
1) The application till now is not tested with any VPN and ensure that while using it.
2) The task is scheduled in Task Scheduler Application->Task Scheduler Library (in explorer pane, left side by default) with name "Fortinet Auto Login" (appear on right side with description). In case of unexpected event or for removal, delete this task.
3) Under properties of the above task, configure it to run on BITS Student Wi-Fi to be more specific on scheduling.
4) The task run in 3:30 hr automatically, in case of disconnection and also when user log in on windows.
5) After scheduling, keep in mind and do not remove the application without deleting the task, to mitigate confusion on OS side.
6) Initially, also tried using requests library, but the TCL connection used would not directly work with requests. Need improvements.

## License
This project is licensed under the MIT License — see the LICENSE file for details.
## Third-Party Licenses
This project uses third-party libraries. See THIRD_PARTY_LICENSES.txt for details.