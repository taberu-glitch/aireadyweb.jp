# -*- coding: utf-8 -*-
"""AI Ready Web — 静的サイトビルド
使い方:  python3 build.py   → ../dist/ に全ページを生成
"""
import os, json, shutil, re, html, datetime
from content import *

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
DIST = os.path.join(ROOT, "dist")
TOP_SRC = os.path.join(SRC, "top.html")  # トップページ（本文）ソース

def esc(t): return html.escape(t, quote=True)
def rel(depth): return "../" * depth
def W(t): return t.replace("¦", "<wbr>")

def jsonld(obj): return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n</script>'

def org(): return {"@type":"Organization","@id":SITE_URL+"#organization","name":COMPANY["name"],"url":SITE_URL,"email":COMPANY["email"],"brand":{"@type":"Brand","name":ENTITY["name"]},"description":ENTITY["name"]+"（"+ENTITY["category"]+"）を運営。"+ENTITY["value"]+"。","areaServed":"JP"}
def website(): return {"@type":"WebSite","@id":SITE_URL+"#website","name":ENTITY["name"],"url":SITE_URL,"description":ENTITY["tagline"],"inLanguage":"ja","publisher":{"@id":SITE_URL+"#organization"}}
def service_ref(): return {"@id": SITE_URL + "#service"}

def breadcrumb_ld(crumbs):
    return {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE_URL+p} for i,(n,p) in enumerate(crumbs)]}

def header(depth, current=""):
    R = rel(depth)
    items = [("service/","サービス"),("ai-search-check/","無料診断"),("growth/","継続運用"),("knowledge/","ナレッジ"),("industry/","業種別"),("research/","Research")]
    lis = "".join('<li><a href="%s%s"%s>%s</a></li>' % (R,p, ' aria-current="page"' if current.startswith(p) else '', n) for p,n in items)
    return f'''<a class="skip" href="#main">本文へ移動</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{R}"><i aria-hidden="true"></i>AI Ready Web</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" id="menu-btn"><span class="menu-icon" aria-hidden="true"><span></span></span><span>メニュー</span></button>
    <nav class="site-nav" id="site-nav" aria-label="サイトメニュー">
      <ul>{lis}</ul>
      <a class="btn btn-primary btn-sm" href="{R}ai-search-check/">無料で診断する</a>
    </nav>
  </div>
</header>'''

def footer(depth):
    R = rel(depth)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-def" id="definition">
      <h4>AI Ready Webとは</h4>
      <dl>
        <div><dt>サービス名</dt><dd>{ENTITY["name"]}</dd></div>
        <div><dt>サービスカテゴリー</dt><dd>{ENTITY["category"]}</dd></div>
        <div><dt>対象</dt><dd>{ENTITY["audience"]}</dd></div>
        <div><dt>主な提供価値</dt><dd>{ENTITY["value"]}</dd></div>
        <div><dt>AEO（AI検索最適化）の定義</dt><dd>{ENTITY["aeo"]}</dd></div>
      </dl>
    </div>
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{R}"><i aria-hidden="true"></i>AI Ready Web</a>
        <p>{ENTITY["tagline"]}</p>
      </div>
      <div class="footer-col">
        <h4>Service</h4>
        <ul>
          <li><a href="{R}service/">AI Ready Web（サービス詳細）</a></li>
          <li><a href="{R}ai-search-check/">無料AI検索診断</a></li>
          <li><a href="{R}growth/">AI Search Growth（継続運用）</a></li>
          <li><a href="{R}industry/">業種別AI検索対策</a></li>
          <li>導入事例<span class="soon">準備中</span></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Knowledge</h4>
        <ul>
          <li><a href="{R}knowledge/">AI検索・Web集客ナレッジ</a></li>
          <li><a href="{R}knowledge/what-is-aeo/">AEOとは？</a></li>
          <li><a href="{R}knowledge/aeo-vs-seo/">AEOとSEOの違い</a></li>
          <li><a href="{R}knowledge/how-to-appear-in-chatgpt/">ChatGPTに自社を表示させるには</a></li>
          <li><a href="{R}research/">Research（AI検索の観測記録）</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="{R}about/">運営会社</a></li>
          <li><a href="{R}contact/">お問い合わせ</a></li>
          <li><a href="{R}privacy/">プライバシーポリシー</a></li>
        </ul>
      </div>
    </div>
    <div class="copyright">
      <span>&copy; <span id="copy-year">2026</span> {COMPANY["name"]} / AI Ready Web</span>
      <span>運営：{COMPANY["name"]}</span>
    </div>
  </div>
</footer>'''

def crumbs_html(depth, crumbs):
    R = rel(depth)
    items = []
    for i,(n,p) in enumerate(crumbs):
        if i == len(crumbs)-1: items.append(f'<li aria-current="page">{esc(n)}</li>')
        else: items.append(f'<li><a href="{R}{p}">{esc(n)}</a></li>')
    return f'<nav aria-label="現在位置"><ol class="crumbs">{"".join(items)}</ol></nav>'

def page(path, title, desc, body, crumbs, ld_graph, noindex=False, extra_head="", extra_scripts="", inline_css=False, current=""):
    depth = path.count("/")
    R = rel(depth)
    url = SITE_URL + path
    graph = [org(), website()] + ld_graph
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">'
    css = f'<style>{open(os.path.join(SRC,"base.css"),encoding="utf-8").read()}</style>' if inline_css else f'<link rel="stylesheet" href="{R}assets/base.css">'
    doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{robots}
<meta property="og:type" content="{'article' if any(g.get('@type')=='Article' for g in ld_graph) else 'website'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="AI Ready Web">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;700&family=Instrument+Sans:wght@500;600;700&display=swap">
{css}
{extra_head}
{jsonld({"@context":"https://schema.org","@graph":graph})}
</head>
<body>
{header(depth, current or path)}
<main id="main">
  <div class="wrap">
    {crumbs_html(depth, crumbs)}
  </div>
{body}
</main>
{footer(depth)}
<script>window.AIRW_CONFIG={{FORM_ENDPOINT:"{FORM_ENDPOINT}",THANKS_URL:"{THANKS_URL}"}};</script>
<script src="{R}assets/site.js"></script>
{extra_scripts}
</body>
</html>
'''
    out = os.path.join(DIST, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    return url

# ---------------------------------------------------------------- 記事系の部品
def related_cards(depth, slugs, services):
    R = rel(depth)
    out = []
    by = {a["slug"]: a for a in KNOWLEDGE}
    for s in slugs:
        a = by[s]
        out.append(f'<a href="{R}knowledge/{s}/"><span class="r-k">Knowledge</span><span class="r-t">{esc(a["h1"])}</span><span class="r-d">{esc(a["answer"][0][:60])}…</span></a>')
    for s in services:
        k, t, d, p = SERVICES[s]
        out.append(f'<a href="{R}{p}"><span class="r-k">{k}</span><span class="r-t">{esc(t)}</span><span class="r-d">{esc(d)}</span></a>')
    return '<div class="related">' + "".join(out) + '</div>'

def faq_html(faqs):
    items = []
    for q,a in faqs:
        items.append(f'<details><summary><span class="q" aria-hidden="true">Q</span><span>{esc(q)}</span><span class="chev" aria-hidden="true"></span></summary><div class="a"><p>{esc(a)}</p></div></details>')
    return '<div class="faq-list">' + "".join(items) + '</div>'

def faq_ld(faqs):
    return {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}

def cta_band(depth, title="まずは、AIから自社がどう見えているか知ることから。", text="会社名・URLなど数項目で申し込める無料AI検索診断で、想定質問での登場状況と改善ポイントを確認できます。特定のAIサービスでの表示を保証するものではありません。"):
    R = rel(depth)
    return f'''<div class="cta-band">
  <div><h2>{esc(title)}</h2><p>{esc(text)}</p></div>
  <div class="actions"><a class="btn btn-primary" href="{R}ai-search-check/">自社のAI検索状況を無料で診断する</a><a class="btn btn-ghost" href="{R}contact/">料金・制作について相談する</a></div>
</div>'''

def article_page(a, section_key, section_name, path_prefix):
    path = f"{path_prefix}{a['slug']}/"
    depth = path.count("/")
    R = rel(depth)
    secs = []
    toc = []
    for i,(h2,body_html) in enumerate(a["sections"]):
        sid = f"s{i+1}"
        toc.append(f'<li><a href="#{sid}">{esc(h2)}</a></li>')
        secs.append(f'<section id="{sid}"><h2>{esc(h2)}</h2>{body_html}</section>')
    toc.append('<li><a href="#related">関連サービス・関連する質問</a></li>')
    toc.append('<li><a href="#faq">よくある質問</a></li>')
    answer = "".join(f"<p>{esc(p)}</p>" for p in a["answer"])
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head">
      <p class="eyebrow"><span class="jp">{esc(section_name)}</span></p>
      <h1>{esc(a["h1"])}</h1>
      <div class="answer"><p class="answer-label">この質問への答え</p>{answer}</div>
      <div class="doc-meta"><span>公開日 <b>{PUBLISHED}</b></span><span>更新日 <b>{PUBLISHED}</b></span><span>発信 <b>AI Ready Web</b></span></div>
    </header>
    <nav class="toc" aria-label="このページの内容"><p class="toc-title">このページの内容</p><ol>{"".join(toc)}</ol></nav>
    {"".join(secs)}
    <section id="related"><h2>関連サービス・関連する質問</h2>
      <p>この内容に関係するAI Ready Webのサービスと、あわせて読まれている質問です。</p>
      {related_cards(depth, a["related"], a["services"])}
    </section>
    <section id="faq"><h2>よくある質問</h2>{faq_html(a["faqs"])}</section>
  </article>
  {cta_band(depth)}
</div>'''
    url = SITE_URL + path
    ld = [
        {"@type":"WebPage","@id":url+"#webpage","url":url,"name":a["title"],"description":a["desc"],"inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"},"about":service_ref()},
        dict(breadcrumb_ld([("ホーム",""),(section_name,path_prefix),(a["h1"],path)]), **{"@id":url+"#breadcrumb"}),
        {"@type":"Article","@id":url+"#article","headline":a["h1"],"description":a["desc"],"inLanguage":"ja","datePublished":PUBLISHED,"dateModified":PUBLISHED,"author":{"@id":SITE_URL+"#organization"},"publisher":{"@id":SITE_URL+"#organization"},"mainEntityOfPage":{"@id":url+"#webpage"},"articleSection":section_name},
        faq_ld(a["faqs"]),
    ]
    page(path, a["title"], a["desc"], body, [("ホーム",""),(section_name,path_prefix),(a["h1"],path)], ld, current=path_prefix)
    return path

# ---------------------------------------------------------------- 一覧ページ
def knowledge_index():
    path = "knowledge/"; depth = 1; R = rel(depth)
    cards = "".join(f'<a class="card" href="{a["slug"]}/"><span class="c-k">Knowledge</span><span class="c-t q">{esc(a["h1"])}</span><span class="c-d">{esc(a["answer"][0])}</span></a>' for a in KNOWLEDGE)
    body = f'''
<div class="wrap page">
  <div class="page-head">
    <p class="eyebrow"><span class="jp">ナレッジ</span></p>
    <h1>AI検索・Web集客ナレッジ</h1>
    <p class="lead">「AEOとは？」「ChatGPTに自社を表示させるには？」など、経営者の方からよくいただく質問に、結論から順に答えています。各ページは、結論 → 定義 → 理由 → 具体例 → 注意点 → 関連サービスの順で構成し、人にもAIにも読み取りやすい形で書いています。</p>
  </div>
  <div class="cards three">{cards}</div>
  {cta_band(depth)}
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"CollectionPage","@id":url+"#webpage","url":url,"name":"AI検索・Web集客ナレッジ｜AI Ready Web","description":"AEO・GEO・ChatGPT検索対策・AI検索に強いホームページなど、AI時代のWeb集客に関する質問に結論から答えるナレッジ。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("ナレッジ",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "AI検索・Web集客ナレッジ｜AI Ready Web", "AEO・GEO・ChatGPT検索対策・AI検索に強いホームページなど、AI時代のWeb集客に関する質問に結論から答えるナレッジ一覧。", body, [("ホーム",""),("ナレッジ",path)], ld)

def industry_index():
    path = "industry/"; depth = 1
    live = f'<a class="card" href="construction/"><span class="c-k">Industry</span><span class="c-t">{esc(INDUSTRY_CONSTRUCTION["h1"])}</span><span class="c-d">{esc(INDUSTRY_CONSTRUCTION["answer"][0][:90])}…</span></a>'
    planned = "".join(f'<div class="card soon"><span class="c-k">Industry</span><span class="c-t">{esc(t)}</span><span class="c-d">{esc(d)}</span><span class="soon-tag">準備中</span></div>' for s,t,d in INDUSTRY_PLANNED)
    body = f'''
<div class="wrap page">
  <div class="page-head">
    <p class="eyebrow"><span class="jp">業種別</span></p>
    <h1>業種別AI検索対策</h1>
    <p class="lead">お客様がAIに聞く質問は、業種によって異なります。地域で絞られる業種、専門性で選ばれる業種、条件で比較される業種。それぞれの顧客質問・検索行動・会社選定の基準にもとづいて、Webサイトに必要な情報を整理しています。テンプレート文章の使い回しではなく、業種ごとに独自の内容として書いています。</p>
  </div>
  <div class="cards three">{live}{planned}</div>
  {cta_band(depth)}
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"CollectionPage","@id":url+"#webpage","url":url,"name":"業種別AI検索対策｜AI Ready Web","description":"工務店・士業・不動産・製造業など、業種ごとの顧客質問と検索行動にもとづくAI検索対策の考え方。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("業種別AI検索対策",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "業種別AI検索対策｜AI Ready Web", "工務店・士業・不動産・製造業など、業種ごとの顧客質問と検索行動にもとづくAI検索対策の考え方と、Webサイトに必要な情報。", body, [("ホーム",""),("業種別AI検索対策",path)], ld)

# ---------------------------------------------------------------- サービス系
def plans_html(depth):
    R = rel(depth)
    out = []
    for p in PLANS:
        badge = '<span class="plan-badge">Recommended</span>' if p["rec"] else ""
        base = f'<p class="plan-meta">{esc(p["base"])}</p>' if p["base"] else ""
        lis = "".join(f"<li>{esc(x)}</li>" for x in p["incl"])
        out.append(f'''<article class="plan{" rec" if p["rec"] else ""}">
  <p class="plan-name">{p["name"]}{badge}</p>
  <p class="plan-price"><span class="num">{p["price"]}</span><span class="unit">円〜</span></p>
  <p class="plan-meta">{esc(p["scope"])}</p>
  <p style="font-size:.92rem">{esc(p["desc"])}</p>
  {base}
  <ul>{lis}</ul>
  <a class="btn {'btn-primary' if p['rec'] else 'btn-ghost'}" href="{R}contact/" data-topic="{p['topic']}">{p["name"]}について相談する</a>
</article>''')
    return '<div class="plans">' + "".join(out) + '</div>'

def service_page():
    path = "service/"; depth = 1; R = rel(depth)
    faqs = [
      ("AI Ready Webは何のサービスですか？", "AI検索・SEOを考慮したWebサイト制作サービスです。企業の事業内容・対象顧客・対応地域・強みなどの情報を整理し、人・検索エンジン・AIのいずれからも理解されやすいWebサイトを企画・設計・制作します。"),
      ("誰向けのサービスですか？", "AIやWebの専門知識を持たない、日本の中小企業を中心とした法人向けです。工務店・リフォーム、不動産、士業、中小製造業、BtoBサービスなど、問い合わせ1件の価値が比較的高い業種を中心にご支援しています。"),
      ("SEOとの違いは何ですか？", "SEOは検索結果で見つけてもらうための最適化です。AI Ready Webでは、SEOの基本設計を土台としたうえで、AIが質問に答えるときに企業情報を参照しやすい情報設計（AI検索設計）を加えます。"),
      ("AI検索での表示は保証されますか？", "特定のAIサービスでの掲載や表示順位を保証するサービスではありません。AIや検索エンジンが企業・サービスについて理解・参照しやすい情報環境を整え、継続的に改善していくことを目的としています。"),
      ("追加料金は発生しますか？", "ページ数、撮影、特殊機能、システム開発、EC機能、多言語対応、大規模なコンテンツ制作など、基本プランの範囲を超える場合は事前にお見積もりを提示します。"),
    ]
    body = f'''
<div class="wrap page">
  <article class="doc" style="max-width:none">
    <header class="doc-head" style="max-width:46rem">
      <p class="eyebrow"><span class="jp">サービス</span></p>
      <h1>AI Ready Web — AI検索・SEOを考慮したWebサイト制作サービス</h1>
      <div class="answer"><p class="answer-label">AI Ready Webとは</p>
        <p>AI Ready Webは、{esc(ENTITY["category"])}です。企業の事業内容・対象顧客・対応地域・強みなどの情報を整理し、人・検索エンジン・AIのいずれからも理解されやすいWebサイトを企画・設計・制作します。</p>
        <p>対象は、{esc(ENTITY["audience"])}。提供価値は、{esc(ENTITY["value"])}です。特定のAIサービスでの掲載や順位を保証するものではありません。</p>
      </div>
    </header>

    <section id="who" style="max-width:46rem"><h2>誰のためのサービスか</h2>
      <p>専門のWeb担当者が社内にいない、ホームページが古くなっている、Webからの問い合わせを増やしたい、AI時代への漠然とした危機感がある。そうした中小企業の経営者・事業責任者の方に向けたサービスです。</p>
      <ul class="bul"><li>工務店、リフォーム会社</li><li>不動産会社</li><li>税理士、社労士、行政書士などの士業</li><li>中小製造業</li><li>BtoBサービス企業</li><li>その他、問い合わせ1件あたりの価値が比較的高い地域企業・専門企業</li></ul>
      <p>業種ごとの考え方は<a href="{R}industry/">業種別AI検索対策</a>で解説しています。</p>
    </section>

    <section id="problem" style="max-width:46rem"><h2>どのような課題を解決するのか</h2>
      <p>優れた商品・サービスがあっても、Web上の情報が不足・分散・あいまいであれば、AIは会社やサービスを十分に理解できません。AI Ready Webは、会社の情報を「AIにも人にも理解しやすい状態」に整理し、Googleで探されるだけのホームページから、AIにも見つけてもらえるホームページへ移行することを支援します。</p>
    </section>

    <section id="principles" style="max-width:46rem"><h2>4つの設計思想</h2>
      <ol class="num">
        <li><strong>AIに理解される情報設計</strong> — 会社、サービス、対象顧客、対応地域、特徴、専門性を明確に整理し、企業の価値を「情報」として設計します。</li>
        <li><strong>AI上で想定される質問に答えるコンテンツ設計</strong> — 「○○に強い会社は？」「この条件で相談できる会社は？」といった質問を想定し、サービスページ、FAQ、事例、専門コンテンツを設計します。</li>
        <li><strong>SEO・クローラー・構造化などの技術設計</strong> — HTML構造、サイトマップ、構造化データ、robots.txtなどを整え、検索エンジンとAIがアクセス・解釈しやすい状態にします。特定の技術施策だけでAI検索への掲載を保証することはできません。</li>
        <li><strong>問い合わせにつながるUX/UI設計</strong> — 最終的に判断するのは人です。「AIには理解しやすく、人には選びやすく」を基本思想とします。</li>
      </ol>
    </section>

    <section id="pricing"><h2>料金プラン</h2>
      <p style="max-width:46rem">AIと標準化された制作プロセスで制作工程を効率化し、「つくること」にかかっていたコストを「見つけてもらうこと」と「育てること」へ配分する料金設計です。表示価格は目安で、要件により個別にお見積もりします。</p>
      {plans_html(depth)}
      <p class="note" style="margin-top:1rem">公開後の運用は<a href="{R}growth/">AI Search Growth（月額39,800円〜）</a>、初期費用0円の月額型プランは<a href="{R}contact/" data-topic="subscription">お問い合わせ</a>からご相談ください。料金の考え方の詳細は<a href="{R}#why">トップページ「なぜ、この価格でつくれるのか」</a>をご覧ください。</p>
    </section>

    <section id="process" style="max-width:46rem"><h2>制作の流れ</h2>
      <ol class="num">
        <li>ヒアリング（事業・顧客・強みを伺う）</li><li>AI検索・競合調査（現在の見え方を把握）</li><li>戦略・情報設計（伝える情報を整理）</li><li>コピー・コンテンツ設計（想定質問に答える内容）</li><li>UI/UXデザイン</li><li>開発</li><li>SEO・AI検索向け技術設定（構造化データ、クローラーへの配慮）</li><li>公開（公開前チェック）</li><li>継続モニタリング（AI検索上の状況を観測）</li>
      </ol>
    </section>

    <section id="faq" style="max-width:46rem"><h2>よくある質問</h2>{faq_html(faqs)}</section>
    <section id="related" style="max-width:46rem"><h2>関連するページ</h2>{related_cards(depth, ["what-is-aeo","ai-era-web-production-difference","how-to-choose-ai-search-web-company"], ["check","growth"])}</section>
  </article>
  {cta_band(depth)}
</div>'''
    url = SITE_URL + path
    ld = [
      {"@type":"WebPage","@id":url+"#webpage","url":url,"name":"AI Ready Web — サービス詳細","description":"AI検索・SEOを考慮したWebサイト制作サービス「AI Ready Web」の対象・解決する課題・4つの設計思想・料金プラン・制作の流れ。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"},"mainEntity":service_ref()},
      dict(breadcrumb_ld([("ホーム",""),("サービス",path)]), **{"@id":url+"#breadcrumb"}),
      {"@type":"Service","@id":SITE_URL+"#service","name":"AI Ready Web","serviceType":ENTITY["category"],"description":"企業の事業内容・対象顧客・対応地域・強みなどの情報を整理し、人・検索エンジン・AIのいずれからも理解されやすいWebサイトを企画・設計・制作するサービス。特定のAIサービスでの掲載や順位を保証するものではない。","url":url,"areaServed":"JP","provider":{"@id":SITE_URL+"#organization"},"audience":{"@type":"BusinessAudience","name":ENTITY["audience"]},
       "offers":[{"@type":"Offer","name":p["name"],"priceSpecification":{"@type":"PriceSpecification","minPrice":int(p["price"].replace(",","")),"priceCurrency":"JPY"},"description":p["scope"]+"。"+p["desc"]} for p in PLANS]},
      faq_ld(faqs),
    ]
    page(path, "AI Ready Web｜AI検索・SEOを考慮したWebサイト制作サービス", "AI Ready Webは、企業情報を整理し、人・検索エンジン・AIのいずれからも理解されやすいWebサイトを企画・設計・制作するサービスです。対象・課題・4つの設計思想・料金プラン・制作の流れを説明します。", body, [("ホーム",""),("サービス",path)], ld)

def form_html(depth, default_topic="check", path=""):
    R = rel(depth)
    opts = [("check","無料AI検索診断を申し込む"),("consult","料金・制作について相談する"),("plan-start","STARTプランについて相談する"),("plan-ready","AI READYプランについて相談する"),("plan-growth","GROWTHプランについて相談する"),("subscription","月額型プラン（Subscription）について相談する"),("growth","AI Search Growth（継続運用）について相談する")]
    o = "".join(f'<option value="{v}"{" selected" if v==default_topic else ""}>{t}</option>' for v,t in opts)
    title = "無料AI検索診断を申し込む" if default_topic=="check" else "料金・制作について相談する"
    btn = "無料診断を申し込む" if default_topic=="check" else "この内容で相談する"
    return f'''<div class="form-card" id="contact">
  <h3 id="form-title">{title}</h3>
  <form id="contact-form" method="post" action="">
    <div class="form-preview" id="form-preview" role="note">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v4.5M12 16h.01"/></svg>
      <p>現在はプレビュー表示です。フォームの送信先が未設定のため、送信は行われません。</p>
    </div>
    <div class="field"><label for="f-topic">ご相談内容 <span class="req">必須</span></label><select id="f-topic" name="topic" required>{o}</select></div>
    <div class="field"><label for="f-company">会社名 <span class="req">必須</span></label><input type="text" id="f-company" name="company" autocomplete="organization" required></div>
    <div class="field"><label for="f-url">ホームページのURL <span class="opt">任意</span></label><input type="url" id="f-url" name="url" inputmode="url" placeholder="https://" autocomplete="url"><p class="help">ホームページがない場合は空欄のままで構いません。</p></div>
    <div class="two">
      <div class="field"><label for="f-name">お名前 <span class="req">必須</span></label><input type="text" id="f-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="f-email">メールアドレス <span class="req">必須</span></label><input type="email" id="f-email" name="email" autocomplete="email" inputmode="email" required></div>
    </div>
    <div class="field"><label for="f-question">お客様がAIに聞きそうな質問 <span class="opt">任意</span></label><textarea id="f-question" name="question" placeholder="例：世田谷区でおすすめの工務店は？"></textarea><p class="help">思いつかない場合は空欄でも大丈夫です。業種や地域からこちらで設定します。</p><p class="help hearing-note" id="f-hearing-note" hidden>セルフ診断の回答内容を添えて送信します。</p><input type="hidden" id="f-hearing" name="hearing" value=""></div>
    <input type="hidden" name="_subject" value="【AI Ready Web】お問い合わせ・無料診断のお申し込み">
    <input type="hidden" name="page" value="{SITE_URL}{path}">
    <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="check"><input type="checkbox" id="f-privacy" name="privacy" required><label for="f-privacy"><a href="{R}privacy/" target="_blank" rel="noopener">プライバシーポリシー</a>に同意する <span class="req">必須</span></label></div>
    <div class="form-actions"><button class="btn btn-primary" type="submit" id="form-submit">{btn}</button><p class="form-status" id="form-status" tabindex="-1" hidden></p></div>
  </form>
</div>'''

def hearing_panel():
    return '''<div class="hearing" id="hearing" role="region" aria-labelledby="hearing-title">
  <div class="hearing-head">
    <div class="hearing-title"><i aria-hidden="true"></i><span id="hearing-title">セルフ診断（約3分）</span></div>
    <div class="hearing-progress" id="hearing-progress"></div>
  </div>
  <div class="hearing-body" id="hearing-body">
    <div class="h-intro" id="h-intro">
      <p class="h-lead">いくつかの質問に答えていただくと、御社について<b>お客様がAIに聞きそうな質問</b>と、<b>今のホームページの整理状況</b>をその場で確認できます。</p>
      <ul class="h-ex" aria-label="質問の例"><li>世田谷区でおすすめの工務店は？</li><li>自然素材の家に強い工務店を教えて</li><li>中小企業に強い税理士は？</li></ul>
      <button class="btn btn-primary" type="button" id="h-start">セルフ診断を始める</button>
      <p class="note">入力内容は、最後に「申し込む」を押すまで送信されません。</p>
    </div>
    <ol class="h-log" id="h-log" aria-label="これまでの質問と回答"></ol>
    <div class="h-current" id="h-current" aria-live="polite" hidden></div>
    <div class="h-result" id="h-result" aria-live="polite" hidden></div>
  </div>
  <div class="hearing-foot" id="hearing-foot" hidden>
    <button type="button" id="h-back">← ひとつ戻る</button>
    <button type="button" id="h-restart">最初からやり直す</button>
  </div>
</div>'''

def check_page():
    path = "ai-search-check/"; depth = 1; R = rel(depth)
    faqs = [
      ("無料AI検索診断では何が分かりますか？", "見込み客がAIに聞きそうな質問を設定し、その回答に御社が登場するか、競合はどう見えているか、御社サイトが引用されているか、企業情報の整理状況、技術面・コンテンツ面の改善ポイントをレポートにまとめます。"),
      ("本当に無料ですか？制作を依頼する必要はありますか？", "診断は無料です。診断後に制作をご依頼いただく必要はありません。"),
      ("結果はどのくらい正確ですか？", "AIの回答は質問のしかたや時期によって変わるため、診断結果は調査時点での傾向を示すものです。特定のAIサービスでの表示を保証するものではありません。"),
      ("ホームページがなくても診断できますか？", "できます。ホームページがない場合は、業種・地域・強みから想定質問を設定し、AI上での現在の見え方と、必要な情報の設計をご提案します。"),
    ]
    body = f'''
<div class="wrap page">
  <div class="page-head">
    <p class="eyebrow"><span class="jp">無料AI検索診断</span></p>
    <h1>あなたの会社は、AIからどう見えている？— 無料AI検索診断</h1>
    <div class="answer" style="max-width:46rem"><p class="answer-label">無料AI検索診断とは</p>
      <p>無料AI検索診断は、見込み客がAIに聞きそうな質問を設定し、ChatGPTなどのAI上で御社と競合がどのように登場するか、御社サイトが引用されているか、企業情報がAIに理解しやすい状態かを調査し、「現在どう見えているか」「なぜそうなっているか」「何を改善すべきか」をレポートにまとめる無料のサービスです。</p>
      <p>まずはこのページのセルフ診断で、想定質問と今のホームページの整理状況をその場で確認できます。その内容をもとに、レポートをお申し込みいただけます。</p>
    </div>
  </div>
  <div class="check-grid">
    <div>
      {hearing_panel()}
      <p class="note" style="margin-top:.8rem">セルフ診断はご入力内容にもとづく簡易チェックです。AI上での実際の表示状況はレポートで確認します。</p>
    </div>
    {form_html(depth, "check", path)}
  </div>

  <article class="doc" style="margin-top:clamp(3rem,6vw,4.5rem)">
    <section id="method"><h2>診断の方法</h2>
      <ol class="num">
        <li><strong>想定質問の設定</strong> — 業種・地域・強みから、見込み客がAIに聞きそうな質問を複数設定します（例：「世田谷区でおすすめの工務店は？」「中小企業に強い税理士は？」）。</li>
        <li><strong>AI上での確認</strong> — 設定した質問をAIに投げ、御社・競合の登場状況、回答内で引用されたページを記録します。回答は変動するため、複数回・複数の言い回しで傾向を見ます。</li>
        <li><strong>企業情報の整理状況の確認</strong> — 御社サイトの、サービス別ページ・対応地域・事例・FAQ・会社概要・更新状況・技術設定（robots.txt、サイトマップ、構造化データ）を確認します。</li>
        <li><strong>レポート</strong> — 「現在どう見えているか」「なぜそうなっているか」「何を改善すべきか」を整理し、改修かリニューアルか、何から始めるべきかをご提案します。</li>
      </ol>
    </section>
    <section id="report"><h2>レポートで分かること</h2>
      <ul class="bul"><li>対象質問における御社の登場状況</li><li>競合企業の登場状況</li><li>御社サイトの引用状況</li><li>企業情報の整理状況</li><li>技術的な改善ポイント</li><li>コンテンツの改善ポイント</li></ul>
      <div class="callout warn"><b>注意</b>：診断結果は調査時点での傾向であり、特定のAIサービスでの掲載や順位を保証するものではありません。</div>
    </section>
    <section id="faq"><h2>よくある質問</h2>{faq_html(faqs)}</section>
    <section id="related"><h2>関連するページ</h2>{related_cards(depth, ["how-to-appear-in-chatgpt","ai-search-friendly-website"], ["service","growth"])}</section>
  </article>
</div>'''
    url = SITE_URL + path
    ld = [
      {"@type":"WebPage","@id":url+"#webpage","url":url,"name":"無料AI検索診断｜AI Ready Web","description":"見込み客がAIに聞きそうな質問を設定し、御社と競合の登場状況・引用状況・企業情報の整理状況を調べる無料の診断。サイト上のセルフ診断で想定質問と現状をその場で確認できます。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
      dict(breadcrumb_ld([("ホーム",""),("無料AI検索診断",path)]), **{"@id":url+"#breadcrumb"}),
      {"@type":"Service","@id":url+"#service","name":"無料AI検索診断","serviceType":"AI検索状況の診断（無料）","description":"見込み客がAIに聞きそうな質問を設定し、自社と競合の登場状況、自社サイトの引用状況、企業情報の整理状況などを診断し、改善ポイントをレポートする。","provider":{"@id":SITE_URL+"#organization"},"areaServed":"JP","offers":{"@type":"Offer","price":0,"priceCurrency":"JPY"},"isRelatedTo":service_ref()},
      faq_ld(faqs),
    ]
    page(path, "無料AI検索診断｜あなたの会社は、AIからどう見えている？— AI Ready Web", "見込み客がAIに聞きそうな質問を設定し、御社と競合の登場状況・引用状況・企業情報の整理状況を調べる無料の診断。サイト上のセルフ診断で、想定質問と今のホームページの整理状況をその場で確認できます。", body, [("ホーム",""),("無料AI検索診断",path)], ld,
         extra_head=f'<link rel="stylesheet" href="{R}assets/hearing.css">', extra_scripts=f'<script src="{R}assets/hearing.js"></script>')

def growth_page():
    path = "growth/"; depth = 1; R = rel(depth)
    faqs = [
      ("AI Search Growthは何をするサービスですか？", "公開後のWebサイトについて、設定したAI検索質問での登場状況、競合の登場状況、自社サイトの引用状況、SEO・アクセス状況、AI経由の流入を定期的に確認し、改善テーマの抽出とFAQ・コンテンツの改善、月次レポートを行う継続運用サービスです。"),
      ("AI Ready Webで制作していないサイトでも利用できますか？", "現状分析のうえでご相談いただけます。技術設定や情報構造に大きな課題がある場合は、先に改修をご提案することがあります。"),
      ("料金はいくらですか？", "月額39,800円〜です。モニタリングの対象数、改善作業量、対応範囲はプランにより設定します。詳細はご相談時にご案内します。"),
    ]
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head">
      <p class="eyebrow"><span class="jp">継続運用</span></p>
      <h1>AI Search Growth — Webサイトは、公開してから育てる。</h1>
      <div class="answer"><p class="answer-label">AI Search Growthとは</p>
        <p>AI Search Growthは、公開後のWebサイトについて「AIからどう見えているか」「競合はどう見えているか」「何を改善すべきか」を継続的に確認しながら、コンテンツとWebサイトを育てていく月額の運用サービスです（月額39,800円〜）。</p>
        <p>検索環境とAIの回答は変化し続けるため、一度制作して終わりにせず、観測と改善を繰り返すことを目的としています。特定のAIサービスでの表示を保証するものではありません。</p>
      </div>
    </header>
    <section id="why"><h2>なぜ公開後の運用が必要なのか</h2>
      <p>AIの回答は、質問のしかた、時期、参照する情報源の変化によって日々変わります。競合が情報を整えれば相対的な見え方も変わります。公開時点で整っていた情報も、更新が止まれば鮮度が下がります。そのため、AI検索対策は「公開して終わり」ではなく、観測と改善を続ける運用が前提になります。</p>
    </section>
    <section id="contents"><h2>サービス内容</h2>
      <ul class="checklist">
        <li><b>AI検索状況の定期チェック</b><span>設定した質問でAIに自社が登場するかを定期的に確認します。</span></li>
        <li><b>設定したAI検索質問のモニタリング</b><span>質問ごとの登場状況の推移を記録します。</span></li>
        <li><b>競合企業の登場状況確認</b><span>同じ質問で挙がる競合と、その根拠になっている情報を確認します。</span></li>
        <li><b>自社サイトの引用状況確認</b><span>回答内で引用されたページと、その内容を確認します。</span></li>
        <li><b>SEO / アクセス状況確認</b><span>検索エンジンからの流入、順位、技術的な問題を確認します。</span></li>
        <li><b>AI経由流入の確認</b><span>AIサービスからの参照流入を計測環境で確認します。</span></li>
        <li><b>改善テーマの抽出</b><span>不足している情報、答えられていない質問を整理します。</span></li>
        <li><b>FAQ / コンテンツ改善</b><span>抽出したテーマにもとづき、FAQや事例、サービスページを追加・更新します。</span></li>
        <li><b>月次レポート</b><span>観測結果と実施した改善、翌月の方針をまとめます。</span></li>
      </ul>
      <p class="note">※ モニタリングの対象、改善作業量、対応範囲は契約プランにより設定します。</p>
    </section>
    <section id="price"><h2>料金</h2>
      <p class="plan-price"><span class="num">39,800</span><span class="unit">円〜 / 月額</span></p>
      <p>観測する質問数や改善の範囲により個別にお見積もりします。初期費用0円で制作から運用までをまとめて提供する<strong>AI Ready Web Subscription（月額49,800円〜）</strong>もご相談いただけます。契約条件の詳細はご相談時にご案内します。</p>
    </section>
    <section id="faq"><h2>よくある質問</h2>{faq_html(faqs)}</section>
    <section id="related"><h2>関連するページ</h2>{related_cards(depth, ["how-to-get-cited-by-ai","aeo-vs-seo"], ["service","check","research"])}</section>
  </article>
  {cta_band(depth, "現状の見え方から、運用の方針を決めましょう。", "無料AI検索診断で現在の登場状況と改善ポイントを確認したうえで、AI Search Growthの観測対象と改善範囲をご提案します。")}
</div>'''
    url = SITE_URL + path
    ld = [
      {"@type":"WebPage","@id":url+"#webpage","url":url,"name":"AI Search Growth（継続運用）｜AI Ready Web","description":"公開後のWebサイトのAI検索状況・競合・引用状況を継続的に観測し、コンテンツを改善する月額運用サービス。月額39,800円〜。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
      dict(breadcrumb_ld([("ホーム",""),("AI Search Growth",path)]), **{"@id":url+"#breadcrumb"}),
      {"@type":"Service","@id":url+"#service","name":"AI Search Growth","serviceType":"Webサイトの継続運用（AI検索モニタリング・改善）","description":"公開後のAI検索状況、競合状況、引用状況を観測し、FAQ・コンテンツの改善と月次レポートを行う継続運用サービス。","provider":{"@id":SITE_URL+"#organization"},"areaServed":"JP","offers":{"@type":"Offer","priceSpecification":{"@type":"UnitPriceSpecification","minPrice":39800,"priceCurrency":"JPY","unitText":"月額"}},"isRelatedTo":service_ref()},
      faq_ld(faqs),
    ]
    page(path, "AI Search Growth（継続運用）｜Webサイトは、公開してから育てる。— AI Ready Web", "公開後のWebサイトについて、AI検索上の登場状況・競合・引用状況を継続的に観測し、FAQやコンテンツを改善する月額運用サービス。月額39,800円〜。", body, [("ホーム",""),("AI Search Growth",path)], ld)

# ---------------------------------------------------------------- Research
REPORT_FIELDS = [("調査日","YYYY-MM-DD"),("対象AI","例：ChatGPT（検索機能あり）、Perplexity、Gemini"),("対象質問","例：「AI検索対応のWeb制作会社は？」ほか"),("質問数","例：20問 × 各3回"),("自社の言及回数","例：20問のうち○問で言及"),("自社サイトの引用状況","例：引用○回（引用されたページ：/knowledge/what-is-aeo/ など）"),("確認できた傾向","例：定義を冒頭に置いたページが引用されやすい"),("実施した改善","例：FAQPage構造化データの追加、対応領域の明記"),("翌月の変化","次回レポートで記載")]

def report_cards():
    """aivis の report コマンドが書き出す src/reports.json を一覧カードにする"""
    rj = os.path.join(SRC, "reports.json")
    if not os.path.exists(rj): return ""
    reps = json.load(open(rj, encoding="utf-8"))
    return "".join(f'<a class="card" href="{esc(r["path"].replace("research/",""))}"><span class="c-k">Report</span><span class="c-t">{esc(r["title"])}</span><span class="c-d">{esc(r["summary"])}</span></a>' for r in reps)

def research_index():
    path = "research/"; depth = 1; R = rel(depth)
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head">
      <p class="eyebrow"><span class="jp">Research</span></p>
      <h1>Research — AI Ready Web自身のAI検索状況を観測する</h1>
      <div class="answer"><p class="answer-label">この領域について</p>
        <p>Researchは、AI Ready Web自身がChatGPTなどのAI上でどのように言及・引用されているかを、毎月同じ方法で観測し、結果と実施した改善を公開する領域です。AI検索対応を販売するサービスとして、自社サイトを実証例にするための一次情報を蓄積します。</p>
        <p>観測結果は、特定のAIサービスでの表示を保証するものではなく、調査時点での傾向を示すものです。</p>
      </div>
    </header>
    <section id="method"><h2>観測の方法</h2>
      <ol class="num">
        <li><strong>対象質問を固定する</strong> — 「AEOとは？」「AI検索対応のWeb制作会社は？」「ChatGPTに自社を表示させるには？」など、ナレッジで答えている質問を中心に設定し、月をまたいで同じ質問を使います。</li>
        <li><strong>対象AIを明記する</strong> — ChatGPT（検索機能の有無）、Perplexity、Geminiなど、観測に使ったサービスと条件を記録します。</li>
        <li><strong>複数回実施する</strong> — 回答は変動するため、同じ質問を複数回・複数の言い回しで投げ、言及・引用の回数を数えます。</li>
        <li><strong>改善と変化を対にして記録する</strong> — その月に実施した改善（ページ追加、構造化データ、表記の統一など）と、翌月の変化を並べて記録します。</li>
      </ol>
    </section>
    <section id="reports"><h2>月次レポート</h2>
      <p>レポートは <code>/research/ai-visibility-report-YYYY-MM/</code> の形式で追加します。各レポートには、調査日、対象AI、対象質問、質問数、自社の言及回数、自社サイトの引用状況、確認できた傾向、実施した改善、翌月の変化を記載します。</p>
      <div class="cards">
        {report_cards()}
        <a class="card" href="ai-visibility-report-2026-09/"><span class="c-k">Report template</span><span class="c-t">AI Visibility Report 2026-09（テンプレート）</span><span class="c-d">初回レポートの記入用テンプレートです。調査を実施し、数値を記入してから公開します。公開までは noindex に設定しています。</span><span class="soon-tag">未実施</span></a>
      </div>
    </section>
    <section id="related"><h2>関連するページ</h2>{related_cards(depth, ["how-to-get-cited-by-ai","what-is-geo"], ["growth","check"])}</section>
  </article>
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"CollectionPage","@id":url+"#webpage","url":url,"name":"Research — AI Ready WebのAI検索観測記録","description":"AI Ready Web自身がAI上でどのように言及・引用されているかを毎月観測し、結果と改善を公開する領域。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("Research",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "Research — AI Ready WebのAI検索観測記録", "AI Ready Web自身がChatGPTなどのAI上でどのように言及・引用されているかを、毎月同じ方法で観測し、結果と実施した改善を公開する領域。観測方法と月次レポートの一覧。", body, [("ホーム",""),("Research",path)], ld)

def research_report_template():
    path = "research/ai-visibility-report-2026-09/"; depth = 2
    rows = "".join(f'<div><dt>{esc(k)}</dt><dd><span class="todo">記入待ち</span> <span class="note">{esc(v)}</span></dd></div>' for k,v in REPORT_FIELDS)
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head">
      <p class="eyebrow"><span class="jp">Research / 月次レポート</span></p>
      <h1>AI Visibility Report 2026-09 <span class="todo">テンプレート・未実施</span></h1>
      <div class="callout warn"><b>公開前の注意</b>：このページは記入用テンプレートです。調査を実施し、すべての項目を実際の結果で埋めてから、<code>noindex</code> を外し、sitemap.xml に追加して公開してください。存在しない数値や評価は記載しないでください。</div>
    </header>
    <section id="summary"><h2>調査概要</h2><dl class="report-meta">{rows}</dl></section>
    <section id="questions"><h2>対象質問と結果</h2>
      <div class="table-wrap"><table class="cmp"><thead><tr><th scope="col">質問</th><th scope="col">実施回数</th><th scope="col">自社の言及</th><th scope="col">自社サイトの引用</th><th scope="col">主に登場した他社・情報源</th></tr></thead>
      <tbody><tr><td>AEOとは？</td><td>—</td><td>—</td><td>—</td><td>—</td></tr><tr><td>AI検索対応のWeb制作会社は？</td><td>—</td><td>—</td><td>—</td><td>—</td></tr><tr><td>ChatGPTに自社を表示させるには？</td><td>—</td><td>—</td><td>—</td><td>—</td></tr></tbody></table></div>
    </section>
    <section id="findings"><h2>確認できた傾向</h2><p><span class="todo">記入待ち</span> 引用されたページの特徴、言及されなかった質問の共通点、競合の情報の傾向などを記載します。</p></section>
    <section id="actions"><h2>実施した改善</h2><p><span class="todo">記入待ち</span> ページの追加・修正、構造化データ、robots.txt、表記の統一など、その月に行った改善を記載します。</p></section>
    <section id="next"><h2>翌月の変化（次回レポートで記載）</h2><p><span class="todo">記入待ち</span></p></section>
  </article>
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"WebPage","@id":url+"#webpage","url":url,"name":"AI Visibility Report 2026-09（テンプレート）","description":"AI Ready WebのAI検索状況の月次レポート（記入用テンプレート）","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("Research","research/"),("AI Visibility Report 2026-09",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "AI Visibility Report 2026-09（テンプレート・未実施）— AI Ready Web Research", "AI Ready WebのAI検索状況を観測する月次レポートの記入用テンプレート。調査実施後に公開します。", body, [("ホーム",""),("Research","research/"),("AI Visibility Report 2026-09",path)], ld, noindex=True, current="research/")

# ---------------------------------------------------------------- 会社・お問い合わせ
def about_page():
    path = "about/"; depth = 1; R = rel(depth)
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head"><p class="eyebrow"><span class="jp">運営会社</span></p><h1>運営会社</h1>
      <div class="answer"><p class="answer-label">AI Ready Webの運営</p><p>AI Ready Webは、{esc(COMPANY["name"])}が企画・運営する、{esc(ENTITY["category"])}です。{esc(ENTITY["value"])}を目的に、Web制作・SEO・AI検索設計を組み合わせたサービスを提供しています。</p></div>
    </header>
    <section><h2>会社概要</h2>
      <dl class="report-meta" style="grid-template-columns:1fr">
        <div><dt>会社名</dt><dd>{esc(COMPANY["name"])}</dd></div>
        <div><dt>事業内容</dt><dd>AI検索・SEOを考慮したWebサイト制作サービス「AI Ready Web」の企画・制作・運用</dd></div>
        <div><dt>連絡先</dt><dd><a href="mailto:{COMPANY["email"]}">{COMPANY["email"]}</a>／<a href="{R}contact/">お問い合わせフォーム</a></dd></div>
      </dl>
    </section>
    <section><h2>AI Ready Webについて</h2><p>{esc(ENTITY["tagline"])}AEO（AI検索最適化）を「{esc(ENTITY["aeo"])}」と定義し、特定のAIサービスでの掲載や順位を保証するものではないことを、すべてのページで明記しています。</p>
      <p>当サイト自身がAI検索最適化の実例となるよう設計し、AI上での見え方を<a href="{R}research/">Research</a>で継続的に公開しています。</p></section>
    <section><h2>関連するページ</h2>{related_cards(depth, ["what-is-aeo"], ["service","check","growth"])}</section>
  </article>
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"AboutPage","@id":url+"#webpage","url":url,"name":"運営会社｜AI Ready Web","description":COMPANY["name"]+"が運営するAI Ready Webの会社情報。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"about":{"@id":SITE_URL+"#organization"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("運営会社",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "運営会社｜AI Ready Web", COMPANY["name"]+"が運営する、AI検索・SEOを考慮したWebサイト制作サービス「AI Ready Web」の会社情報と連絡先。", body, [("ホーム",""),("運営会社",path)], ld)

def privacy_page():
    path = "privacy/"; depth = 1; R = rel(depth)
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head"><p class="eyebrow"><span class="jp">プライバシーポリシー</span></p><h1>プライバシーポリシー</h1>
      <p style="margin-top:1rem">{esc(COMPANY["name"])}（以下「当社」）は、当社が運営するWebサイト「AI Ready Web」（{SITE_URL}、以下「本サイト」）において取得する個人情報を、以下の方針にもとづき取り扱います。</p>
      <div class="doc-meta"><span>制定日 <b>{PRIVACY_DATE}</b></span><span>事業者 <b>{esc(COMPANY["name"])}</b></span></div>
    </header>
    <section id="p1"><h2>1. 取得する情報</h2>
      <p>当社は、本サイトを通じて次の情報を取得します。</p>
      <ul class="bul">
        <li><strong>お問い合わせ・無料診断のお申し込み時にご入力いただく情報</strong>：会社名、お名前、メールアドレス、ホームページのURL、ご相談内容、お客様がAIに聞きそうな質問、セルフ診断でご回答いただいた内容（業種、対応地域、サービス・強み、主なお客様、ホームページの状況）</li>
        <li><strong>アクセスに関する情報</strong>：本サイトの閲覧履歴、Cookie、IPアドレス、ブラウザの種類など、アクセス解析ツールを利用する場合に自動的に取得される情報</li>
      </ul>
    </section>
    <section id="p2"><h2>2. 利用目的</h2>
      <ul class="bul">
        <li>無料AI検索診断の実施と、結果のご報告</li>
        <li>お問い合わせへの回答、お見積もり、ご相談への対応</li>
        <li>当社サービスに関するご案内（ご希望されない場合は、ご連絡いただければ停止します）</li>
        <li>本サイトおよびサービスの改善、利用状況の分析（個人を特定しない形で行います）</li>
      </ul>
    </section>
    <section id="p3"><h2>3. 無料AI検索診断における外部AIサービスの利用</h2>
      <p>無料AI検索診断では、ご入力いただいた会社名、ホームページのURL、およびお客様がAIに聞きそうな質問を、調査のためにChatGPT（OpenAI）、Perplexity、Gemini（Google）などの外部AIサービスに送信し、その回答を確認します。お名前やメールアドレスなど、個人を特定する情報は送信しません。送信した情報は、各サービスの利用規約およびプライバシーポリシーにもとづいて取り扱われます。</p>
    </section>
    <section id="p4"><h2>4. 第三者への提供・業務の委託</h2>
      <p>当社は、法令にもとづく場合を除き、ご本人の同意なく個人情報を第三者に提供しません。ただし、利用目的の達成に必要な範囲で、次の業務を外部の事業者に委託することがあります。</p>
      <ul class="bul">
        <li>お問い合わせフォームの送信・メール転送（フォーム送信サービス）</li>
        <li>メールの送受信、データの保管（クラウドサービス）</li>
        <li>アクセス解析（アクセス解析ツールの提供事業者）</li>
      </ul>
      <p>委託先には、個人情報の適切な取り扱いを求めます。</p>
    </section>
    <section id="p5"><h2>5. Cookie・アクセス解析</h2>
      <p>本サイトでは、利用状況の把握と改善のためにCookieやアクセス解析ツールを利用することがあります。これらにより取得される情報には、個人を特定する情報は含まれません。Cookieの利用はブラウザの設定で無効にできますが、その場合、本サイトの一部の機能が利用できないことがあります。</p>
    </section>
    <section id="p6"><h2>6. 安全管理</h2>
      <p>当社は、取得した個人情報の漏えい、滅失、毀損を防止するため、アクセス権限の管理、通信の暗号化（HTTPS）など、合理的な安全管理措置を講じます。</p>
    </section>
    <section id="p7"><h2>7. 開示・訂正・利用停止・削除のご請求</h2>
      <p>ご本人から、保有する個人情報の開示、訂正、利用停止、削除のご請求があった場合は、ご本人であることを確認のうえ、法令にしたがい速やかに対応します。ご請求は下記の窓口までお願いします。</p>
    </section>
    <section id="p8"><h2>8. 本ポリシーの変更</h2>
      <p>当社は、法令の改正やサービス内容の変更に応じて、本ポリシーを改定することがあります。改定後の内容は本サイトに掲載した時点から適用します。</p>
    </section>
    <section id="p9"><h2>9. お問い合わせ窓口</h2>
      <dl class="report-meta">
        <div><dt>事業者</dt><dd>{esc(COMPANY["name"])}</dd></div>
        <div><dt>連絡先</dt><dd><a href="mailto:{COMPANY["email"]}">{COMPANY["email"]}</a></dd></div>
      </dl>
    </section>
  </article>
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"WebPage","@id":url+"#webpage","url":url,"name":"プライバシーポリシー｜AI Ready Web","description":COMPANY["name"]+"が運営するAI Ready Webの個人情報の取り扱いについて。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("プライバシーポリシー",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "プライバシーポリシー｜AI Ready Web", COMPANY["name"]+"が運営するAI Ready Webにおける個人情報の取得・利用目的・第三者提供・外部AIサービスの利用・お問い合わせ窓口について。", body, [("ホーム",""),("プライバシーポリシー",path)], ld)

def thanks_page():
    path = "contact/thanks/"; depth = 2; R = rel(depth)
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head"><p class="eyebrow"><span class="jp">送信完了</span></p><h1>お申し込み・お問い合わせを受け付けました</h1>
      <div class="answer"><p class="answer-label">ありがとうございます</p><p>内容を確認のうえ、ご入力いただいたメールアドレスへ担当者よりご連絡します。無料AI検索診断をお申し込みの場合は、想定質問の設定と調査を行ったうえで、結果をレポートとしてお送りします。</p></div>
    </header>
    <section><h2>お待ちいただく間に</h2>{related_cards(depth, ["what-is-aeo","ai-search-friendly-website"], ["service","growth"])}</section>
    <p style="margin-top:2rem"><a class="link" href="{R}">トップページへ戻る</a></p>
  </article>
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"WebPage","@id":url+"#webpage","url":url,"name":"送信完了｜AI Ready Web","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"}}]
    page(path, "送信完了｜AI Ready Web", "お問い合わせ・無料診断のお申し込みを受け付けました。", body, [("ホーム",""),("お問い合わせ","contact/"),("送信完了",path)], ld, noindex=True, current="contact/")

def contact_page():
    path = "contact/"; depth = 1; R = rel(depth)
    body = f'''
<div class="wrap page">
  <div class="page-head"><p class="eyebrow"><span class="jp">お問い合わせ</span></p><h1>お問い合わせ・無料診断のお申し込み</h1>
    <p class="lead">無料AI検索診断のお申し込み、料金・制作のご相談、月額型プランのご相談は、こちらのフォームからお送りください。特定のAIサービスでの表示や順位を保証するものではありません。診断後に制作をご依頼いただく必要はありません。</p></div>
  <div class="check-grid">
    <div>
      <h2 style="font-size:1.2rem;margin-bottom:.8rem">ご相談の種類</h2>
      <ul class="checklist">
        <li><b>無料AI検索診断</b><span>まだ制作を決めていない方へ。現在の見え方と改善ポイントをレポートします。<a href="{R}ai-search-check/">セルフ診断から始める</a>こともできます。</span></li>
        <li><b>料金・制作について</b><span>リニューアルを検討中の方へ。プラン選びやお見積もりのご相談。</span></li>
        <li><b>月額型プラン（Subscription）</b><span>初期費用0円・月額49,800円〜。契約条件はご相談時にご案内します。</span></li>
        <li><b>AI Search Growth（継続運用）</b><span>公開後の観測と改善。月額39,800円〜。</span></li>
      </ul>
    </div>
    {form_html(depth, "consult", path)}
  </div>
</div>'''
    url = SITE_URL + path
    ld = [{"@type":"ContactPage","@id":url+"#webpage","url":url,"name":"お問い合わせ｜AI Ready Web","description":"無料AI検索診断のお申し込み、料金・制作・月額型プランのご相談フォーム。","inLanguage":"ja","isPartOf":{"@id":SITE_URL+"#website"},"breadcrumb":{"@id":url+"#breadcrumb"}},
          dict(breadcrumb_ld([("ホーム",""),("お問い合わせ",path)]), **{"@id":url+"#breadcrumb"})]
    page(path, "お問い合わせ・無料診断のお申し込み｜AI Ready Web", "無料AI検索診断のお申し込み、料金・制作のご相談、月額型プラン・継続運用のご相談フォーム。", body, [("ホーム",""),("お問い合わせ",path)], ld)

# ---------------------------------------------------------------- トップページ・robots・sitemap・README
def not_found_page():
    body = f'''
<div class="wrap page">
  <article class="doc">
    <header class="doc-head"><p class="eyebrow"><span class="jp">404</span></p><h1>ページが見つかりません</h1>
      <p style="margin-top:1rem">URLが変更されたか、入力に誤りがある可能性があります。以下からお探しください。</p></header>
    <section>{related_cards(0, ["what-is-aeo","ai-search-friendly-website"], ["service","check","growth"])}</section>
    <p style="margin-top:2rem"><a class="link" href="/">トップページへ戻る</a></p>
  </article>
</div>'''
    depth = 0
    doc = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>ページが見つかりません｜AI Ready Web</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;700&family=Instrument+Sans:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/assets/base.css">
</head>
<body>
{header(depth)}
<main id="main">{body}</main>
{footer(depth)}
<script src="/assets/site.js"></script>
</body>
</html>
'''
    open(os.path.join(DIST, "404.html"), "w", encoding="utf-8").write(doc)

def top_page():
    src = open(TOP_SRC, encoding="utf-8").read()
    i = src.index("</style>") + len("</style>")
    head_part, body_part = src[:i], src[i:]
    head_part = head_part.replace("<title>AI Ready Web</title>", "<title>AI Ready Web｜あなたの会社、ChatGPTに聞いたら出てきますか？</title>", 1)
    if "[hidden]{display:none!important}" not in head_part:
        head_part = head_part.replace("*,*::before,*::after{box-sizing:border-box}", "*,*::before,*::after{box-sizing:border-box}\n[hidden]{display:none!important}", 1)
    out = ('<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + head_part.strip() + "\n</head>\n<body>\n" + body_part.strip() + "\n</body>\n</html>\n")
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(out)

def robots_and_sitemap(urls):
    robots = f"""# AI Ready Web — robots.txt
# 検索エンジンと、AI検索・回答型サービスのクローラーにクロールを許可します。
User-agent: *
Allow: /

# OpenAI（ChatGPTの検索機能が参照するクローラー）
User-agent: OAI-SearchBot
Allow: /

# OpenAI（ユーザーの操作に応じてページを取得）
User-agent: ChatGPT-User
Allow: /

# Perplexity
User-agent: PerplexityBot
Allow: /

# Anthropic（Claude）
User-agent: ClaudeBot
Allow: /

# Google（検索）/ Bing
User-agent: Googlebot
Allow: /
User-agent: Bingbot
Allow: /

# 学習用途のクローラー（GPTBot / Google-Extended など）を制限したい場合は、
# 以下のコメントを外して Disallow に設定してください。
# User-agent: GPTBot
# Disallow: /
# User-agent: Google-Extended
# Disallow: /

Sitemap: {SITE_URL}sitemap.xml
"""
    open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8").write(robots)
    today = PUBLISHED
    items = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    sm = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}</urlset>\n'
    open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8").write(sm)

def readme(urls):
    txt = f"""# AI Ready Web — 静的サイト 制作メモ

## 構成
- index.html                      トップページ（LP。CSS/JSは内包、セルフ診断のみ assets を参照）
- service/                        サービス詳細（Service 構造化データの主ページ）
- ai-search-check/                無料AI検索診断（セルフ診断 + 申込フォーム）
- growth/                         AI Search Growth（継続運用）
- knowledge/                      ナレッジ一覧 + 記事 {len(KNOWLEDGE)} 本（結論→定義→理由→具体例→注意点→関連）
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
3. フォーム送信先：Formspree（src/content.py の FORM_ENDPOINT）。送信は JavaScript から行い、成功したら /contact/thanks/ に移動します。
   届いた内容は Formspree の管理画面（https://formspree.io/forms）でも確認できます。無料プランは月50件まで。
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

## sitemap 収録URL（{len(urls)}）
""" + "\n".join("- " + u for u in urls) + "\n"
    open(os.path.join(DIST, "README.md"), "w", encoding="utf-8").write(txt)

def main():
    if os.path.exists(DIST):
        for n in os.listdir(DIST):
            p = os.path.join(DIST, n)
            if n == "assets":
                continue
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(os.path.join(DIST, "assets"), exist_ok=True)
    for f in ("base.css", "site.js", "hearing.css", "hearing.js"):
        shutil.copy(os.path.join(SRC, f), os.path.join(DIST, "assets", f))
    # GitHub Pages 用：カスタムドメインと Jekyll 無効化
    from urllib.parse import urlparse
    open(os.path.join(DIST, "CNAME"), "w").write(urlparse(SITE_URL).hostname + "\n")
    open(os.path.join(DIST, ".nojekyll"), "w").write("")

    urls = [SITE_URL, SITE_URL+"service/", SITE_URL+"ai-search-check/", SITE_URL+"growth/", SITE_URL+"knowledge/"]
    top_page()
    service_page(); check_page(); growth_page()
    knowledge_index()
    for a in KNOWLEDGE:
        urls.append(SITE_URL + article_page(a, "knowledge", "ナレッジ", "knowledge/"))
    industry_index(); urls.append(SITE_URL+"industry/")
    urls.append(SITE_URL + article_page(INDUSTRY_CONSTRUCTION, "industry", "業種別AI検索対策", "industry/"))
    research_index(); urls.append(SITE_URL+"research/")
    rj = os.path.join(SRC, "reports.json")
    if os.path.exists(rj):
        for r in json.load(open(rj, encoding="utf-8")): urls.append(SITE_URL + r["path"])
    research_report_template()
    about_page(); urls.append(SITE_URL+"about/")
    privacy_page(); urls.append(SITE_URL+"privacy/")
    contact_page(); urls.append(SITE_URL+"contact/")
    thanks_page()
    not_found_page()
    robots_and_sitemap(urls)
    readme(urls)
    print("built", len(urls), "indexable pages")

if __name__ == "__main__":
    main()
