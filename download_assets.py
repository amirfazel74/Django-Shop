import os
import urllib.request
import re

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
JS_DIR = os.path.join(STATIC_DIR, 'js', 'vendors')
CSS_DIR = os.path.join(STATIC_DIR, 'css')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts', 'vazirmatn')

os.makedirs(JS_DIR, exist_ok=True)
os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

js_files = {
    'jquery.min.js': 'https://code.jquery.com/jquery-3.6.0.min.js',
    'sweetalert2.min.js': 'https://cdn.jsdelivr.net/npm/sweetalert2@11',
    'alpine.min.js': 'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js'
}

for filename, url in js_files.items():
    print(f"Downloading {filename}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open(os.path.join(JS_DIR, filename), 'wb') as f:
            f.write(response.read())

print("Downloading Vazirmatn font css...")
font_css_url = 'https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css'
req = urllib.request.Request(font_css_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    css_content = response.read().decode('utf-8')

# Find all url(...) in css
font_urls = re.findall(r"url\('([^']+)'\)", css_content)
base_url = 'https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/'

for rel_url in font_urls:
    if rel_url.endswith('.woff2') or rel_url.endswith('.woff') or rel_url.endswith('.ttf'):
        full_url = base_url + rel_url
        filename = os.path.basename(rel_url)
        print(f"Downloading font {filename}...")
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                with open(os.path.join(FONTS_DIR, filename), 'wb') as f:
                    f.write(response.read())
        except Exception as e:
            print(f"Failed to download {filename}: {e}")

# Replace font URLs in CSS to point to local
# The original CSS has format url('fonts/webfonts/Vazirmatn-Thin.woff2')
# We will replace 'fonts/webfonts/' with '../fonts/vazirmatn/' or just adjust it
css_content = re.sub(r"url\('[^']+/([^']+)'\)", r"url('../fonts/vazirmatn/\1')", css_content)

with open(os.path.join(CSS_DIR, 'Vazirmatn-font-face.css'), 'w', encoding='utf-8') as f:
    f.write(css_content)

print("Done downloading all assets.")
