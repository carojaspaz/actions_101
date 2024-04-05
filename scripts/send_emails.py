import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_email(username, password, subject, body, to, from_address, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition",
                    f"attachment; filename= {attachment_path}")
    msg.attach(part)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(username, password)
    text = msg.as_string()
    server.sendmail(from_address, to.split(','), text)
    server.close()


parser = argparse.ArgumentParser(description='Send emails.')
parser.add_argument('--username', type=str, help='Username.')
parser.add_argument('--password', type=str, help='Password.')
parser.add_argument('--from_address', type=str, help='From address.')
parser.add_argument('--to_addresses', type=str, help='Email address.')
parser.add_argument('--body', type=str, help='Body for emails.')
parser.add_argument('--attachment_path', type=str,
                    help='Path for the attachment')

args = parser.parse_args()

send_email(args.username, args.password, "GitHub Actions Demo 04 - Script",
           args.body, args.to_addresses, args.from_address, args.attachment_path)
