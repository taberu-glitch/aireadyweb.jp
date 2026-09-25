# aireadyweb.jp — AI Ready Web サイト

- `src/`  … 生成元（content.py = 文言・記事、build.py = テンプレート、top.html = トップページ本文、*.css / *.js）
- `dist/` … ビルド結果（公開されるファイル）。**直接編集しない**。`python3 src/build.py` で再生成
- `.github/workflows/pages.yml` … main に push すると自動でビルドして GitHub Pages に公開

## 更新のしかた
1. `src/content.py`（文言・記事）や `src/top.html`（トップ）を編集
2. `python3 src/build.py` でローカル確認（`cd dist && python3 -m http.server 8000`）
3. commit → push（main）→ 数十秒〜数分で https://aireadyweb.jp/ に反映

詳細は `dist/README.md`（公開前チェック・ページ追加のしかた）を参照。
