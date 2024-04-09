# from flask import Flask, render_template_string, request, redirect, url_for
# import boto3
# from werkzeug.utils import secure_filename
# import requests

# # Initialize Flask application
# web_app = Flask(__name__)

# # AWS S3 bucket configuration
# bucket_image = 'term-assignment-image-recog'

# # AWS Clients
# aws_s3_client = boto3.client('s3')
# aws_api_client = boto3.client('', region_name='us-east-2')

# # HTML templates for the web interface
# Image_upload = """
# <!doctype html>
# <html>
# <head><title>Upload image</title></head>
# <body>
# <h2>Upload image</h2>
# <form action="/upload" method="post" enctype="multipart/form-data">
#     <input type="file" name="document" accept=".pdf">
#     <button type="submit">Upload Image</button>
# </form>
# </body>
# </html>
# """

# next_image = """
# <!doctype html>
# <html>
# <head><title>Success</title></head>
# <body>
# <h2>Upload Completed</h2>
# <a href="/">Upload Another</a>
# </body>
# </html>
# """

# @web_app.route('/')
# def home():
#     return render_template_string(Image_upload)

# @web_app.route('/upload', methods=['POST'])
# def file_upload():
#     image_file = request.files.get('document')
#     if image_file and image_file.filename.endswith('.pdf'):
#         safe_name = secure_filename(image_file.filename)
#         try:
#             aws_s3_client.upload_fileobj(image_file, bucket_image, safe_name)
#             apis = aws_api_client.get_rest_apis()['items']
#             for api in apis:
#                 if api['name'] == "SimpleApiGateway":
#                     process_url=f"https://{api['id']}.execute-api.us-east-2.amazonaws.com/prod"+"/service";
#             headers = {'Content-Type': 'application/json'}
#             payload = {"input_bucket": bucket_image, "input_bucket_file": safe_name}
#             result = requests.post(process_url, json=payload, headers=headers)
#             if result.status_code == 200:
#                 return render_template_string(f"<h2>Processed successfully: {safe_name}</h2>")
#             else:
#                 return render_template_string(next_image)
#         except Exception as error:
#             return str(error)
#     return redirect(url_for('home'))

# if __name__ == '__main__':
#     web_app.run(debug=True)

from flask import Flask, request, render_template_string, redirect, url_for
import boto3
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Replace 'YOUR_BUCKET_NAME' with your actual S3 bucket name.
S3_BUCKET = 'term-assignment-image-recog'

s3 = boto3.client('s3')

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
        # Redirect to the success page
        return redirect(url_for('upload_success'))
    except Exception as e:
        return f'<h2>Failed to upload file.</h2><p>{e}</p>'

@app.route('/upload_success')
def upload_success():
    return render_template_string(SUCCESS_MESSAGE)

if __name__ == '__main__':
    app.run(debug=True)
