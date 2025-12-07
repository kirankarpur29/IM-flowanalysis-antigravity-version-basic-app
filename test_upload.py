import urllib.request
import urllib.parse
import json
import os

# Create a dummy STL file
stl_content = b'solid dummy\nendsolid dummy'
with open('test_dummy.stl', 'wb') as f:
    f.write(stl_content)

url = 'http://localhost:8000/geometry/upload'
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

# Construct multipart body manually since we don't have requests
data = b''
data += b'--' + boundary.encode() + b'\r\n'
data += b'Content-Disposition: form-data; name="file"; filename="test_dummy.stl"\r\n'
data += b'Content-Type: application/octet-stream\r\n\r\n'
data += stl_content + b'\r\n'
data += b'--' + boundary.encode() + b'--\r\n'

req = urllib.request.Request(url, data=data)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
finally:
    if os.path.exists('test_dummy.stl'):
        os.remove('test_dummy.stl')
