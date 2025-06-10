# resume-drive-manager
Automated tool to download resumes from Gmail and organize them in Google Drive. Perfect for recruiters and hiring managers to streamline their resume management process.
# Resume Downloader and Drive Uploader

A Python script that automatically downloads resumes from Gmail and uploads them to Google Drive. This tool is particularly useful for recruiters and hiring managers who need to organize resumes from job applications.

## Features

- 🔍 Search Gmail for specific job post emails
- 📎 Download resume attachments (PDF, DOC, DOCX)
- ☁️ Upload resumes to Google Drive
- 📁 Keep both local and cloud copies
- ⏱️ Add timestamps to avoid duplicate files
- 📝 Detailed logging of all operations

## Prerequisites

- Python 3.7 or higher
- Gmail account with App Password enabled
- Google Cloud Project with Drive API enabled
- Google Drive account

## Installation


2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up Gmail App Password:
   - Go to your Google Account settings
   - Navigate to Security > 2-Step Verification
   - At the bottom, click on "App passwords"
   - Select "Mail" and "Other (Custom name)"
   - Name it "Resume Downloader"
   - Copy the generated password

4. Set up Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable the Google Drive API
   - Create a service account:
     - Go to "IAM & Admin" > "Service Accounts"
     - Click "Create Service Account"
     - Name it "resume-uploader"
     - Grant it the "Editor" role
   - Create a key:
     - Click on the service account
     - Go to "Keys" tab
     - Click "Add Key" > "Create new key"
     - Choose JSON format
     - Download the key file
   - Rename the downloaded JSON to `service_account.json`
   - Place it in the project directory

5. Share Google Drive folder:
   - Open `service_account.json`
   - Find the `client_email` field
   - Copy the email address
   - Create a folder in your Google Drive
   - Share the folder with the service account email
   - Give it "Editor" access
   - Uncheck "Notify people" when sharing

## Configuration

Edit `job_resume_downloader.py` and update these variables:
```python
EMAIL = "your.email@gmail.com"  # Your Gmail address
PASSWORD = "your-app-password"  # Your Gmail App Password
DOWNLOAD_DIR = "downloaded_resumes"  # Local folder for downloads
```

## Usage

1. Run the script:
```bash
python job_resume_downloader.py
```

2. Enter the required information when prompted:
   - Job post subject line (to search in Gmail)
   - Google Drive folder name (where to store resumes)

3. The script will:
   - Search your Gmail for matching emails
   - Download resume attachments
   - Upload them to Google Drive
   - Keep local copies
   - Show a summary of operations

## Output

- Downloaded resumes are stored in the `downloaded_resumes` folder
- Files are uploaded to your specified Google Drive folder
- A log file `resume_downloader.log` tracks all operations
- Console output shows progress and summary

## File Structure

```
resume-downloader/
├── job_resume_downloader.py    # Main script
├── service_account.json        # Google Cloud credentials
├── requirements.txt           # Python dependencies
├── downloaded_resumes/        # Local storage folder
└── resume_downloader.log      # Operation logs
```

## Dependencies

- `google-auth`
- `google-api-python-client`
- `imaplib` (built-in)
- `email` (built-in)

## Security Notes

- Never commit `service_account.json` to version control
- Keep your Gmail App Password secure
- The script only processes PDF, DOC, and DOCX files
- All operations are logged for audit purposes

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Cloud Platform
- Gmail API
- Google Drive API
- Python community


## Author

Your Name
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com 
