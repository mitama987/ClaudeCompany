"""フォロワー31人記事用の図解画像をOpenAI gpt-image-2で生成するスクリプト"""
import base64, json, os, pathlib, sys
from openai import OpenAI


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
OUTPUT_DIR = pathlib.Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\有料版\images\フォロワー31人で1日15000円_X自動投稿の勝ち筋"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key=API_KEY)

DIAGRAMS = [
    {
        "filename": "フォロワー31人で1日15000円_X自動投稿の勝ち筋_diagram_pricing.png",
        "size": "1536x1024",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景。

テーマ：「XToolsPro3 料金プラン（全プラン買い切り・サブスクなし）」

構成：3つのプランカードを完全に同じサイズ・同じ高さで横一列に並列配置（3カラム均等）
- カード1（グレー系）：「無料版」¥0 ／ 1アカウントだけ試せる
- カード2（青系）：「買い切り＋アドオン1つ」¥2,980〜 ／ 複数アカウント対応 ／ AIクレジット1,000pt
- カード3（金色系）：「フル買切り」¥19,800 ／ 全5アドオン同梱（単品計¥23,000相当から¥3,200割引）

下部に帯：「サブスクなし・全プラン買い切り・月額費用ゼロ」

スタイル：SaaS風 Pricing Cards。各カードの色（グレー／青／金）はしっかりと発色させ、視認性の高いはっきりした色で塗る（薄いパステルや色を抜いた印象にはしない）。**3つのカードは完全に対等・並列で表示し、特定のカードを「おすすめ」「人気」「ベスト」などのバッジで強調しない。サイズ・影・枠線の太さも3カードで統一する**（金色カードを大きくしたり影を強めたりしない）。色の鮮やかさはそのまま、レイアウトのみ完全均等にする。フラットデザインで清潔感のあるインフォグラフィック。テキストは全て日本語。""",
    },
    {
        "filename": "フォロワー31人で1日15000円_X自動投稿の勝ち筋_diagram_core_features.png",
        "size": "1536x1024",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景。

テーマ：「XToolsPro3 コア機能（ぜんぶ盛り）」

構成：6つの機能カードを2行×3列のグリッドで配置（各カードにアイコン + 機能名 + 1行説明）
1. ランダム投稿エンジン（プールから重複なし配信）
2. アカウント別プロキシ（連鎖凍結ブロック）
3. コミュニティ自動投稿(濃い層に直撃)
4. 自動DM返信（テンプレ＋リクエスト承認）
5. Amazon在庫復活アラート（Keepa連携・即ツイート）
6. AI投稿生成（GPT-4o / Gemini で文面量産）

下部にバッジ：「API不要・IDとパスだけで動く」

スタイル：6カードのフィーチャーグリッド。各カードを色分け（紫/水色/緑/ピンク/オレンジ/青）。アイコン付き、フラットデザイン。テキストは全て日本語。""",
    },
]


def generate_and_save(diagram, idx):
    print(f"[{idx}/{len(DIAGRAMS)}] generating {diagram['filename']} (model={IMAGE_MODEL})")
    try:
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=diagram["prompt"],
            size=diagram["size"],
            n=1,
        )

        b64 = response.data[0].b64_json
        if not b64:
            print("  NG: no b64 returned")
            return False

        image_data = base64.b64decode(b64)
        output_path = OUTPUT_DIR / diagram["filename"]
        with open(output_path, "wb") as f:
            f.write(image_data)
        print(f"  OK: {output_path}")
        return True

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
