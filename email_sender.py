import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

def send_epub_email(sender_email, sender_password, recipient_email, subject, body, epub_path):
    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    # Open the file in bynary
    with open(epub_path, 'rb') as epub_file:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(epub_file.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {os.path.basename(epub_path)}',
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, text)
        print('Email sent successfully!')
    except Exception as e:
        print(f'An error occurred: {str(e)}')
    finally:
        server.quit()

# Example usage
# send_epub_email('your_email@gmail.com', 'your_password', 'recipient@example.com', 'EPUB Book', 'Here is the EPUB file you requested.', '/path/to/your/epub/file.epub')


def send_email_with_attachment(message, sender, receivers, password, pdf_path, subject='New article', type='pdf'):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)

    # Attach the message body
    msg.attach(MIMEText(message))

    # Attach the PDF file
    with open(pdf_path, 'rb') as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype=type)
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
        msg.attach(pdf_attachment)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receivers, msg.as_string())
        server.quit()
        print("Successfully sent email with PDF attachment")
    except smtplib.SMTPException as e:
        print(f"Error: unable to send email. {str(e)}")