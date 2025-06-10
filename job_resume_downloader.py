import os
import imaplib
import email
from datetime import datetime
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resume_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
EMAIL = "sairamvuyyuru1511@gmail.com"
PASSWORD = "pwkk ycty tgdy hurv"  # Your Gmail App Password
DOWNLOAD_DIR = "downloaded_resumes"
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'  # You'll need to create this

def setup_directories():
    """Create necessary directories"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    logger.info(f"Created download directory: {DOWNLOAD_DIR}")

def authenticate_gmail():
    """Connect to Gmail"""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        logger.info("Successfully connected to Gmail")
        return mail
    except Exception as e:
        logger.error(f"Failed to connect to Gmail: {e}")
        raise

def authenticate_drive():
    """Authenticate with Google Drive using service account"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Successfully authenticated with Google Drive")
        return service
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Drive: {e}")
        raise

def search_job_emails(mail, job_subject):
    """Search for emails with specific job subject"""
    try:
        # Search for emails with the job subject
        search_criteria = f'SUBJECT "{job_subject}"'
        status, messages = mail.search(None, search_criteria)
        
        if status != 'OK':
            logger.error("Failed to search emails")
            return []
            
        email_ids = messages[0].split()
        logger.info(f"Found {len(email_ids)} emails matching the job subject")
        return email_ids
    except Exception as e:
        logger.error(f"Error searching emails: {e}")
        return []

def download_resumes(mail, email_ids):
    """Download resume attachments from emails"""
    downloaded_files = []
    
    for email_id in email_ids:
        try:
            # Fetch the email
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != 'OK':
                continue
                
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Get email details
            subject = email_message.get('Subject', 'No Subject')
            sender = email_message.get('From', 'Unknown Sender')
            logger.info(f"Processing email: {subject} from {sender}")
            
            # Process attachments
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                    
                if part.get('Content-Disposition') is None:
                    continue
                    
                filename = part.get_filename()
                if not filename:
                    continue
                    
                # Only process resume files
                if not filename.lower().endswith(('.pdf', '.doc', '.docx')):
                    continue
                    
                # Create unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"
                filepath = os.path.join(DOWNLOAD_DIR, unique_filename)
                
                # Save the attachment
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                    
                downloaded_files.append(unique_filename)
                logger.info(f"Downloaded: {unique_filename}")
                
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}")
            continue
            
    return downloaded_files

def upload_to_drive(drive_service, folder_id, files):
    """Upload files to Google Drive folder"""
    uploaded_count = 0
    for filename in files:
        try:
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            media = MediaFileUpload(
                file_path,
                mimetype='application/octet-stream',
                resumable=True
            )
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            uploaded_count += 1
            logger.info(f"Uploaded: {filename}")
        except Exception as e:
            logger.error(f"Error uploading {filename}: {e}")
            continue
    return uploaded_count

def get_or_create_folder(drive_service, folder_name):
    """Get existing folder or create new one"""
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            folder_id = items[0]['id']
            logger.info(f"Found existing folder: {folder_name}")
            return folder_id
            
        # Create new folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        folder_id = folder.get('id')
        logger.info(f"Created new folder: {folder_name}")
        return folder_id
        
    except Exception as e:
        logger.error(f"Error getting/creating folder: {e}")
        raise

def main():
    """Main function to run the resume downloader"""
    print("\nJob Resume Downloader")
    print("=" * 50)
    
    # Check for service account file
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"\nError: {SERVICE_ACCOUNT_FILE} not found!")
        print("\nTo use Google Drive upload, you need to:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com)")
        print("2. Create a new project or select existing one")
        print("3. Enable the Google Drive API")
        print("4. Create a service account")
        print("5. Download the service account key as JSON")
        print("6. Save it as 'service_account.json' in this directory")
        print("7. Share your Google Drive folder with the service account email")
        return
    
    # Get job details
    job_subject = input("\nEnter the job post subject line: ").strip()
    folder_name = input("Enter Google Drive folder name: ").strip()
    
    if not job_subject or not folder_name:
        print("Error: Both job subject and folder name are required")
        return
        
    try:
        # Setup
        setup_directories()
        
        # Connect to Gmail
        mail = authenticate_gmail()
        
        # Search for job emails
        email_ids = search_job_emails(mail, job_subject)
        if not email_ids:
            print(f"No emails found with subject: {job_subject}")
            return
            
        # Download resumes
        print("\nDownloading resumes...")
        downloaded_files = download_resumes(mail, email_ids)
        if not downloaded_files:
            print("No resumes found in the emails")
            return
            
        # Upload to Drive
        print("\nUploading to Google Drive...")
        drive_service = authenticate_drive()
        folder_id = get_or_create_folder(drive_service, folder_name)
        uploaded_count = upload_to_drive(drive_service, folder_id, downloaded_files)
        
        # Summary
        print("\nDownload Summary:")
        print(f"- {len(downloaded_files)} resumes downloaded")
        print(f"- {uploaded_count} files uploaded to Google Drive")
        print(f"- Files are in folder: {folder_name}")
        print(f"- Local copies are in: {os.path.abspath(DOWNLOAD_DIR)}")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        print(f"\nAn error occurred: {e}")
    finally:
        if 'mail' in locals():
            try:
                mail.logout()
            except:
                pass

if __name__ == "__main__":
    main() 