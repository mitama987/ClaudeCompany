# 2026-05-01 学び

## ccnest 修正が「反映されない」問題の正体

ソースを直して commit/push しても、`ccnest` コマンド実体は cargo bin の `.exe` が呼ばれる。ここを再ビルドしないと cmd を開き直しても古いまま。

- PATH 優先: `C:\Users\mitam\scoop\apps\rustup\current\.cargo\bin\` (cargo install 系) → `C:\Users\mitam\AppData\Roaming\npm\` (npm 系)
- cargo bin 実体は scoop persist 経由: `C:\Users\mitam\scoop\persist\rustup\.cargo\bin\ccnest.exe`
- 反映手順:
  1. `cargo build --release` で target/release に新 exe を作る
  2. `cargo install --path . --force` を試す
  3. **実行中の ccnest があると os error 5 で move 失敗**するので、その場合は旧 exe を `Rename-Item` で `.old-<timestamp>` に逃して、新 exe を `Copy-Item -Force` で配置 (Windows は実行中exeの rename は許可、上書きは不可)
- 動いていた 2 プロセスは旧バイナリのままメモリ常駐 → 新規 cmd で立ち上げ直すと最新版が動く

詳細はメモリ `feedback_ccnest_reinstall_windows.md` に保存済み。

## 関連

- ccnest の最新コミット (2026-05-01 18:01 main): tab click switching / Ctrl+click URL open / Alt+F rename / chat double-click line select 等。これらが今日の再ビルドで初めて手元バイナリに入った。
- npm 配布版 (`ccnest-cli`) を更新するには別途 git tag push → GitHub Actions で自動 publish の流れが必要 (Cargo.toml は v0.1.3 のまま、新タグ未発行)。
