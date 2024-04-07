from flask import Flask, request, render_template_string
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = 'AKIA47CRWVGW27WJ42GV'
AWS_SECRET_ACCESS_KEY = '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'
REGION_NAME = 'us-east-1'

s3_resource = boto3.resource(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)

# Predetermined bucket name
BUCKET_NAME = 'image-anaysis'

# HTML Form
HTML = '''
<!doctype html>
<title>Upload to S3</title>
<h2>Upload a file to S3</h2>
<form method=post enctype=multipart/form-data>
  File: <input type=file name=file>
  <input type=submit value=Upload>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Create S3 bucket if it doesn't exist
            if BUCKET_NAME not in [bucket.name for bucket in s3_resource.buckets.all()]:
                try:
                    s3_resource.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={
                        'LocationConstraint': REGION_NAME})
                    print(f"Bucket {BUCKET_NAME} created successfully.")
                except s3_resource.meta.client.exceptions.BucketAlreadyOwnedByYou:
                    print(f"Bucket {BUCKET_NAME} already exists.")
                except NoCredentialsError:
                    return "Credentials not available", 403
            
            # Upload file to the specified bucket
            s3_resource.Bucket(BUCKET_NAME).put_object(Key=file.filename, Body=file)
            return f'File {file.filename} uploaded to {BUCKET_NAME}.'
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)
