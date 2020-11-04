from socket import gaierror
import requests
import smtplib
import os

from requests.exceptions import ConnectTimeout
from requests.exceptions import ConnectionError

from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from time import sleep
# from daemonize import Daemonize


# Setup pid file

base_dir = os.getcwd()
pid_file = "test.pid"
pid = os.path.join(base_dir, pid_file)


def web_availability():
    # url="http://172.22.0.2:8080"
    url = "http://192.168.100.14:8088/blah"
    try:
        response = requests.get(url, timeout=3)
        status = response.status_code
        headers = response.headers

        # format html rep to user friendly string
        headers = str(headers).replace("\'", "").replace("{", "").replace("}", "")
        
    except (ConnectionError, ConnectTimeout):
        print("connection error")
        headers = "Connection Error"
        status = "No Status/Site might be down"

    return headers, status


def send_email(sender, passwd, recipient, headers, status, count):

    # Server Details
    smtp_server = os.environ['SMTP_SERVER']
    port = 465

    # Msg creation
    message = "Response Headers: " + str(headers) + "\n"+"Status: " + str(status) + "\n" + "Missing response count: " + str(count)

    msg = MIMEMultipart()
    msg['Subject'] = Header("Sent from python", 'utf-8')
    sender_title = "Python Automated Email notification"
    msg['From'] = formataddr((str(Header(sender_title, 'utf-8')), sender))
    msg['To'] = recipient
    msg.attach(MIMEText(message))

    if status != 200:

        count += 1
        try:
            # send your message with credentials specified above

            server = smtplib.SMTP_SSL(smtp_server, 465)
            server.login(sender, passwd)
            server.sendmail(sender, [recipient], msg.as_string())
            server.quit()

        # tell the script to report if your message was sent or which errors need to be fixed 
            print('Email notification sent')
        except (gaierror, ConnectionRefusedError):
            print('Failed to connect to the server. Bad connection settings?')
        except smtplib.SMTPServerDisconnected:
            print('Failed to connect to the server. Wrong user/password?')
        except smtplib.SMTPException as e:
            print('SMTP error occurred: ' + str(e))

    return count
        

# if __name__ == "__main__":
def main():
    count = 0
    while True:

        # Define mail sender / recipient

        sender = os.environ['SENDER']
        recipient = os.environ['RECIPIENT']
        passwd = os.environ['PASSWORD']

        headers, status = web_availability()
        count = send_email(sender, passwd, recipient, headers, status, count)
        
        print(count)
        sleep(10)


# daemon = Daemonize(app="test_app", pid=pid, action=main)
# daemon.start()
main()