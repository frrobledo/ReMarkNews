import subprocess
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

def upload_to_tablet(pdf_path, remarkable_path='/news/'):
    command = f"rmapi put '{pdf_path}' '{remarkable_path}/'"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully uploaded {pdf_path} to ReMarkable")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to upload {pdf_path} to ReMarkable: {e}")
        return False
    
def generate_folder(new_folder, main_folder='/news/'):
    command = f"rmapi mkdir {main_folder}{new_folder}"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Successfully created folder {new_folder} in {main_folder} in Remarkable')
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create folder {new_folder} to ReMarkable: {e}")
        return False
    

def send_pdfs_using_pdf2rm(pdf_files):
    # Ensure the pdf2rm.sh script is in the same directory as the main.py file
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf2rm.sh')

    if not os.path.exists(script_path):
        print(f"Error: pdf2rm.sh script not found at {script_path}")
        return False

    # Prepare the command to run the bash script
    command = [script_path] + pdf_files

    try:
        # Run the script with the PDF files as arguments
        subprocess.run(command, check=True)
        print("PDFs processed and sent to ReMarkable tablet successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing and sending PDFs: {e}")
        return False



def send_epubs_using_epub2rm(epub_files):
    # Ensure the epub2rm.sh script is in the same directory as the main.py file
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epub2rm.sh')

    if not os.path.exists(script_path):
        print(f"Error: epub2rm.sh script not found at {script_path}")
        return False

    # Prepare the command to run the bash script
    command = [script_path] + epub_files

    try:
        # Run the script with the EPUB files as arguments
        subprocess.run(command, check=True)
        print("EPUBs processed and sent to ReMarkable tablet successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing and sending EPUBs: {e}")
        return False
    


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