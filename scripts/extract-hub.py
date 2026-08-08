import json, re
with open('/home/z/my-project/tool-results/openinbox-hub.json') as f:
    d = json.load(f)
html = d.get('data',{}).get('html','')
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'&amp;', '&', text)
text = re.sub(r'&lt;', '<', text)
text = re.sub(r'&gt;', '>', text)
text = re.sub(r'&#x27;', "'", text)
text = re.sub(r'&quot;', '"', text)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:10000])
