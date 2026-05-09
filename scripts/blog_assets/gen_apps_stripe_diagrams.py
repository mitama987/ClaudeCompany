"""Gemini API で Apps API vs Stripe 記事の図解画像を生成するスクリプト"""
import os, pathlib, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(pathlib.Path(__file__).resolve().parents[2] / ".env")
API_KEY = os.environ["GEMINI_API_KEY"]
OUTPUT_DIR = pathlib.Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\16_決済サービス\Apps\_attachments"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

DIAGRAMS = [
    {
        "filename": "apps_stripe_01_platform_vs_own.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1400x720px程度。

テーマ：「プラットフォーム販売 vs 独自決済 ― お金と顧客リストの流れ」

構成：左右2カラムの対比型インフォグラフィック

左カラム（赤・グレー系、Before）：
- 見出し：「プラットフォーム販売（note / Brain / Udemy など）」
- 顧客アイコン →（購入）→ プラットフォームアイコン（大きな四角） →（販売者アイコンに一部だけ到達）
- 矢印に「売上 70〜90%」「手数料 10〜30%」と明示
- プラットフォーム側の箱の中に「顧客リストはここに残る」赤枠
- 下部バッジ（赤）：「顧客資産がプラットフォーム依存」

右カラム（緑・金色系、After）：
- 見出し：「独自決済（自分のLPで販売）」
- 顧客アイコン →（購入）→ 自分のLP/販売者アイコンへほぼ100%到達
- 矢印に「売上の大部分」「手数料は少額」と明示
- 自分側の箱の中に「顧客リスト・メールアドレスが手元に残る」緑枠
- 下部バッジ（緑）：「顧客資産が自分の手元に」

中央に縦の「VS」マーク、2カラムを区切る。

スタイル：フラットデザイン、角丸、人物・箱・矢印アイコン、左右の配色コントラスト（赤系 vs 緑系）。テキストは全て日本語、視認性高く。"""
    },
    {
        "filename": "apps_stripe_02_api_hub.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1400x900px程度。

テーマ：「Apps API で広がる自動化 ― Webhookで繋がる世界」

構成：中央にハブ、周囲にスポーク（ハブ&スポーク型）

- 中央の大きな円（濃紺）：「Apps」「（決済発生）」のロゴ風
- 中央円から外へ向かう Webhook 矢印（ラベル：「Webhook イベント」）

- 周囲に5つの連携先ノードを配置（各ノードはアイコン＋ラベル＋一言説明）：
  1. 右上（緑）：「Google スプレッドシート」
     → 「顧客情報・売上を自動記録」
  2. 右下（紫）：「Discord」
     → 「購入者に自動でロール付与／解約時に剥奪」
  3. 左下（オレンジ）：「メール配信（リマインド）」
     → 「かご落ち・フォローアップを自動送信」
  4. 左上（水色）：「自分のLP」
     → 「CTAから決済ページへシームレス遷移」
  5. 真上（金色・"今後"ラベル）：「自社アプリ／サイト」
     → 「決済APIで自前UIに組み込み（予定）」

- 下部バッジ（金色）：「イベント7種・エンドポイント4＋α／ノーコードでも繋がる」

スタイル：ハブ&スポーク構造、中央は大きく・外周は均等配置、矢印は双方向感。フラットデザイン、各ノードはカラフルで区別しやすく。テキストは全て日本語。"""
    },
    {
        "filename": "apps_stripe_03_positioning_map.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1400x900px程度。

テーマ：「Apps vs Stripe ポジショニングマップ ― どちらがあなたに向くか」

構成：2軸の散布図（ポジショニングマップ）

- 縦軸（上下）：
  上：「グローバル / 英語ドキュメント前提」
  下：「日本市場特化 / 日本語サポート」
- 横軸（左右）：
  左：「ノーコード / 管理画面中心」
  右：「実装重視 / API高機能」

- 2つの大きな円を配置：
  1. 「Apps」の円（金色）：左下寄り（日本市場×ノーコード寄り）
     キャッチ：「日本語コンテンツ販売に最適」
     サブ：「講座／オンラインサロン／Brain的コンテンツ」
  2. 「Stripe」の円（青）：右上寄り（グローバル×API高機能）
     キャッチ：「SaaS・グローバル展開の定番」
     サブ":「海外対応／マーケットプレイス／複雑要件」

- 各円の周囲に小さなタグ：
  Apps: 「Discord連携標準」「Webhookイベント7種」「日本語サポート」「ノーコード決済ページ」
  Stripe: 「多言語対応」「Webhook豊富」「審査厳しめ」「API広範」

- 下部帯：「"どちらが優秀か" ではなく "どちらが向くか" の問題」

スタイル：散布図ポジショニングマップ、軸ラベル明確、2円の配置で位置を一目把握、フラットデザイン。テキストは全て日本語。"""
    },
    {
        "filename": "apps_stripe_04_start_3steps.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1400x500px程度。

テーマ：「Apps + Apps API の始め方 ― 3ステップで自動化スタート」

構成：横方向の3ステップフロー図

ステップ1（青系）：
- 大きな丸番号「1」
- アイコン：商品登録（箱＋タグ）
- タイトル：「Apps にアカウント作成 & 商品登録」
- サブテキスト：「デジタルコンテンツ／サブスク／買い切りを登録」

↓矢印→

ステップ2（紫系）：
- 大きな丸番号「2」
- アイコン：鍵＋APIシンボル
- タイトル：「APIキーを発行」
- サブテキスト：「管理画面でアプリID／アプリシークレットを取得」

↓矢印→

ステップ3（緑系）：
- 大きな丸番号「3」
- アイコン：Webhook（ベル＋矢印）
- タイトル：「Webhook URLを設定」
- サブテキスト：「スプシ連携はGAS、Discord連携はBot or n8nでOK」

下部に金色リボン：「ここまで設定すれば、決済 → 自動でスプシ記録 / Discord招待 / メール送信 が動き出す」

スタイル：横フロー図、3ステップが等間隔、各ステップは丸い番号＋色分けされたカード。矢印でシンプルに接続。フラットデザイン。テキストは全て日本語。"""
    },
    {
        "filename": "apps_stripe_05_comparison_table.png",
        "prompt": """シンプルで分かりやすい日本語の図解を生成してください。白背景、1400x1100px程度。

テーマ：「Apps vs Stripe ― 9観点のかんたん比較」

構成：2カラム対比型の比較インフォグラフィック（表ではなく、カード＋アイコンで視覚的に）

上部ヘッダー：左「Apps（金色系）」、右「Stripe（青系）」の大きなブランドヘッダーを左右に配置。

9行の比較行を上から下に並べる。各行は：
- 左端に観点ラベル（グレーのピル）
- 中央に観点名
- 左右に各サービスの特徴を短いフレーズ＋アイコンで表現
- 「Apps側が向く項目は金色ハイライト／Stripe側が向く項目は青ハイライト」

比較行：
1. 主戦場 / Apps: 日本のコンテンツ販売 / Stripe: グローバル汎用決済
2. 日本語サポート / Apps: ◎ 国内企業 / Stripe: △ 基本は英語
3. 決済ページ作成 / Apps: 管理画面でノーコード / Stripe: 基本は実装が必要
4. サブスク・分割 / Apps: 標準搭載 / Stripe: 標準搭載（両方とも○）
5. Webhookイベント / Apps: 7種（コンテンツ販売最適化） / Stripe: 非常に多い・汎用
6. API / Apps: シンプル（4エンドポイント+α） / Stripe: 広範・高機能
7. 初期セットアップ / Apps: 軽い / Stripe: 事業者審査が厳しめ
8. コミュニティ連携 / Apps: Discord連携が標準 / Stripe: 自前実装
9. 向いているサービス / Apps: 講座／サロン／Brain的コンテンツ / Stripe: SaaS／海外展開／マーケットプレイス

下部バッジ：「"優劣"ではなく"向き不向き"で住み分け」

スタイル：フラットデザイン、角丸カード、左右対比が一目でわかる。表ではなくカード列挙型。テキスト全て日本語、視認性高く。金色と青色のブランドカラー対比を強調。"""
    },
    {
        "filename": "apps_stripe_00_thumbnail.png",
        "prompt": """note.com 記事のサムネイル画像を生成してください。横長・1280x670px程度、16:9に近い比率。

記事タイトル：「独自決済で売るならどっち？ Apps API 正式リリースを機にStripeと比べてみた」

デザイン要件：
- 左右2分割構図：左は「Apps」（金色・ゴールド系ブランドカラー）、右は「Stripe」（青・ネイビー系ブランドカラー）、中央に大きな「VS」マークを配置
- 上部に記事タイトルを大きく日本語で配置（改行して2行でOK）：「独自決済で売るならどっち？」/「Apps API vs Stripe」
- 左側「Apps」エリアにはサブラベル「日本のコンテンツ販売に特化」と商品カード・サロンアイコン
- 右側「Stripe」エリアにはサブラベル「グローバル定番の決済API」と地球アイコン・コードブラケットアイコン
- 下部に小さく「Apps API 2026年4月 正式リリース」のバッジ
- 背景は白またはライトグレー、要素は立体感のあるフラットデザイン（drop shadow 控えめ）

スタイル：
- プロフェッショナルかつポップな雰囲気
- 文字の視認性を最優先（フォントは太め、適切なコントラスト）
- サムネイルとして note.com のタイムラインで目立つ配色
- 情報は詰め込みすぎず、一目で「Apps vs Stripe 比較記事」と分かる

テキストは全て日本語（タイトルは日本語＋英語混在OK）。読み手はコンテンツ販売・個人クリエイター層。"""
    },
]


def generate_and_save(diagram, index):
    """1枚の図解を生成して保存"""
    print(f"[{index}/{len(DIAGRAMS)}] {diagram['filename']} を生成中...")

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

        print(f"  NG: no image returned")
        return False

    except Exception as e:
        print(f"  NGエラー: {e}")
        return False


if __name__ == "__main__":
    indices = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else list(range(1, len(DIAGRAMS) + 1))

    success = 0
    for i in indices:
        if 1 <= i <= len(DIAGRAMS):
            if generate_and_save(DIAGRAMS[i - 1], i):
                success += 1

    print(f"\n完了: {success}/{len(indices)} 枚生成")
