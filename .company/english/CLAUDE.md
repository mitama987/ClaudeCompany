# 英語学習部署

## 役割
オーナーの「自分プロファイル英語化＋暗記」プロジェクトの本拠地。初対面の英語ネイティブとの1〜2時間の会話で出てくる定型トピックを、日本語インタビュー → 口語＋少しフォーマルの英訳 → OpenAI TTSで音声化、までワンセットで運用する。

## 窓口
- オーナーは秘書経由で英語部署にアクセスする（窓口は秘書）
- 秘書がインタビュー進行・整理・英訳・TTS実行までワンストップで担当する

## ディレクトリ
```
.company/english/
├── CLAUDE.md            ← このファイル
├── profile/             ← 日本語インタビュー結果（生メモ）
├── scripts/             ← 英訳スクリプト
│   ├── NN-xxx.en.md     ← 英語のみ（TTS入力。口語＋少しフォーマル、ブロックマーカー付き）
│   └── NN-xxx.bi.md     ← 1文ごと英→日のバイリンガル（読解・シャドーイング用、ブロック見出し付き）
├── audio/               ← 生成 mp3（gitignore済み）
│   ├── NN-xxx.mp3       ← フル音声
│   └── NN-xxx/          ← ブロック分割
│       └── bMM-slug.mp3
└── routine/             ← 日々の練習ログ（YYYY-MM-DD.md）
```

TTSコード: `scripts/english_tts/gen_audio.py`

## 17トピック（順番）
1. life-flow（人生の流れ全部）
2. school（学校で勉強したこと）
3. current-job（今の仕事 + 業界の現在地・市況・展望）
4. career-path（職歴の変遷）
5. turning-points（人生のターニングポイント）
6. values（大事にしている価値観）
7. future（将来やりたいこと）
8. worries（今悩んでいること）
9. hobbies（好きなこと・趣味）
10. weekends（休日の過ごし方）
11. travel-food（旅行・食の好み）
12. places-lived（住んだところ）
13. family（家族・パートナー）
14. friends（友達）
15. favorite-places（好きな場所・紹介したいところ）
16. japan-views（日本のいいところ・問題だと思うところ）
17. why-english（英語勉強のきっかけ）

## 1トピックのループ
1. **インタビュー**: 秘書が日本語で5〜8問の深掘り質問。回答を `profile/NN-xxx.md` に整理
2. **英訳（英語のみ）**: 秘書が `scripts/NN-xxx.en.md` を生成。**約20個の暗記単位ブロック**に切って `<!-- BLOCK NN: title -->` マーカーを挿入する
3. **バイリンガル版**: 同じ20ブロックの順で `scripts/NN-xxx.bi.md` に `### BNN. タイトル / 和題` 見出し付きで「1文 EN → 1文 JA」を並べる
4. **音声化**: `uv run python scripts/english_tts/gen_audio.py --topic NN`（入力は `.en.md`）
   - フル音声 `audio/NN-xxx.mp3` と、ブロック別 `audio/NN-xxx/bMM-slug.mp3` の両方を自動生成
5. **練習ログ**: 任意で `routine/YYYY-MM-DD.md` に記録

## 英訳スタイル（固定）
- **基調**: 話し言葉ベース（contractions多用: I'm / gonna / kinda / wanna）
- **つなぎ表現を入れる**: you know, I mean, actually, like, sort of, to be honest
- **仕事・社会の話題は少しフォーマル寄り**: 業界用語は崩さない、文末は丁寧
- **段落単位で1〜2分の塊**: 音読しやすい長さに区切る
- **ファイル先頭にメタ**: トピック名、語数、想定音声尺
- **印刷可能**: 紙に出してそのまま読める段落構成にする

## profile/ の書き方
- 質問→回答のQ&A形式でも、トピック単位の散文でもOK
- 回答漏れがあれば秘書が追加質問して埋める
- 同日に複数トピック触ったら、ファイルは別（トピックファイル単位）

## scripts/ の書き方

### `scripts/NN-xxx.en.md` （英語のみ・TTS本体）
- 約20個の暗記単位ブロックに `<!-- BLOCK NN: title -->` マーカーを置く
- マーカーがあると gen_audio.py が「フルmp3」＋「ブロック別mp3」を自動生成する
- マーカーが無ければフルmp3のみ
- ブロックタイトルは英語の短い説明（mp3ファイル名のslugになる）

```markdown
---
topic: 01-life-flow
words: 約NNN
est_minutes: N.N
voice: alloy
speed: 1.0
blocks: 20
---

# Topic Title

<!-- BLOCK 01: short english title -->
(2〜4文の塊。1分以内で言い切れる粒度)

<!-- BLOCK 02: another title -->
(2〜4文)

...
```

### `scripts/NN-xxx.bi.md` （バイリンガル・読解／シャドーイング用）
- `.en.md` と**同じブロックNNの順**で `### BNN. EN title / 和題` を見出しに
- 各ブロック内は「1文 EN → 1文 JA」を空行区切りで並べる
- TTS入力には**使わない**（`.en.md` のみが入力）
- mp3 (`bNN-slug.mp3`) と1:1で対応するので、聴きながら .bi.md の同じ BNN を見れば意味確認できる

```markdown
---
topic: 01-life-flow
type: bilingual
voice: alloy
speed: 1.0
blocks: 20
---

# Topic Title / 和題

> 各ブロックは `audio/NN-xxx/bNN-slug.mp3` に対応。

---

### B01. Block title / 和訳タイトル

So, where do I start?
さて、どこから話そうか。

I was born in 1989 ...
1989 年 ...

---

### B02. ...
```

## TTS仕様
- model: `gpt-4o-mini-tts` または `tts-1`
- voice: `alloy` 固定
- speed: `1.0` 固定
- format: `mp3`
- 既存ファイルは skip、`--force` で上書き

## ルール
- 同じ日付の `routine/` ファイルは追記、新規作成しない
- ファイル操作前に必ず今日の日付を確認
- 英訳は一気に全文出さず、段落ごとにオーナーに見せて確認できる粒度で
