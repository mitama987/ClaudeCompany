# XToolsPro3 Rich LP

## Purpose

ObsidianのXToolsPro3 noteLPを、GitHub Pagesで公開できる短いHTML/CSSランディングページへ再構成する。

## Source

- Source note: `C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\有料版\【本書】note記事_XToolsPro3更新版（買い切りのみ）.md`
- Reference assets: `C:\Users\mitam\Desktop\work\82_xtp3-lp\assets\images\*.webp`
- Public feature assets: `docs/assets/images/*.png`
- Public entry: `docs/index.html`

## Content Rules

- noteLPの長い実績談、更新履歴、細かい仕様説明は削る。
- 残す訴求は、API不要、ランダム投稿、プロキシ、コミュニティ投稿、自動DM、Amazon在庫復活、買い切り価格。
- 価格は無料版、買い切り + アドオン、フル買切りの3プランに整理する。
- 購入前の注意点として、Windows専用、プロキシ別契約、24時間運用条件を明記する。

## Implementation Notes

- GitHub Pagesの`/docs`公開に合わせ、外部ビルド不要の静的HTML/CSS/JSにする。
- 画像は`docs/assets/images/`配下のローカル画像を使う。機能図解と比較表はPNG、開発者プロフィールは参照LPのWebPを使う。
- 主要リンクは既存noteLP内のThe Apps、note、Google Forms、購入後手順書URLを使う。
- UIは紙白、くすみオレンジ、深緑、青を使い、過度な装飾や長文ブロックを避ける。
- TDDとして`tests/test_docs_site.py`でLP本文、画像、アクセシビリティ、Version Historyを検査する。

## Version History

- ver1.0 - 2026-05-06 - XToolsPro3 noteLPからGitHub Pages向け短縮リッチLPへの再構成方針を追加。
- ver1.1 - 2026-05-06 - feature項目を説明先行レイアウトへ変更し、画像をリッチなSVG図解に差し替える方針を追加。
- ver1.2 - 2026-05-06 - SVG図解からGPT Images 2生成のPNG画像へ差し替える方針を追加。
- ver1.3 - 2026-05-06 - コミュニティ投稿、自動DM、Amazon在庫復活もフル幅表示に統一し、自動DMとAmazon在庫復活の図解を簡潔化。
- ver1.4 - 2026-05-06 - ヒーロー見出しを常時2行表示にし、FAQのアカウント数目安を具体化。
- ver1.5 - 2026-05-06 - 現行ミニマム版を`docs/index-minimal.html`に保存し、参照LPから選ばれる理由・基本版・アドオン・比較・信頼材料を短く追加。
- ver1.6 - 2026-05-06 - 追加章のカード階層、アドオンCTA、比較表ハイライト、信頼材料パネルをリッチ化。
- ver1.7 - 2026-05-06 - 参照LPをもとにFAQを拡充し、ミニマム版は維持する方針を追加。
- ver1.8 - 2026-05-06 - 信頼材料章を削除し、アドオン詳細トグル・画像比較・開発者紹介章に再構成する方針を追加。
- ver1.9 - 2026-05-06 - 3プラン比較画像をカード型ではなく表形式の比較表画像として作成する方針へ修正。
