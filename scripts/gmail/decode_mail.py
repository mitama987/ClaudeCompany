import base64
import json
from pathlib import Path

src = Path(r"C:\Users\mitam\AppData\Local\Temp\seo_port.json")
text = src.read_text(encoding="utf-8")
start = text.find("{")
payload = json.loads(text[start:])
data = payload["payload"]["body"]["data"]
decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8")
print(decoded)
