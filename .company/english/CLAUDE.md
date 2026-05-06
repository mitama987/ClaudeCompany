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
│   ├── NN-xxx.en.md     ← 英語のみ（TTS入力。口語＋少しフォーマル）
│   └── NN-xxx.bi.md     ← 1文ごと英→日のバイリンガル（読解・シャドーイング用）
└── routine/             ← 日々の練習ログ（YYYY-MM-DD.md）
```

音声: `outputs/english/audio/NN-xxx.mp3`（gitignore済み）
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
2. **英訳（英語のみ）**: 秘書が `scripts/NN-xxx.en.md` を生成（音読・TTSの本体）
3. **バイリンガル版**: 同じ内容を `scripts/NN-xxx.bi.md` に「1文 EN → 1文 JA」の対訳形式で生成
4. **音声化**: `uv run python scripts/english_tts/gen_audio.py --topic NN`（入力は `.en.md` のみ）
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
```markdown
---
topic: 01-life-flow
words: 約NNN
est_minutes: N.N
voice: alloy
speed: 1.0
---

# Life Flow

(1〜2分の段落 × 数本。contractions多用、つなぎ表現入り)
```

### `scripts/NN-xxx.bi.md` （バイリンガル・読解／シャドーイング用）
- 1文 EN → 直下に 1文 JA の対訳形式
- セクション見出し（`## §1. ... / ...`）でブロック分け
- TTS入力には**使わない**（`.en.md` のみが入力）
- 文単位なので EN を見ながら意味確認、または JA を読んで EN を口頭で言う練習にも使える

```markdown
---
topic: 01-life-flow
type: bilingual
voice: alloy
speed: 1.0
---

# Life Flow / 人生の流れ

## §1. Section title / 見出し

So, where do I start?
さて、どこから話そうか。

(EN文 → JA訳 のペアを空行区切りで続ける)
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
