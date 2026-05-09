import base64
import json
from pathlib import Path


def decode_and_save(json_path: Path, out_path: Path) -> None:
    text = json_path.read_text(encoding="utf-8")
    start = text.find("{")
    payload = json.loads(text[start:])
    data = payload["data"]
    decoded = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
    out_path.write_bytes(decoded)
    print(f"saved: {out_path} ({len(decoded)} bytes)")


if __name__ == "__main__":
    out_dir = Path(r"C:\Users\mitam\Desktop\work\30_XTP2_POST_r5\log\a00124_市岡大樹")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(r"C:\Users\mitam\AppData\Local\Temp")
    decode_and_save(tmp / "app_log.json", out_dir / "app.log")
    decode_and_save(tmp / "xpost_log.json", out_dir / "x_post_debug.log")
