"""フォロワー31人記事用の図解画像をGeminiで生成するスクリプト"""
import json, os, pathlib, sys
from google import genai
from google.genai import types


def _load_gemini_api_key() -> str:
    if key := os.environ.get("GEMINI_API_KEY"):
        return key
    cfg_path = pathlib.Path(
        r"C:\Users\mitam\Desktop\work\50_ブログ\.obsidian\plugins\buzzblog-generator\data.json"
    )
    return json.loads(cfg_path.read_text(encoding="utf-8"))["apiKey"]


API_KEY = _load_gemini_api_key()
OUTPUT_DIR = pathlib.Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\有料版\images\フォロワー31人で1日15000円_X自動投稿の勝ち筋"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

DIAGRAMS = [
    {
        "filename": "フォロワー31人で1日15000円_X自動投稿の勝ち筋_diagram_pricing.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1200x680px程度。

テーマ：「XToolsPro3 料金プラン（全プラン買い切り・サブスクなし）」

構成：3つのプランカードを横に並べる
- カード1（グレー系）：「無料版」¥0 ／ 1アカウントだけ試せる
- カード2（青系）：「買い切り＋アドオン1つ」¥2,980〜 ／ 複数アカウント対応 ／ AIクレジット1,000pt
- カード3（金色系・おすすめバッジ付き）：「フル買切り」¥19,800 ／ 全5アドオン同梱（単品計¥23,000相当から¥3,200割引）

下部に強調帯：「サブスクなし・全プラン買い切り・月額費用ゼロ」

スタイル：SaaS風 Pricing Cards。おすすめカードを少し大きめ・影を強く。フラットデザインで清潔感のあるインフォグラフィック。テキストは全て日本語。""",
    },
    {
        "filename": "フォロワー31人で1日15000円_X自動投稿の勝ち筋_diagram_core_features.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1200x720px程度。

テーマ：「XToolsPro3 コア機能（ぜんぶ盛り）」

構成：6つの機能カードを2行×3列のグリッドで配置（各カードにアイコン + 機能名 + 1行説明）
1. ランダム投稿エンジン（プールから重複なし配信）
2. アカウント別プロキシ（連鎖凍結ブロック）
3. コミュニティ自動投稿（濃い層に直撃）
4. 自動DM返信（テンプレ＋リクエスト承認）
5. Amazon在庫復活アラート（Keepa連携・即ツイート）
6. AI投稿生成（GPT-4o / Gemini で文面量産）

下部にバッジ：「API不要・IDとパスだけで動く」

スタイル：6カードのフィーチャーグリッド。各カードを色分け（紫/水色/緑/ピンク/オレンジ/青）。アイコン付き、フラットデザイン。テキストは全て日本語。""",
    },
]


def generate_and_save(diagram, idx):
    print(f"[{idx}/{len(DIAGRAMS)}] generating {diagram['filename']}")
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=diagram["prompt"],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                output_path = OUTPUT_DIR / diagram["filename"]
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"  OK: {output_path}")
                return True

        print("  NG: no image returned")
        return False

    except Exception as e:
        print(f"  NGエラー: {e}")
        return False


if __name__ == "__main__":
    indices = (
        [int(x) for x in sys.argv[1:]]
        if len(sys.argv) > 1
        else list(range(1, len(DIAGRAMS) + 1))
    )

    success = 0
    for i in indices:
        if 1 <= i <= len(DIAGRAMS):
            if generate_and_save(DIAGRAMS[i - 1], i):
                success += 1

    print(f"\n完了: {success}/{len(indices)} 枚生成")
