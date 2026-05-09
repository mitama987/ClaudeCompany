"""ccnest紹介note記事の「分かりづらい部分」を補足する情報図解を3枚生成する。

抽象的なヒーロー画像（gen_ccnest_images.py）とは別軸で、
具体的なフロー・構造を見せるための情報図解。日本語ラベル入り。

出力先：C:/Users/mitam/Desktop/work/50_ブログ/images/ccnest_Claude_Code向けターミナル多重化ツール_generated/

生成枚数:
  1. diagram_install_flow.png — npm install -g ccnest-cli の内部フロー
  2. diagram_pane_split.png   — Ctrl+D=右分割 / Ctrl+E=下分割 の方向図
  3. diagram_sidebar.png       — サイドバー4セクション (Files/Claude/Git/Panes) 構造
  4. diagram_comparison.png    — ccnest vs tmux の比較ビジュアル

CLI:
  python gen_ccnest_diagrams.py              # 全部生成
  python gen_ccnest_diagrams.py KEY [KEY..]  # 指定キーだけ生成
"""

from __future__ import annotations

import base64
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API_KEY = "AIzaSyAAmWfDSIg_kTUAVJWteuphVDrPAL8AK6k"
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
)
OUT_DIR = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\images\ccnest_Claude_Code向けターミナル多重化ツール_generated"
)
BASENAME = "ccnest_Claude_Code向けターミナル多重化ツール_generated"


COMMON_STYLE = """
【スタイル】クリーンで読みやすいインフォグラフィック。フラットデザイン、太い線、はっきりした塗り分け。
【配色】背景=ダークネイビー(#0b1220)、メイン=白文字、アクセント=ゴールド(#e3b341)、サブ=エレクトリックブルー(#5cc8ff)、警告系=オレンジ。
【フォント】日本語は太めのゴシック体、英字はモノスペース。文字は中サイズ以上で見出しは特に大きく。
【アスペクト比】16:9 (1920x1080)
【品質】高解像度・高コントラスト・余白を十分に取る・装飾過多にしない
【日本語】記事用の図解なので、日本語テキストは正確に描画してください。誤字・余計な文字・ローマ字混入は避けてください。
"""


PROMPTS = {
    "diagram_install_flow": f"""ccnest の npm インストールフローを示すインフォグラフィック画像を作成してください。
{COMMON_STYLE}

【中心テーマ】「npm install -g ccnest-cli」を叩いた後、内部で何が起きるかを左→右の流れ図で見せる。

【構図】16:9。横方向に5つのステップを矢印「→」で繋ぐ大きなフロー図。各ステップは角丸の四角形カードで、上に小さなアイコン、下に日本語見出し、その下に1行の補足。

【ステップ（左から順番）】
1) ターミナルから実行 — 上に黒い丸ターミナルアイコン。タイトル「コマンド実行」。コード「npm install -g ccnest-cli」をモノスペースで表示。
2) postinstall 起動 — 上に歯車アイコン。タイトル「postinstall」。補足「Node.jsスクリプトが自動で走る」
3) OS / アーキ判定 — 上に Windows / Apple / Linux ロゴが3つ並ぶ小アイコン。タイトル「OS／アーキ判定」。補足「win-x64 / mac-arm64 / mac-x64 / linux-x64」
4) GitHub Releases から DL — 上にクラウドダウンロード矢印アイコンとGitHub猫アイコン。タイトル「GitHub Releases から DL」。補足「対応バイナリを取得」
5) PATH に配置 → 完了 — 上に緑のチェックアイコン。タイトル「PATH に配置」。補足「`ccnest` コマンドが使える」

【ヘッダー】画像上部中央に大きな見出し「npm install -g ccnest-cli の内部フロー」（白の極太ゴシック）。右上に小さく ccnest のロゴ風テキスト。

【背景】薄いグリッドが微かに見えるダークネイビー。各カードの背後にゴールドの細い光のラインが流れているような演出。

日本語は正確に描画してください。""",
    "diagram_pane_split": f"""ccnest のペイン分割キーバインドを示す図解画像を作成してください。
{COMMON_STYLE}

【中心テーマ】Ctrl+D が右分割（縦の境界線 ┃）、Ctrl+E が下分割（横の境界線 ━）であることを、3コマで直感的に理解させる。

【構図】16:9。横方向に3つの大きなターミナル枠を並べ、左→中→右へ「→」で繋ぐ。

【3コマ】
1) 左：起動直後の単一ペイン。タイトル「起動直後」。中の枠に「Pane 1」とだけ表示。
2) 中：Ctrl+D を押した後 = 右に縦分割された2ペイン。中央に縦線。タイトル「Ctrl+D で右分割」。左ペインに「Pane 1」、右ペインに「Pane 2」。中央上部にキーバインド「Ctrl + D」をキーキャップ風に大きく描画（金色のキー）。
3) 右：さらに Ctrl+E を押した後 = 右ペインがさらに上下分割された3ペイン。タイトル「Ctrl+E で下分割」。Pane 1（左ロング縦）、Pane 2（右上）、Pane 3（右下）。中央上部にキーバインド「Ctrl + E」をキーキャップ風（金色）。

【補足ラベル】
- 縦分割の境界線の横に小さく「縦の仕切り ┃」と日本語注釈
- 横分割の境界線の上に小さく「横の仕切り ━」と日本語注釈

【ヘッダー】画像上部中央に大きな見出し「プレフィックス不要のペイン分割」（白の極太ゴシック）。サブタイトル「Ctrl + D は右、Ctrl + E は下」（ゴールド）。

【背景】ダークネイビー。各ターミナル枠は黒に近い濃紺の角丸長方形で、白の細い枠線。

日本語は正確に描画してください。""",
    "diagram_comparison": f"""ccnest と tmux の比較表をビジュアル化したインフォグラフィック画像を作成してください。
{COMMON_STYLE}

【中心テーマ】「ccnest vs tmux」を縦に並べた比較表。8項目の対比を、◯／✕ や色分けで一目で分かるようにする。

【構図】16:9。画像上部中央に大きな見出し「ccnest vs tmux 早見比較」（白の極太ゴシック）。
中央〜下部に3列の比較表を配置。

【表の構造】
- ヘッダー行（最上段）：左から「項目」「ccnest」「tmux」
  - ccnest 列のヘッダーはゴールド背景に黒文字、tmux 列のヘッダーは濃紺背景に白文字。
- 8つのデータ行を縦に並べる。各行は薄い区切り線。
- ccnest 列の有利な値はゴールドハイライト＋小さな◯マーク、tmux 列の不利な値は灰色トーン＋✕マーク（数や対応OSなど中立な項目はマーク無しでOK）。

【データ行（上から順番）】
1) 項目「Claude Code統合」 / ccnest「ネイティブ（自動起動・残量表示）」◯ / tmux「なし」✕
2) 項目「プレフィックスキー」 / ccnest「不要」◯ / tmux「必須（既定 Ctrl+b）」✕
3) 項目「設定ファイル」 / ccnest「不要」◯ / tmux「.tmux.conf 必須」✕
4) 項目「ファイルツリー」 / ccnest「標準搭載」◯ / tmux「プラグイン必須」✕
5) 項目「Gitステータス表示」 / ccnest「標準搭載」◯ / tmux「自前で組む」✕
6) 項目「主要対応OS」 / ccnest「Win/macOS/Linux」 / tmux「多数」（両方マーク無し、中立）
7) 項目「配布方法」 / ccnest「npm（ビルド済み）／cargo」 / tmux「ディストリのパッケージ」（両方マーク無し）
8) 項目「学習曲線」 / ccnest「低」◯ / tmux「高」✕

【全体配色】
- 背景：ダークネイビー (#0b1220)
- 「項目」列：濃紺塗り＋白文字
- ccnest 列：ゴールド（#e3b341）アクセント。◯マークはゴールド円。
- tmux 列：薄い灰色トーン。✕マークは赤みオレンジ。
- 表全体は角丸の枠で囲み、上下に余白を確保。

【補足】右下隅に小さく「Claude Code に最適化した縦特化ツール」という日本語キャッチコピー（ゴールド）。

日本語は正確に描画してください。誤字や余計なローマ字混入は避けてください。""",
    "diagram_sidebar": f"""ccnest のサイドバー4セクション構造を示す図解画像を作成してください。
{COMMON_STYLE}

【中心テーマ】ccnest のサイドバーには Files / Claude / Git / Panes の4セクションがあり、それぞれが何を担当するかを一目で分からせる。

【構図】16:9。左 1/3 にサイドバーのモックアップを縦長に大きく描画、右 2/3 に各セクションの役割カード4枚を縦に並べる。

【左側サイドバーモックアップ】
- 縦長の濃紺パネル
- 上から順に 4ブロック：
  - 「📁 Files」見出し下にツリー風のリスト（src/、README.md など）
  - 「🤖 Claude」見出し下に「#1  68%」「#2  22%」のような残量表示
  - 「🌿 Git」見出し下に「main  +3 -1」
  - 「🪟 Panes」見出し下に「#1  #2  #3」
- 各ブロックの見出しはゴールド、本文は白。
- アクティブ行が反転白ブロックで強調されているとなお良い。

【右側カード4枚（縦に積む）】
1) Files — タイトル「Files」（ゴールド大）／本文「プロジェクトのファイルツリー。遅延ロード式・Emojiアイコン対応」
2) Claude — タイトル「Claude」／本文「各ペインのトークン残量をJSONLログから集計して表示」
3) Git — タイトル「Git」／本文「現在のブランチと変更ファイル数を常時表示」
4) Panes — タイトル「Panes」／本文「起動中のペイン一覧と状態」

各カードはダークネイビーの角丸長方形＋細いゴールドの左ボーダー。

【ヘッダー】画像上部中央に大きな見出し「ccnest のサイドバー4セクション」（白の極太ゴシック）。

【背景】ダークネイビー (#0b1220) のフラット背景に、薄いグリッド。

日本語は正確に描画してください。""",
}


def generate_one(prompt: str, output_path: Path, label: str) -> tuple[str, bool, str]:
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9"},
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            body = json.loads(resp.read())
        for part in body["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                img = base64.b64decode(part["inlineData"]["data"])
                output_path.write_bytes(img)
                return (label, True, str(output_path))
        return (label, False, "no inlineData in response")
    except Exception as exc:
        return (label, False, f"{type(exc).__name__}: {exc}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    selected = sys.argv[1:] if len(sys.argv) > 1 else list(PROMPTS.keys())
    unknown = [k for k in selected if k not in PROMPTS]
    if unknown:
        print(f"Unknown keys: {unknown}")
        print(f"Available: {list(PROMPTS.keys())}")
        return 2

    jobs: list[tuple[str, str, Path]] = []
    for key in selected:
        jobs.append(
            (
                key,
                PROMPTS[key],
                OUT_DIR / f"{BASENAME}_{key}.png",
            )
        )

    print(f"Total jobs: {len(jobs)}")
    print(f"Output: {OUT_DIR}")
    print(f"Model: {MODEL}\n")

    results: list[tuple[str, bool, str]] = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        future_to_label = {
            ex.submit(generate_one, prompt, path, label): label
            for label, prompt, path in jobs
        }
        for fut in as_completed(future_to_label):
            label, ok, info = fut.result()
            status = "OK" if ok else "FAIL"
            print(f"[{status}] {label} -> {info}")
            results.append((label, ok, info))

    failed = [r for r in results if not r[1]]
    print(f"\nDone. Success: {len(results) - len(failed)} / {len(results)}")
    if failed:
        print("Failed jobs:")
        for label, _, info in failed:
            print(f"  - {label}: {info}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
