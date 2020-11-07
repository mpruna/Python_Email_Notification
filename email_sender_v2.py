from socket import gaierror
import datetime as dt
import logging
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
from daemonize import Daemonize


# Setup pid file

base_dir = os.getcwd()
pid_file = "test.pid"
pid = os.path.join(base_dir, pid_file)

# Setup logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
log_file = os.path.join(base_dir, "script_exec.log")
fh = logging.FileHandler(log_file, "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def web_availability():

    # url = "http://172.22.0.2:8080"
    # url = "http://192.168.100.14:8088/blah"
    url = "http://192.168.100.14:8080/"

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


def send_email(message):

    # Server Details
    smtp_server = os.environ['SMTP_SERVER']
    port = 465

    # Define mail sender / recipient

    sender = os.environ['SENDER']
    recipient = os.environ['RECIPIENT']
    passwd = os.environ['PASSWORD']

    msg = MIMEMultipart()
    msg['Subject'] = Header("Sent from python", 'utf-8')
    sender_title = "Python Automated Email notification"
    msg['From'] = formataddr((str(Header(sender_title, 'utf-8')), sender))
    msg['To'] = recipient
    msg.attach(MIMEText(message))

    try:
        # send your message with credentials specified above

        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(sender, passwd)
        server.sendmail(sender, [recipient], msg.as_string())
        # server.sendmail(sender, [recipient], msg)
        server.quit()

        # tell the script to report if your message was sent or which errors need to be fixed
        e_msg = 'Email notification sent'
        print(e_msg)
        logger.debug(e_msg)

    except (gaierror, ConnectionRefusedError):
        e_msg = 'Failed to connect to the server. Bad connection settings?'
        print(e_msg)
        logger.debug(e_msg)

    except smtplib.SMTPServerDisconnected:
        e_msg = 'Failed to connect to the server. Wrong user/password?'
        print(e_msg)
        logger.debug(e_msg)

    except smtplib.SMTPException as e:
        e_msg = 'SMTP error occurred: ' + str(e)
        print(e_msg)
        logger.debug(e_msg)


def create_email(headers, status, count, was_down):

    date = dt.datetime.now().strftime('%y-%m-%d %a %H:%M:%S')

    # Msg creation
    message = '{0} {1} {2} {4}'.format('Response Headers ', headers, '\n',
                                       'Status: ', status, '\n',
                                       'Count: ', count, '\n',
                                       'Date: ', date)
    if status != 200:
        count += 1

    if status != 200 and count <=3:
        logger.debug(date)
        send_email(message)
        was_down = True

    elif status == 200 and was_down:
        message = "Service up and running"
        print(message)
        send_email(message)
        was_down = False
        count = 0


    logger.debug(message)

    return was_down, count
        

# if __name__ == "__main__":
def main():
    count = 0
    was_down = True
    while True:

        headers, status = web_availability()
        was_down, count = create_email(headers, status, count, was_down)
        
        print("Consecutive down count", count)
        sleep(10)

daemon = Daemonize(app="test_app", pid=pid, action=main)
daemon.start()
# main()