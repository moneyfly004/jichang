import requests
import base64
import re
def fetch_nodes(sub_url):
    try:
        headers = {'User-Agent': 'v2rayN/6.23'}
        r = requests.get(sub_url, headers=headers, timeout=10)
        text = r.text.strip()
        # 尝试 base64 解码
        try:
            missing_padding = len(text) % 4
            if missing_padding:
                text += '=' * (4 - missing_padding)
            decoded = base64.b64decode(text).decode('utf-8')
            return decoded
        except Exception:
            return text
    except Exception as e:
        return str(e)
