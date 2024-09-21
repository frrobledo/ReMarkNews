import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import AuthError
import os

def upload_epub_to_dropbox(access_token, local_file_path, dropbox_file_path):
    """
    Upload an EPUB file to Dropbox
    
    :param access_token: Dropbox access token
    :param local_file_path: Path to the local EPUB file
    :param dropbox_file_path: The path where the file will be stored in Dropbox
    """
    try:
        # Create a Dropbox object
        dbx = dropbox.Dropbox(access_token)

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
        except AuthError:
            print("ERROR: Invalid access token")
            return

        # Open the local file
        with open(local_file_path, 'rb') as file:
            # Upload the file
            print(f"Uploading {local_file_path} to Dropbox as {dropbox_file_path}...")
            try:
                dbx.files_upload(file.read(), dropbox_file_path, mode=WriteMode('overwrite'))
            except Exception as e:
                print(f"Error uploading file: {str(e)}")
                return

        print("File successfully uploaded")

    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
# access_token = "YOUR_DROPBOX_ACCESS_TOKEN"
# local_file_path = "/path/to/your/local/epub/file.epub"
# dropbox_file_path = "/path/in/dropbox/file.epub"
# upload_epub_to_dropbox(access_token, local_file_path, dropbox_file_path)