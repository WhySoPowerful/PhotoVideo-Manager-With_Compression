# Google Cloud Photo and Video Manager
A cloud-based photo and video management application that makes it easy for users to upload, manage, and organize their photos and videos in one place. Allowed File Formats: jpg, png, gif, mp4, webm.
## Requirements
Requires Python 3.8+.
## Dependencies
- Flask
- Flask-Admin
- google-cloud
- python-dotenv
- wtforms
- google-cloud-storage
- pillow
## Setup
1. `pip install -r requirements.txt`
2. Follow the following instructions to [Generate Google Cloud Credentials](https://stackoverflow.com/questions/75344294/how-to-generate-credentials-json-in-google-cloud-platform#answer-75344353)
3. Place google cloud credentials json file in `cloud_file_manager` with the name `credentials.json`
4. Modify `.env` file if necessary (Change GOOGLE_CLOUD_BUCKET_NAME to another name of your choice!)
## Run
1. From inside of the cloud_file_manager folder: `flask run`
