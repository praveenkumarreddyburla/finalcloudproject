from flask import Flask, render_template_string, request, redirect, url_for
import boto3
from werkzeug.utils import secure_filename
import requests

# Initialize Flask application
web_app = Flask(__name__)

# AWS S3 bucket configuration
bucket_image = 'term-assignment-image-recog'

# AWS Clients
aws_s3_client = boto3.client('s3', region_name='us-east-2')


# HTML templates for the web interface
Image_upload = """
<!doctype html>
<html>
<head><title>Upload image</title></head>
<body>
<h2>Upload image</h2>
<form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="document" accept=".pdf">
    <button type="submit">Upload Image</button>
</form>
</body>
</html>
"""

next_image = """
<!doctype html>
<html>
<head><title>Success</title></head>
<body>
<h2>Upload Completed</h2>
<a href="/">Upload Another</a>
</body>
</html>
"""

@web_app.route('/')
def home():
    return render_template_string(Image_upload)

@web_app.route('/upload', methods=['POST'])
def file_upload():
    image_file = request.files.get('document')
    if image_file and image_file.filename.endswith('.pdf'):
        safe_name = secure_filename(image_file.filename)
        try:
            aws_s3_client.upload_fileobj(image_file, bucket_image, safe_name)
            apis = aws_api_client.get_rest_apis()['items']
            for api in apis:
                if api['name'] == "SimpleApiGateway":
                    process_url=f"https://{api['id']}.execute-api.us-east-2.amazonaws.com/prod"+"/service";
            headers = {'Content-Type': 'application/json'}
            payload = {"input_bucket": bucket_image, "input_bucket_file": safe_name}
            result = requests.post(process_url, json=payload, headers=headers)
            if result.status_code == 200:
                return render_template_string(f"<h2>Processed successfully: {safe_name}</h2>")
            else:
                return render_template_string(next_image)
        except Exception as error:
            return str(error)
    return redirect(url_for('home'))

if __name__ == '__main__':
    web_app.run(debug=True)
