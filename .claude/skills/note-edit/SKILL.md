# note.com 記事投稿スキル

ローカルの Markdown 記事ファイルを note.com に新規投稿するスキル。エディタへのフォーマット付き流し込み、引用ブロック化、箇条書き変換等をブラウザ自動操作で行う。

## 使用方法

```
/note-edit <記事MDファイルパス>
```

- **引数**: 投稿する記事の MD ファイルパス（`_generated.md` 等）
- スキルはファイルを読み込み、note.com の新規記事エディタにフォーマット付きで流し込む

例: `/note-edit 02_note/00_XToolsPro4/X APIまとめ_generated.md`

## 記事MDファイルの仕様

YAMLフロントマター付きの Markdown ファイル:

```markdown
---
title: "記事タイトル"
date: 2026-03-08
tags: [tag1, tag2]
source: "元ファイルパス"
---

# 記事タイトル

本文テキスト...

## 見出し2

- リスト項目1
- リスト項目2
```

### 対応するMarkdown要素

| Markdown | note.com変換 |
|---|---|
| `# Title` | タイトル欄に入力（本文には含めない） |
| `## Heading` | `<h2>` 見出し |
| `### Heading` | `<h3>` 小見出し |
| 通常テキスト | `<p>` 段落 |
| `- item` | `<ul><li>` 箇条書き |
| `> quote` | blockquote（ツールバー経由で後から変換） |
| `**bold**` | `<strong>` 太字 |
| `[text](url)` | `<a>` リンク |
| `` `code` `` | `<code>` インラインコード |
| `| table |` | テキスト変換（note.comはテーブル非対応） |
| `![[image]]` | スキップ（Obsidian形式、手動対応を報告） |

## 処理フロー

### Step 1: 記事ファイル読み込み
1. 指定されたMDファイルを `Read` ツールで読み込む
2. YAMLフロントマターからタイトル・タグを取得
3. 本文をブロック単位（見出し、段落、リスト、引用、テーブル、画像）にパース
4. `# タイトル` 行（H1）は本文から除外（タイトル欄で使用）

### Step 2: ブラウザ準備
1. `tabs_context_mcp` でタブ情報を取得
2. 新しいタブを作成し、`https://note.com/notes/new` に遷移（`editor.note.com/notes/new` に直接アクセスすると Access Denied になるため、`note.com/notes/new` 経由で開く）
3. エディタの読み込み完了を待つ（`.ProseMirror` の出現を確認）

### Step 3: タイトル入力
1. `take_snapshot` でタイトル入力欄を特定
2. YAMLフロントマターの `title` をタイトル欄に入力

### Step 3.5: アイキャッチ画像（サムネイル）のご案内
記事トップのサムネイル画像は、ブラウザのセキュリティ制限により **自動アップロード不可**。
ユーザーに手動アップロードを依頼する。

**必ずユーザーに以下を伝える:**
1. アップロードするファイルの **フルパス** を表示する
2. 手順: エディタ上部「画像を追加」→「画像をアップロード」→ ファイル選択

例:
```
サムネイル画像を手動でアップロードしてください:
パス: C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_紹介記事\icloud_thumbnail.jpg
手順: エディタ上部「画像を追加」→「画像をアップロード」→ 上記ファイルを選択
```

**理由**: file inputへのローカルファイル自動セットはブラウザセキュリティで不可。ダイアログが開くとMCPが操作不能になる。

### Step 4: 本文コンテンツ挿入
1. MDの各ブロックをHTML要素に変換し、ProseMirrorエディタに一括挿入（パターン8使用）
2. 本文の先頭に冒頭あいさつ文を挿入: 「こんにちは！SNS自動化ツール開発歴7年のYouパパです。」
3. 変換ルール:
   - `##` → `<h2>`, `###` → `<h3>`
   - 通常段落 → `<p>`（インライン書式も変換）
   - `- ` リスト → `<ul><li>`
   - `> ` 引用 → まず `<p>` として挿入（後でStep 5で変換）
   - テーブル → `<ul><li>` 箇条書きに変換（note.comはテーブル非対応。列挙データはリスト化する）
   - 番号付きリスト（`1. テキスト`） → `<p>` として `1. ` を含むテキストで挿入（note.comに `<ol>` はないため）
4. 画像（`![[...]]`）は位置をメモし、Step 5.5でパターン9により挿入。事前にBuzzBlogプラグイン等で画像を生成しておく

### Step 5: 引用ブロック変換
1. 元MDに `>` 引用がある場合、挿入後にパターン2（ツールバー方式）で blockquote に変換
2. **重要**: JS Selection API だけではProseMirrorの内部選択状態が更新されない。以下の手順で実際のマウス/キーボード操作で選択する:
   - JSで対象段落の座標を取得（`getBoundingClientRect()`）
   - `triple_click` でその座標をクリックし段落を選択（ProseMirrorが認識する選択方式）
   - `find` で「引用」ボタンを探し、`left_click` でクリック
3. 冒頭の悩みパート（「〜ませんか？」等の疑問文連続）がある場合、パターン10で引用+中黒箇条書きに変換

### Step 5.5: H2見出し画像挿入（画像ファイルがある場合）
1. H2見出しに対応する画像ファイル一覧を確認
2. パターン9の手順で各画像を挿入
3. 全画像挿入後、パターン9 Step 9-3で空行を一括削除
4. 挿入結果を確認

### Step 6: 確認・一時保存
1. `take_snapshot` で挿入結果を全体確認
2. 「一時保存」ボタンをクリックして保存
3. スキップした画像やテーブルの一覧をユーザーに報告

### Step 7: 公開（ユーザーから指示があった場合）
1. 「公開に進む」ボタンをクリック → 公開設定ページ（`/publish/`）に遷移
2. ハッシュタグを追加（パターン7参照。YAMLフロントマターの tags も活用）
3. 公開設定を確認（記事タイプ、マガジン、詳細設定など）
4. **「投稿する」ボタンのクリック前に必ずユーザーに確認を取る**

### Step 8: 完了報告
- 投稿した記事のタイトルとURL
- 適用したフォーマットのサマリー
- 手動対応が必要な項目（画像挿入、テーブル等）

## 既存記事の部分編集

新規投稿（Step 1〜8）とは異なり、**既に公開/下書きされている記事に対して部分的な書式変更を加える**場合の基本方針。引用ブロック化・UL変換・新規セクション挿入などを既存コンテンツに追加する際に使用する。

### 基本原則3つ

**①引用ボタンはトグル動作**
- note.comの「引用」ボタンは同じ要素に2回クリックすると**引用解除**になる
- バッチ処理で失敗と思って再試行すると、実は成功していた箇所を元に戻してしまう事故が頻発する
- **対策**: 処理前に `target.closest('blockquote')` で既引用チェック、既引用ならスキップ

**②1操作 = 1 javascript_exec**
- 1つのJS実行内で `for` ループを使って複数要素を連続処理するとProseMirror状態が壊れる
- 中盤から浮動ツールバーが出現しなくなり失敗が連鎖する
- **対策**: 各要素の処理を個別の `javascript_exec` 呼び出しに分割する

**③処理前後の必須検証**
- 各操作の前後で「期待通りの状態か」をJSで確認
- 失敗時のリトライは **状態を再読み込み** してから（キャッシュされた要素参照は無効になっている可能性）

### 既編集チェックヘルパー（必須）

各処理フェーズの前後で現在の状態を一覧確認：

```javascript
(() => {
  const tests = [
    ['プレフィックス1', 'Q1A'],
    ['プレフィックス2', 'Q2'],
    // ... 以下対象箇所を列挙
  ];
  const res = [];
  for (const [prefix, label] of tests) {
    const match = Array.from(document.querySelectorAll('.ProseMirror p'))
      .find(x => x.textContent.startsWith(prefix));
    res.push(`${label}:${match?.closest('blockquote') ? '✓' : '✗'}`);
  }
  return res.join(' ');
})();
```

### 部分編集フロー

1. **事前スナップショット**: 編集前の対象セクションをJSで列挙・記録
2. **1操作ずつ処理**: パターン12〜15を1要素ずつ適用
3. **各操作後の検証**: `closest('blockquote')` 等で結果を確認
4. **最後にまとめて一時保存**: パターン6で保存（途中保存でもエディタ状態は維持される）

## note.com エディタ技術情報

### ProseMirror ベースのエディタ
- note.com のエディタは **ProseMirror** を使用している
- エディタのセレクタ: `.ProseMirror` または `div[contenteditable="true"]`
- DOM構造: `<div class="ProseMirror">` の中に `<p>`, `<h2>`, `<blockquote>`, `<ul>` 等が並ぶ
- 変更後は `dispatchEvent(new Event('input', { bubbles: true }))` で ProseMirror にDOM変更を通知する必要がある

### エディタのDOM構造例
```html
<div class="ProseMirror" contenteditable="true">
  <h2>見出し</h2>
  <p>通常の段落テキスト</p>
  <blockquote><p>引用テキスト</p></blockquote>
  <ul><li><p>リスト項目</p></li></ul>
</div>
```

## 操作パターン集

### パターン1: テキスト挿入（新規段落追加）

本文の先頭や特定位置に新しい段落を追加する。

```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    if (!editor) return 'エディタが見つかりません';

    const newP = document.createElement('p');
    newP.textContent = '追加するテキスト';

    // 先頭に追加する場合
    editor.insertBefore(newP, editor.firstChild);

    // 特定要素の後に追加する場合
    // const target = editor.querySelector('h2'); // 例: 最初のh2の後
    // target.parentNode.insertBefore(newP, target.nextSibling);

    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return '段落を追加しました';
})();
```

### パターン2: 引用ブロック化（ツールバー使用方式）【推奨】

テキストを選択してツールバーの「引用」ボタンをクリックする方式。
**これが唯一の正しい方法。DOM直接操作では引用ブロックが壊れる（パターン3の注意参照）。**

#### Step 2-1: JavaScript Selection APIで対象テキストを選択
```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    const ps = Array.from(editor.querySelectorAll(':scope > p'));
    const startP = ps.find(p => p.textContent.includes('対象テキスト開始部分'));
    const endP = ps.find(p => p.textContent.includes('対象テキスト終了部分'));
    if (!startP || !endP) return 'テキストが見つかりません';

    const range = document.createRange();
    range.setStart(startP, 0);
    range.setEnd(endP, endP.childNodes.length);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    return '選択完了';
})();
```

#### Step 2-2: ブロックレベルツールバーの「引用」ボタンをクリック
テキストを選択すると、ページ上部にブロックレベルのツールバーが表示される。
このツールバーには以下のボタンが含まれる：
- AIアシスタント、見出し、**太字**、取り消し線、文章の配置、リンク、**引用**、コード、削除、音声を編集

```
// take_snapshot でボタンのuidを特定
// 「引用」ボタン（button "引用"）を click でクリック
```

**注意:** インライン選択時の浮動ツールバー（太字・取り消し線・リンクの3つのみ）とは異なる。
ブロックレベルのツールバーは複数段落を選択した場合に表示される。

#### 結果のDOM構造
note.comの引用ブロックは以下の構造になる：
```html
<figure>
  <blockquote>
    <p>引用テキスト（複数行はテキストノードとして並ぶ）</p>
  </blockquote>
  <figcaption>出典（任意）</figcaption>
</figure>
```

### パターン3: 引用ブロック化（DOM直接操作方式）

**⚠️ 警告: この方式は正しく動作しない。必ずパターン2（ツールバー方式）を使うこと。**

DOM直接操作で `<blockquote>` を作成しても、ProseMirrorがスキーマに基づいてDOMを再構築する。
note.comのスキーマではblockquoteは `<figure>` 内に配置され、段落は1つしか保持されない。
結果として、複数の `<p>` を含む `<blockquote>` を作ると最初の段落以外が `<figcaption>` に流出する。

### パターン4: 箇条書きリスト変換

`・` や `- ` で始まる段落をHTML `<ul><li>` リストに変換する。

```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    if (!editor) return 'エディタが見つかりません';

    const startText = '対象テキスト開始部分';
    const endText = '対象テキスト終了部分';

    const paragraphs = Array.from(editor.querySelectorAll('p'));
    let startIdx = -1, endIdx = -1;
    paragraphs.forEach((p, i) => {
        if (p.textContent.includes(startText)) startIdx = i;
        if (p.textContent.includes(endText)) endIdx = i;
    });

    if (startIdx === -1 || endIdx === -1) return 'テキストが見つかりません';

    // <ul> 要素を作成
    const ul = document.createElement('ul');
    for (let i = startIdx; i <= endIdx; i++) {
        const li = document.createElement('li');
        const p = document.createElement('p');
        // 先頭の「・」や「- 」を除去してテキスト設定
        p.textContent = paragraphs[i].textContent.replace(/^[・\-]\s*/, '');
        li.appendChild(p);
        ul.appendChild(li);
    }

    // 元の段落を置き換え
    paragraphs[startIdx].parentNode.insertBefore(ul, paragraphs[startIdx]);
    for (let i = startIdx; i <= endIdx; i++) {
        paragraphs[i].remove();
    }

    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return '箇条書きリスト変換完了';
})();
```

### パターン5: テキスト修正（innerHTML操作）

既存テキストの一部を修正する。引用ブロック内のテキスト修正にも対応。

```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    if (!editor) return 'エディタが見つかりません';

    // 特定の段落テキストを修正
    const paragraphs = editor.querySelectorAll('p');
    for (const p of paragraphs) {
        if (p.textContent.includes('修正対象テキスト')) {
            p.innerHTML = p.innerHTML.replace('修正対象テキスト', '修正後テキスト');
            break;
        }
    }

    // blockquote 内のテキスト修正
    const blockquotes = editor.querySelectorAll('blockquote p');
    for (const p of blockquotes) {
        if (p.textContent.includes('修正対象テキスト')) {
            p.innerHTML = p.innerHTML.replace('修正対象テキスト', '修正後テキスト');
            break;
        }
    }

    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return 'テキスト修正完了';
})();
```

### パターン6: 一時保存

```javascript
// find ツールで「一時保存」ボタンを見つけてクリック
// または take_snapshot でボタンのuidを特定
```

### パターン7: ハッシュタグ追加（公開設定ページ）

公開設定ページ（`/publish/`）でハッシュタグを追加する。

#### 公開設定ページの構成
「公開に進む」ボタンクリック後に遷移するページ。左側メニュー:
- ハッシュタグ
- 記事タイプ（無料/有料）
- 記事の追加（マガジン等）
- 詳細設定

#### ハッシュタグ追加手順

**1. 推奨タグのクリック**
ページに記事内容に基づく推奨タグがボタンとして表示される。適切なものをクリックして追加。

**2. カスタムタグの入力**
推奨タグにないハッシュタグは、入力欄（combobox「ハッシュタグを追加する」）に入力してEnterで確定。

```
// 1. 推奨タグをクリック（take_snapshotでuid確認）
// 例: click uid=15_11  // #Stripe

// 2. カスタムタグを入力
// fill uid=15_9 value="Firebase"
// press_key Enter

// 3. 繰り返し
// fill uid=15_9 value="GAS"
// press_key Enter
```

#### ハッシュタグ選定の指針
記事内容から以下のカテゴリでタグを選定する（合計8〜10個が目安）:
- **技術固有名詞**: 記事で扱う技術・サービス名（例: Stripe, Firebase, GAS）
- **技術カテゴリ**: 大分類のタグ（例: プログラミング, 決済システム）
- **ターゲット層**: 想定読者向けタグ（例: エンジニア）
- **関連技術**: 記事で言及する周辺技術（例: CloudFunctions, GoogleCloud, スプレッドシート）

### パターン8: 記事一括挿入（新規投稿用）

MDファイルの本文をパースしてProseMirrorエディタに一括挿入する。

**注意**: blockquote は DOM直接操作では壊れるため、この関数では `<p>` として挿入し、後からパターン2（ツールバー方式）で変換する。

```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    if (!editor) return 'エディタが見つかりません';

    // 既存の空段落をクリア
    while (editor.firstChild) editor.firstChild.remove();

    // blocks は動的に生成したJSON配列に置き換える
    // 例: [{ type: 'h2', content: '見出し' }, { type: 'p', html: '<strong>太字</strong>テキスト' }, ...]
    const blocks = __BLOCKS__;

    blocks.forEach(block => {
        let el;
        switch (block.type) {
            case 'h2':
                el = document.createElement('h2');
                el.textContent = block.content;
                break;
            case 'h3':
                el = document.createElement('h3');
                el.textContent = block.content;
                break;
            case 'p':
                el = document.createElement('p');
                if (block.html) {
                    el.innerHTML = block.html;
                } else {
                    el.textContent = block.content || '';
                }
                break;
            case 'ul':
                el = document.createElement('ul');
                block.items.forEach(item => {
                    const li = document.createElement('li');
                    const p = document.createElement('p');
                    p.innerHTML = item;
                    li.appendChild(p);
                    el.appendChild(li);
                });
                break;
            case 'empty':
                el = document.createElement('p');
                el.innerHTML = '<br>';
                break;
        }
        if (el) editor.appendChild(el);
    });

    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return blocks.length + 'ブロックを挿入しました';
})();
```

使用時は `__BLOCKS__` をパース結果のJSON配列に置き換える。

#### Markdown → blocks 変換ルール

各行を以下のルールでブロックに変換する:

1. `## テキスト` → `{ type: 'h2', content: 'テキスト' }`
2. `### テキスト` → `{ type: 'h3', content: 'テキスト' }`
3. `- テキスト` が連続 → `{ type: 'ul', items: ['テキスト1', 'テキスト2', ...] }`
4. `> テキスト` → まず `{ type: 'p', content: 'テキスト' }` として挿入し、後でツールバーで引用化
5. `![[画像]]` → スキップ（ユーザーに報告）
6. `| テーブル |` → ヘッダー行と区切り行を除き、データ行を `{ type: 'p', content: '項目: 値' }` 形式に変換
7. 空行 → `{ type: 'empty' }`
8. その他 → `{ type: 'p', html: inlineFormat(テキスト) }`

#### インライン書式変換（inlineFormat）

Markdown のインライン書式をHTMLに変換する:

- `**text**` → `<strong>text</strong>`
- `[text](url)` → `<a href="url">text</a>`
- `` `code` `` → `<code>code</code>`

### パターン9: H2見出し画像挿入

H2見出し直下に画像を挿入する。画像はクリップボード経由でペーストする方式。

#### 画像挿入手順（1枚ずつ繰り返し）

**Step 9-1: 画像をクリップボードにコピー（PowerShell）**
```powershell
powershell.exe -Command 'Add-Type -AssemblyName System.Windows.Forms; $img = [System.Drawing.Image]::FromFile("画像パス"); [System.Windows.Forms.Clipboard]::SetImage($img); Write-Host "copied"'
```

**Step 9-2: カーソルを配置してペースト**
JSでH2直後の空P要素にカーソルを配置し、すぐにCtrl+Vでペースト。
**重要**: スクリーンショット撮影はクリップボードを上書きするため、コピー後ペーストまでの間にscreenshot等を挟まないこと。

**Step 9-3: 空行削除（全画像挿入後に一括実行）**
H2とFIGURE(画像)の間に残る空P要素を削除する:
```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    const children = Array.from(editor.children);
    let removed = 0;
    for (let i = children.length - 1; i >= 0; i--) {
        const tag = children[i].tagName;
        if (tag === 'H2' || tag === 'H3') {
            const next1 = children[i + 1];
            if (next1 && next1.tagName === 'P' && (!next1.textContent || !next1.textContent.trim())) {
                next1.remove();
                removed++;
            }
        }
    }
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return removed + '個の空行を削除しました';
})();
```

#### 注意事項
- スクリーンショットはクリップボードを上書きする → コピー→ペーストは連続で実行
- 逆順で削除してインデックスずれを防止
- 削除後は必ずdispatchEventで変更通知

### パターン10: 冒頭悩みパートの引用+中黒箇条書き化

記事冒頭の「〜ありませんか？」「〜ですよね？」等の読者の悩みを列挙するパートを、
引用ブロック内で中黒（・）付き箇条書きに変換する。

#### 対象の判定
- 記事冒頭（H2の前）にある連続する疑問文・悩み文
- 典型パターン: 「〜ませんか？」「〜ですよね？」「〜でしょうか？」で終わる連続段落
- 末尾に「こんな悩みを抱えていませんか？」等のまとめ文がある場合、引用ブロックには含めず、引用の直後に通常段落（`<p>`）として配置する

#### 変換手順

**Step 10-1: 対象段落を特定**
JSで冒頭の疑問文段落群を特定し、テキスト内容を取得。

**Step 10-2: 中黒付きテキストに変換して引用ブロック化**
1. 各悩み文の先頭に「・」を付与
2. パターン2（ツールバー方式）で引用ブロックに変換
   - Selection APIで対象段落を選択
   - ツールバーの「引用」ボタンをクリック
3. まとめ文（「こんな悩みを抱えていませんか？」等）は引用ブロックに含めず、引用直後の `<p>` として残す

#### 変換前後の例

**変換前（MD）:**
```
「X APIを使ってBOTを作りたいけど、従量課金っていくらかかるの？」
「Freeプランなのにいざ投稿しようとしたら402エラーが出てしまう…」
こんな悩みを抱えていませんか？
```

**変換後（note.comエディタ）:**
```html
<figure>
  <blockquote>
    <p>・X APIを使ってBOTを作りたいけど、従量課金っていくらかかるの？
    ・Freeプランなのにいざ投稿しようとしたら402エラーが出てしまう…</p>
  </blockquote>
</figure>
<p>こんな悩みを抱えていませんか？</p>
```

### パターン11: 冒頭あいさつ文挿入

記事本文の一番先頭に自己紹介のあいさつ文を挿入する。

#### あいさつ文
「こんにちは！SNS自動化ツール開発歴7年のYouパパです。」

#### 挿入位置
- エディタの最初の要素の前（`editor.firstChild` の前）
- 悩みパート（パターン10）がある場合はその前に配置

#### JS
パターン1（テキスト挿入）を使用し、`editor.insertBefore(newP, editor.firstChild)` で先頭に挿入。

```javascript
(() => {
    const editor = document.querySelector('.ProseMirror');
    if (!editor) return 'エディタが見つかりません';
    const newP = document.createElement('p');
    newP.textContent = 'こんにちは！SNS自動化ツール開発歴7年のYouパパです。';
    editor.insertBefore(newP, editor.firstChild);
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return '挿入完了';
})();
```

### パターン12: 連続引用化の正しいイベント順序【既存記事編集】

パターン2の「JS Selection API + ツールバー方式」を既存記事の複数段落に連続適用する場合、**selectionchange イベント発火** と **アクティベーション前処理** が必須。これらが抜けると浮動ツールバーが出現せず失敗する。

#### 正しい手順（1段落ずつ実行）

```javascript
(async () => {
  const prefix = 'A: プレフィックス';
  const ps = document.querySelectorAll('.ProseMirror p');
  let target = null;
  for (const p of ps) {
    // トグル防止: 既に引用済みはスキップ
    if (p.textContent.startsWith(prefix) && !p.closest('blockquote')) { target = p; break; }
  }
  if (!target) return 'already done';

  // 1. スクロールして要素を表示領域に入れる
  target.scrollIntoView({block: 'center'});
  await new Promise(r => setTimeout(r, 500));

  // 2. アクティベーション前処理（重要：省略すると失敗率が高くなる）
  const r = target.getBoundingClientRect();
  target.dispatchEvent(new MouseEvent('mousedown', {bubbles:true, clientX: r.left+50, clientY: r.top+10}));
  target.dispatchEvent(new MouseEvent('mouseup', {bubbles:true, clientX: r.left+50, clientY: r.top+10}));
  target.dispatchEvent(new MouseEvent('click', {bubbles:true, clientX: r.left+50, clientY: r.top+10}));
  await new Promise(r => setTimeout(r, 300));

  // 3. Range選択
  const range = document.createRange();
  range.selectNodeContents(target);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);

  // 4. selectionchange イベント発火（これが無いと浮動ツールバーが出ない）
  document.dispatchEvent(new Event('selectionchange'));

  // 5. mouseup でツールバー表示をトリガー
  target.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, cancelable: true, clientX: r.left+100, clientY: r.top+20}));
  await new Promise(r => setTimeout(r, 700));

  // 6. 引用ボタンを探す（top 30〜innerHeight-30 の可視範囲で）
  const btns = document.querySelectorAll('button[aria-label="引用"]');
  let btn = null;
  for (const b of btns) {
    const br = b.getBoundingClientRect();
    if (br.width > 0 && br.top > 30 && br.top < window.innerHeight - 30) { btn = b; break; }
  }
  if (!btn) return 'no btn';

  // 7. クリック
  btn.click();
  await new Promise(r => setTimeout(r, 600));

  // 8. 検証
  const v = Array.from(document.querySelectorAll('.ProseMirror p')).find(p => p.textContent.startsWith(prefix));
  return v?.closest('blockquote') ? 'OK' : 'FAIL';
})();
```

#### 注意事項
- **バッチ処理禁止**: 1つのJS内で `for` ループで複数要素を処理しない。1段落につき1 `javascript_exec` 呼び出し
- **失敗時のリトライ**: 同じコードでもう一度呼ぶと通ることが多い（ProseMirror状態の安定化待ち）
- **click()がJSで効かない場合**: 座標を取得して `computer.left_click` で物理クリックに切り替える

### パターン13: UL → 中黒引用ブロック変換【既存記事編集】

既存の `<ul><li>` 箇条書きを `・` プレフィックス付きの段落に変換し、さらに引用ブロック化する。markdown `>` + `・` 形式を note.com 上で再現する。

#### Step 13-1: ULをパラグラフ化（リスト解除）

1. ULの最初のLIの左端を click で選択
2. 最後のLIの末尾を shift+click で選択範囲を拡張
3. `shift+End` で最終行末まで確実に選択
4. ツールバー「**リスト**」ボタン（`aria-label="リスト"`）をクリック → サブメニュー表示
5. サブメニューの「**指定なし**」ボタンをクリック

結果: `<ul><li><p>item1</p></li><li><p>item2</p></li></ul>` → `<p>item1<br>item2</p>` のような単一P（`<br>` で区切られた形式）

#### Step 13-2: 各行先頭に「・」を追加

```
1. 段落の y 座標を取得し、各行の中心 y = top + 18 + (36 * n) で計算
2. computer.left_click で line 1 をクリック
3. computer.key("Home") で行頭へ
4. computer.type("・")
5. computer.key("Down Home") で次行先頭へ
6. computer.type("・")
7. 行数分繰り返し
```

#### Step 13-3: 引用化

パラグラフ全体を選択してパターン12で引用化：
- triple_click ではなく Range API で `selectNodeContents(target)` を使う（複数行の `<br>` 区切りを含めて全選択できる）
- shift+click で全範囲を選択する方法も有効

### パターン14: 既存記事への新規セクション挿入【既存記事編集】

既存のH2見出しの前に新しいセクション（見出し + 本文）を挿入する。

#### 手順

```
1. ターゲットH2（挿入位置の直後にある既存H2）を特定
2. その直前にある空Pを探す（prev = konyu.previousElementSibling）
   - 多くの記事で空Pが存在。なければ type 前に Enter で新規Pを作る
3. 空Pの座標を取得して computer.left_click
4. computer.type("📩 新セクション見出し")
5. triple_click で段落を選択
6. ツールバー「見出し」ボタンクリック → ドロップダウン出現
7. 「大見出し」ボタンをクリック（H2化）
8. 見出しの末尾クリック → computer.key("End")
9. computer.key("Enter") で本文P作成
10. computer.type("本文1")
11. computer.key("Enter Enter") で空行を挟む
12. 次の本文をtype → 繰り返し
```

#### 見出しドロップダウンの選択肢

| ボタン | 効果 |
|---|---|
| 大見出し | H2 |
| 小見出し | H3 |

位置は都度 `getBoundingClientRect()` で取得する（スクロール位置で変わる）。

### パターン15: 既編集チェックヘルパー【既存記事編集】

複数箇所を編集する前後で現状をまとめて確認する。トグル事故の早期発見、リトライ時の対象絞り込みに必須。

```javascript
(() => {
  // テストケース: [プレフィックス, 表示ラベル]
  const tests = [
    ['A: 申し訳ございませんが', 'Q1A'],
    ['XToolsPro3は Windows', 'Q1-2'],
    ['対応OS：', 'Q1-3'],
    ['A: 本ツールへ登録', 'Q2'],
    // ... 以下、対象箇所を列挙
  ];
  const res = [];
  for (const [prefix, label] of tests) {
    const ps = Array.from(document.querySelectorAll('.ProseMirror p'));
    const match = ps.find(x => x.textContent.startsWith(prefix));
    res.push(`${label}:${match?.closest('blockquote') ? '✓' : '✗'}`);
  }
  return res.join(' ');
})();
```

#### 出力例
```
Q1A:✓ Q1-2:✓ Q1-3:✓ Q2:✓ Q3A:✓ Q3-2:✗ Q4:✓
```

この出力から「Q3-2 だけ未処理」と即判断でき、対象を絞って追加操作できる。

## 本文表現のガイドライン

### 文体: ですます調で統一

記事本文は **ですます調** を基本とする。「〜である」「〜だ」「〜と言う」等の常体（だ・である調）を混ぜない。

| NG (常体) | OK (ですます調) |
|---|---|
| 結論から言う。〜だ。 | 結論からお伝えします。〜です。 |
| 〜に跳ね上がる。 | 〜に跳ね上がります。 |
| 〜を作ってきた。 | 〜を作ってきました。 |
| 〜してほしい。 | 〜してください / 〜をご覧ください。 |

**Why:** 読者との距離感を一定に保ち、説明調の親しみやすさを担保するため。note記事の読者層（個人開発者・副業層）にはですます調の方が届きやすい。

**例外:** 箇条書き項目や図表の見出しなど短文は体言止め可。

### 冒頭まとめ文のNGフレーズ

記事冒頭の悩みパート直後に置く「まとめ文」では、以下のフレーズを **使用しない**：

| NG表現 | 理由 |
|---|---|
| `1つでも当てはまるなら、この記事はあなたのために書いた。` | 押しつけがましく昭和のセールスコピー感が強い。「あなた」への直接的な呼びかけが距離感として近すぎる |
| `〜は必読です。` / `絶対に〜すべき。` | 読者への命令調 |
| `これを知らないと損する。` | 煽り調 |

### 推奨する代替表現（ですます調）

読者判断を尊重したニュートラルな表現に置き換える：

- **推奨:** `1つでも当てはまるなら、この記事は最後まで読む価値があります。`
- **推奨:** `1つでも当てはまるなら、このまま読み進めてみてください。`
- **推奨:** `1つでも当てはまるなら、この記事がきっと役に立つはずです。`

**方針:** 焦点を「あなた(読者)」ではなく「記事の価値」側に寄せ、読者が自分で判断する形にする。命令・断定・煽りではなく、提案・示唆のトーンを使う。

## 絶対にやってはいけないこと

### 1. キーボードショートカットの使用禁止
以下のキーボードショートカットは **日本語キーボード環境で文字が入力されてしまう** ため、使用してはならない：

| ショートカット | 問題 |
|---|---|
| `Ctrl+Shift+8` | `*` が入力される |
| `Ctrl+Shift+>` | `>` が入力される |
| `Ctrl+Shift+9` | `)` が入力される |

これらのショートカットは ProseMirror のリスト・引用操作に割り当てられているが、日本語キーボードでは Shift キーとの組み合わせで文字が発生するため、**必ずツールバーボタンクリックまたはDOM直接操作を使う**。

### 2. triple_click の乱用
- 見出し直後の行で `triple_click` を使うと、見出しごと選択されてしまう
- テキスト選択には `click` → `Home` → `Shift+ArrowDown` → `Shift+End` の方式を使う

### 3. Ctrl+Z による Undo
- `Ctrl+Z` は JavaScript によるDOM操作も含めて巻き戻すため、意図しない箇所まで元に戻る可能性がある
- ミスした場合は **DOM再操作で修正** する

### 4. dispatchEvent の省略
- DOM操作後に `dispatchEvent(new Event('input', { bubbles: true }))` を呼ばないと、ProseMirror が変更を認識しない
- 保存時に変更が失われる原因になる

### 5. 引用ボタンの重複クリック（トグル事故）
- note.comの「引用」ボタンは**トグル動作**: 既に引用済みの要素に再度クリックすると引用解除される
- 失敗したと思って再試行すると、実は成功していた操作を取り消してしまう
- **対策**: パターン12の通り、処理前に `p.closest('blockquote')` で既引用チェック。`!p.closest('blockquote')` のフィルタで既引用を除外する

### 6. 1つのJSでバッチ引用化
- `for` ループで複数段落を連続処理すると、ProseMirror状態が中盤から壊れ浮動ツールバーが出なくなる
- **対策**: パターン12の通り、1段落 = 1 `javascript_exec` 呼び出しに分割する

## エラー対処

### 「エディタが見つかりません」
- `.ProseMirror` セレクタで見つからない場合、ページの読み込みを待つ
- `wait_for` で特定テキストの出現を待ってからリトライする

### 「テキストが見つかりません」
- 修正指示MDの対象テキストが実際のエディタ内テキストと一致しない
- `take_snapshot` でエディタ内の実際のテキストを確認し、修正指示を調整する
- 全角・半角の違い、改行位置の違いに注意

### DOM操作後に変更が反映されない
- `dispatchEvent` を忘れていないか確認
- `{ bubbles: true }` オプションが付いているか確認

### 引用ブロック化でレイアウトが崩れる
1. DOM直接操作で `<blockquote>` を作成した場合に発生する
2. **必ずパターン2（ツールバー方式）を使うこと**
3. 壊れた場合は、まずDOM操作で通常の `<p>` に戻してから、ツールバーの「引用」ボタンを使う
4. 手順: JS Selection APIでテキスト選択 → `take_snapshot` で「引用」ボタンのuid取得 → `click`

### 一時保存ボタンが見つからない
- ページ上部にスクロールする
- `find` ツールで「一時保存」を検索
- ボタンが無効化されている場合は、エディタ内でクリックしてフォーカスを与えてからリトライ

### スクリーンショットが真っ黒になる（既存記事編集時）
- note.comエディタは `scrollY > ~5000px` 付近でスクリーンショットが真っ黒になる現象あり
- エディタ自体は機能しておりDOM操作は効く
- **対策**: 視覚確認が必要な時は `window.scrollTo(0, 0)` で一旦最上部に戻す
- DOM状態確認はJSで `JSON.stringify(...)` を使い、スクリーンショットに依存しない

### 浮動ツールバーが出現しない
- `selectionchange` イベントを発火させていない可能性が高い
- **対策**: パターン12の手順で `document.dispatchEvent(new Event('selectionchange'))` を明示発火
- 加えて、対象要素への `mousedown/mouseup/click` でアクティベーションを行う
- それでも出ない場合は、対象要素に triple_click を物理操作で実行してから JS で Range を上書きする

### 引用化したはずが元に戻っている
- 「引用」ボタンのトグル動作が原因（禁止事項5参照）
- 連続処理中に既引用要素に再クリックしてしまっている
- **対策**: `find` 時のフィルタを `!p.closest('blockquote')` にして既引用を除外する
- パターン15のチェックヘルパーで処理前後の状態を確認して早期発見

## バージョン履歴

- ver 2.9 - 2026/04/19 - 既存記事の部分編集パターンを新設。引用ボタンのトグル動作・ProseMirror選択イベント順序（selectionchange必須）・UL中黒変換・新規セクション挿入・既編集チェックの4パターン（12〜15）を追加。禁止事項に「引用ボタン重複クリック」「1JSバッチ引用化」、エラー対処に「スクリーンショット真っ黒」「浮動ツールバー非表示」「引用の消失」を追記
- ver 2.8 - 2026/04/18 - 「本文表現のガイドライン」を新設。文体はですます調で統一するルールを追加。冒頭まとめ文の押しつけがましいNGフレーズ（「この記事はあなたのために書いた。」等）を禁止し、「最後まで読む価値があります」等のニュートラルな推奨表現（ですます調）に切り替え
- ver 2.7 - 2026/04/10 - Step 3.5（アイキャッチ画像アップロード）を追加。サムネイルは「画像を追加」→「画像をアップロード」→ file input経由。自動化の制限事項を記載
- ver 2.6 - 2026/04/10 - テーブル変換ルールを変更: テキスト変換 → 箇条書き(`<ul><li>`)に変換。列挙データはリスト化する
- ver 2.5 - 2026/04/10 - Step 2: `note.com/notes/new` 経由での遷移に修正（editor.note.comへの直接アクセスはAccess Deniedになる）。Step 5: 引用変換にtriple_click方式の注意事項を追加（JS Selection APIだけではProseMirrorが認識しない）
- ver 2.4 - 2026/03/08 - パターン10: まとめ文（「こんな悩みを抱えていませんか？」）を引用外に配置するルールに変更
- ver 2.3 - 2026/03/08 - パターン11（冒頭あいさつ文挿入）を新設。処理フローStep 4に反映
- ver 2.2 - 2026/03/08 - パターン9のH3対応を追加。パターン10（冒頭悩みパートの引用+中黒箇条書き化）を新設
- ver 2.1 - 2026/03/08 - パターン9（H2見出し画像挿入）を追加。画像ペースト後の空行削除ステップを含む。処理フローにStep 5.5を新設
- ver 2.0 - 2026/03/08 - 新規投稿フローに全面改訂。記事MDファイルから直接投稿する方式に変更。パターン8（記事一括挿入）とMarkdown変換ルールを追加
- ver 1.2 - 2026/02/21 - 公開フロー（Step 6）とハッシュタグ追加パターン（パターン7）を追加。公開設定ページの構成、ハッシュタグ選定指針を記載
- ver 1.1 - 2026/02/21 - パターン2（引用ブロック化）をJS Selection API + ツールバーボタン方式に改訂。DOM直接操作が壊れる問題と正しい手順を記載。ブロックレベルツールバーのボタン一覧を追加
- ver 1.0 - 2026/02/20 - 初版作成。ProseMirrorエディタ操作パターン、禁止事項、エラー対処を集約
