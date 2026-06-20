import os

d = r'd:\news-site\Django-Shop'
for root, dirs, files in os.walk(d):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "{% extends 'shared/_layout.html' %}" in content:
                    content = content.replace("{% extends 'shared/_layout.html' %}", "{% extends 'shared/base.html' %}")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filepath}")
            except Exception as e:
                pass
