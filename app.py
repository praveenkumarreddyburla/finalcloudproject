from flask import Flask, request, render_template_string, redirect, url_for
import boto3
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)

# Replace 'YOUR_BUCKET_NAME' with your actual S3 bucket name.
S3_BUCKET = 'term-assignment-image-recog'

s3 = boto3.client('s3')
aws_api_client=boto3.client('apigateway',region_name='us-east-2')

UPLOAD_FORM = """
<!doctype html>
<html>
<head><title>File Upload</title></head>
<body>
<h2>Upload File to S3</h2>
<form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit">
</form>
</body>
</html>
"""

SUCCESS_MESSAGE = """
<!doctype html>
<html>
<head><title>Upload Successful</title></head>
<body>
<h2>Successful upload</h2>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UPLOAD_FORM)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    try:
        s3.upload_fileobj(file, S3_BUCKET, filename)
        apis = aws_api_client.get_rest_apis()['items']
        for api in apis:
            if api['name'] == "SimpleApiGateway":
                process_url=f"https://{api['id']}.execute-api.us-east-2.amazonaws.com/prod"+"/service";
                headers = {'Content-Type': 'application/json'}
                payload = {"input_bucket": "term-assignment-image-recog" , "input_key": "dog.jpg" }
                result = requests.post(process_url, json=payload, headers=headers)
                if result.status_code == 200:
                    return render_template_string(f"<h2>Processed successfully!!! </h2>")
        # Redirect to the success page
        return redirect(url_for('upload_success'))
    except Exception as e:
        return f'<h2>Failed to upload file.</h2><p>{e}</p>'

@app.route('/upload_success')
def upload_success():
    return render_template_string(SUCCESS_MESSAGE)

if __name__ == '__main__':
    app.run(debug=True)
