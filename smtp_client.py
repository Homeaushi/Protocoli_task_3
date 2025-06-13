import os
import smtplib
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate


def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    return {
        'smtp_server': config.get('SMTP', 'server', fallback='smtp.gmail.com'),
        'smtp_port': config.getint('SMTP', 'port', fallback=587),
        'username': config.get('SMTP', 'username'),
        'password': config.get('SMTP', 'password'),
        'recipients': [r.strip() for r in config.get('EMAIL', 'recipients').split(',')],
        'subject': config.get('EMAIL', 'subject'),
        'attachments': [a.strip() for a in config.get('EMAIL', 'attachments').split(',')]
        if config.get('EMAIL', 'attachments') else []
    }


def read_message(message_path):
    with open(message_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_email(config, message_body):
    msg = MIMEMultipart()
    msg['From'] = config['username']
    msg['To'] = ', '.join(config['recipients'])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = config['subject']

    msg.attach(MIMEText(message_body, 'plain', 'utf-8'))

    for attachment in config['attachments']:
        if not os.path.isfile(attachment):
            print(f"Warning: Attachment file {attachment} not found. Skipping.")
            continue

        with open(attachment, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        filename = os.path.basename(attachment)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        msg.attach(part)

    return msg


def send_email(config, msg):
    try:
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.sendmail(
                config['username'],
                config['recipients'],
                msg.as_string()
            )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.ini')
    message_path = os.path.join(base_dir, 'message.txt')

    config = read_config(config_path)
    message_body = read_message(message_path)

    msg = create_email(config, message_body)
    send_email(config, msg)


if __name__ == '__main__':
    main()