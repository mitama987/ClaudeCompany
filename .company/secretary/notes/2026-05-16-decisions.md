# 意思決定ログ 2026-05-16

## /insights フリクション分析 → 再発防止策の全面実施

`/insights`（200セッション / 506h / 220コミット, 2026-04-15〜05-15）のフリクション分析を深掘りし、再発防止策を全て実装した。

### 背景：フリクションの根本原因
- 根っこは「**Claudeが中間ステップの成功を最終成果と取り違える**」こと
- 主要カテゴリ: buggy_code (28回), wrong_approach (22回)
- 象徴例: SuperMovieで全8ステップのプロジェクトデータを生成したのにmp4を未レンダで「完了」報告 → 「動画はどこ？」

### 実施した対策（3点 + 記録）

1. **グローバル `~/.claude/CLAUDE.md` に5つのガードレール節を追記**
   - Media & Build Deliverables: 最終成果物の存在・サイズ検証をDoneの定義に
   - Testing & Verification: ボタン押下で止めず実end stateを検証 / 初手失敗時は根本原因へ
   - Image Generation: アセット種別ごとの指定モデル厳守（サムネ図解=gpt-image-2, 挿絵=Gemini）、無指定なら確認
   - Local Server & Environment: uv必須 / ポート空き確認＆フォールバック / stale プロセスkill
   - Git & Repository Conventions: public-by-default、private/PRワークフローは明示依頼時のみ

2. **`render-video` スキル新規作成**（`~/.claude/skills/render-video/`）
   - 不変条件「最終mp4が存在・サイズ>0・尺>0を検証するまで未完了」
   - Step1特定 → Step2実レンダ → Step3 ffprobe検証 → Step4原因追及 → Step5証跡つき報告

3. **commit前テストフック追加**（`~/.claude/settings.json` PreToolUse + `~/.claude/hooks/pre-commit-tests.sh`）
   - `Bash(git commit:*)` 時に高速ユニットテストを実行、失敗ならコミットをブロック
   - 厳重ガード: テスト構成が明確な時のみ実行 / e2e・slow・liveマーカー除外 / Rustは対象外（既存skill+Stopレビューに委譲）
   - エスケープハッチ: `touch .skip-precommit`（cwd or `~/.claude/`）

### 検証
- settings.json: 有効JSON確認済み
- pre-commit-tests.sh: `bash -n` 構文OK
- render-video: スキル一覧に表示確認済み

### 設計判断のメモ
- フック本体はJSON内インラインを避け外部スクリプト化（巨大JSONエスケープ事故 / auto-modeブロック回避）
- 既存のXTP限定Stopレビューと同じ「スコープ＋スキップガード厳重」流儀を踏襲
- pytestは `-m "not e2e and not slow and not live"` でライブE2Eの毎コミット実行を防止（RPA系の重い/対話的テスト対策）
