"""フォロワー31人記事のアイキャッチ（サムネ）を OpenAI gpt-image-2 で生成。

note.com 推奨サイズ 1280x670 (1.91:1) に合わせるため、
1. gpt-image-2 で 1536x1024 を生成（gpt-image-2 が直接対応する最も横長の比率）
2. Pillow で中央水平帯を 1.91:1 にクロップ（1536x804）
3. LANCZOS で 1280x670 に縮小
4. 既存サムネ PNG を上書き保存
"""
import base64, io, json, os, pathlib
from openai import OpenAI
from PIL import Image


def _load_openai_config() -> tuple[str, str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_IMAGE_MODEL")
    if api_key and model:
        return api_key, model
    cfg_path = pathlib.Path(
        r"C:\Users\mitam\Desktop\work\50_ブログ\.obsidian\plugins\buzzblog-generator\data.json"
    )
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return (
        api_key or cfg["openaiApiKey"],
        model or cfg.get("openaiImageModel", "gpt-image-1"),
    )


API_KEY, IMAGE_MODEL = _load_openai_config()
OUTPUT_PATH = pathlib.Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\有料版\images\フォロワー31人で1日15000円_X自動投稿の勝ち筋\フォロワー31人で1日15000円_X自動投稿の勝ち筋_thumbnail.png"
)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

GEN_SIZE = "1536x1024"
TARGET_W, TARGET_H = 1280, 670
TARGET_RATIO = TARGET_W / TARGET_H

PROMPT = """note.com の記事アイキャッチとして使う日本語サムネイル画像を生成してください。

最終的なアスペクト比は 1.91:1（1280x670）。生成後に上下を中央クロップする前提なので、**重要なテキスト・ロゴ・主要オブジェクトはすべて画像の中央 65% の水平帯に収める**。画像の上下端には文字を置かない。

【テーマ】X(Twitter) アフィリエイトのサクセスストーリー型サムネ
- メインコピー（巨大・太字・ビビッドな黄色 #FFD400）：「31人で¥15,000/日」
- サブコピー（中サイズ・白）：「フォロワー数 ≠ 売上」
- 補助コピー（小サイズ・シアン #00E5FF）：「X自動投稿の勝ち筋」

【構成】
- 背景：純黒 (#0A0A0A) のグラデーション、わずかにネオン紫の光彩を散らす
- 左側：メインコピー＋サブコピーを大きくレイアウト
- 右下：黒地に白の大きな X(Twitter) ロゴ（リブランド後の四角型）。ネオンシアンとマゼンタのエッジ発光
- ロゴ周辺に小さな投稿カード（白背景の角丸長方形 + テキストライン + アバター丸）が3〜4枚浮遊し、ロゴへ向かう細いネオン矢印が「自動投稿」を示唆

【スタイル】
- フラットでモダンな日本語インフォグラフィック / プロダクトサムネ
- 日本語フォントは Noto Sans JP / Meiryo 系の太字、メインコピーには強いドロップシャドウ
- 高コントラスト・ネオン彩度（黄色・シアン・マゼンタ）。**「薄い色」「パステル」は使わない**
- 余分な文字、URL、ウォーターマーク、英語の小さな段落、説明キャプションは入れない
- 日本語テキストは正確に表示し、ローマ字化や文字化けを発生させない"""


def main():
    print(f"generating thumbnail (model={IMAGE_MODEL}, size={GEN_SIZE})")
    client = OpenAI(api_key=API_KEY)
    response = client.images.generate(
        model=IMAGE_MODEL,
        prompt=PROMPT,
        size=GEN_SIZE,
        n=1,
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError("no image returned")
    img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
    src_w, src_h = img.size
    print(f"  generated: {src_w}x{src_h}")

    new_h = int(round(src_w / TARGET_RATIO))
    if new_h > src_h:
        new_w = int(round(src_h * TARGET_RATIO))
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    print(f"  cropped to: {img.size[0]}x{img.size[1]} (ratio {img.size[0]/img.size[1]:.3f})")

    img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    img.save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"  saved: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
