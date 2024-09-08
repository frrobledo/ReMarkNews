import subprocess
from datetime import datetime


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
    