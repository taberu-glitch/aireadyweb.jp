# AI Ready Web — 静的サイト 制作メモ

## 構成
- index.html                      トップページ（LP。CSS/JSは内包、セルフ診断のみ assets を参照）
- service/                        サービス詳細（Service 構造化データの主ページ）
- ai-search-check/                無料AI検索診断（セルフ診断 + 申込フォーム）
- growth/                         AI Search Growth（継続運用）
- knowledge/                      ナレッジ一覧 + 記事 9 本（結論→定義→理由→具体例→注意点→関連）
- industry/                       業種別一覧 + construction/（工務店・リフォーム）
- research/                       Research（観測方法）+ ai-visibility-report-2026-09/（テンプレート・noindex）
- about/                          運営会社（内容未設定・noindex）
- contact/                        お問い合わせ
- assets/base.css, site.js        下層ページ共通
- assets/hearing.css, hearing.js  セルフ診断（トップと診断ページで共用）
- robots.txt / sitemap.xml

## 公開前に必ず行うこと
1. 本番URL：`https://aireadyweb.jp/` に設定済み（canonical / og:url / JSON-LD / sitemap / robots）。
   変更する場合は src/content.py の SITE_URL と、index.html 内の URL を置換して再ビルド。www を使う場合は www → 非www へリダイレクトを設定。
2. 運営会社：株式会社ハブグラム（about/ と Organization に設定済み）。所在地を掲載する場合は src/content.py の COMPANY と build.py の org() / about_page() に追加。
3. フォーム送信先：FormSubmit（https://formsubmit.co/all@hubgram.jp）に設定済み。
   ★初回の送信後、all@hubgram.jp に届く「Activate Form」メールのリンクを押すまでメールは転送されません（1回だけ）。
   送信後は /contact/thanks/ に戻ります。別のサービスに変える場合は src/content.py の FORM_ENDPOINT と index.html の CONFIG.FORM_ENDPOINT。
4. プライバシーポリシー：/privacy/ を作成済み（制定日 2026-09-25）。公開前に内容を確認し、必要なら法務レビュー。
5. Research レポート：実施後に数値を記入 → noindex を外す → sitemap に追加。存在しない数値は記載しない。
6. 税区分、Subscription の契約条件（期間・解約・所有権・データ移管）の確定と反映。

## ページを追加するとき
- ナレッジ記事：src/content.py の KNOWLEDGE に辞書を追加して `python3 src/build.py`。
  結論（answer）→ 定義 → 理由 → 具体例 → 注意点 の順を守り、保証表現は使わない。
- 業種別ページ：INDUSTRY_CONSTRUCTION を参考に、業種ごとの「顧客がAIに聞く質問」「検索行動」「必要な情報」「選定基準への答え」を独自に書く。テンプレート文章の使い回しはしない。
- 月次レポート：research/ai-visibility-report-YYYY-MM/ を複製し、REPORT_FIELDS の項目を実データで埋める。

## エンティティの統一
サービス名 / カテゴリー / 対象 / 提供価値 / AEOの定義 は src/content.py の ENTITY で一元管理し、全ページのフッターと構造化データに反映しています。

## GitHub Pages で公開する
リポジトリ直下に src/ と .github/workflows/pages.yml を置き、GitHub の Settings → Pages → Source を「GitHub Actions」にすると、
push のたびに src からビルドして公開されます（dist/ はビルド結果。直接編集しない）。
カスタムドメインは Settings → Pages → Custom domain に aireadyweb.jp を入力し、DNS（Aレコード4件 / www の CNAME）を設定。

## ローカル確認
ディレクトリ形式のURL（/knowledge/what-is-aeo/）を使っているため、ローカルでは簡易サーバーで確認してください。
  cd dist && python3 -m http.server 8000  → http://localhost:8000/

## sitemap 収録URL（20）
- https://aireadyweb.jp/
- https://aireadyweb.jp/service/
- https://aireadyweb.jp/ai-search-check/
- https://aireadyweb.jp/growth/
- https://aireadyweb.jp/knowledge/
- https://aireadyweb.jp/knowledge/what-is-aeo/
- https://aireadyweb.jp/knowledge/aeo-vs-seo/
- https://aireadyweb.jp/knowledge/what-is-geo/
- https://aireadyweb.jp/knowledge/how-to-appear-in-chatgpt/
- https://aireadyweb.jp/knowledge/ai-search-friendly-website/
- https://aireadyweb.jp/knowledge/how-to-choose-ai-search-web-company/
- https://aireadyweb.jp/knowledge/do-smes-need-ai-search/
- https://aireadyweb.jp/knowledge/how-to-get-cited-by-ai/
- https://aireadyweb.jp/knowledge/ai-era-web-production-difference/
- https://aireadyweb.jp/industry/
- https://aireadyweb.jp/industry/construction/
- https://aireadyweb.jp/research/
- https://aireadyweb.jp/about/
- https://aireadyweb.jp/privacy/
- https://aireadyweb.jp/contact/
