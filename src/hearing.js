/* =====================================================================
   セルフ診断（ヒアリング）— 質問文・選択肢・想定質問のテンプレートはここで編集できます
   ===================================================================== */
(function () {
  var root = document.getElementById("hearing");
  if (!root) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var intro = document.getElementById("h-intro"), log = document.getElementById("h-log"), cur = document.getElementById("h-current"),
      res = document.getElementById("h-result"), foot = document.getElementById("hearing-foot"), prog = document.getElementById("hearing-progress"),
      body = document.getElementById("hearing-body");

  var SITE_ITEMS = [
    { k: "service", t: "サービスごとの説明ページがある", why: "サービスが1ページにまとまっていると、AIが「何ができる会社か」を判断しにくい可能性があります。" },
    { k: "area",    t: "対応地域を明記している",         why: "「○○（地域）で〜」という質問で、候補に挙がりにくい可能性があります。" },
    { k: "cases",   t: "事例・実績のページがある",       why: "実績が分からないと、AIが紹介する根拠が弱くなる可能性があります。" },
    { k: "faq",     t: "よくある質問（FAQ）がある",      why: "質問形式の情報がないと、AIの回答に使われにくい可能性があります。" },
    { k: "company", t: "会社概要（所在地・代表者など）がある", why: "基本情報が見つからないと、AIが会社として認識しにくい可能性があります。" },
    { k: "fresh",   t: "1年以内に情報を更新している",   why: "更新が止まっていると、情報の鮮度が低いと判断される可能性があります。" },
    { k: "mobile",  t: "スマートフォンで見やすい",       why: "人が読みにくいサイトは、候補に挙がっても問い合わせにつながりにくくなります。" },
    { k: "contact", t: "問い合わせフォームがある",       why: "候補に挙がっても、次の行動（問い合わせ）に進めません。" }
  ];

  var STEPS = [
    { id: "industry", type: "chips", q: "まず、御社の業種を教えてください。",
      options: ["工務店・リフォーム", "不動産", "士業（税理士・社労士・行政書士など）", "製造業", "BtoBサービス", "その他"], other: "その他", otherPlaceholder: "業種を入力（例：整体院、学習塾、印刷会社）" },
    { id: "area", type: "text", q: "主な対応地域を教えてください。", placeholder: "例：世田谷区、神奈川県、全国", hint: "お客様が探すときの言い方で。市区町村、都道府県、全国など。" },
    { id: "strength", type: "text", q: "主なサービスや強みを、ひとことで教えてください。", placeholder: "例：自然素材の注文住宅、相続に強い、短納期の試作加工" },
    { id: "customer", type: "chips", q: "主なお客様はどちらですか？", options: ["個人のお客様", "法人のお客様", "どちらも"] },
    { id: "site", type: "chips", q: "現在、会社のホームページはありますか？", options: ["ある", "ない・これからつくる"] },
    { id: "url", type: "url", q: "ホームページのURLを教えてください（任意）。", placeholder: "https://", skip: true, when: function (a) { return a.site === "ある"; } },
    { id: "state", type: "multi", q: "今のホームページに当てはまるものを、すべて選んでください。", options: SITE_ITEMS, none: "当てはまるものはない", when: function (a) { return a.site === "ある"; } },
    { id: "questions", type: "questions", q: "御社について、お客様がAIに聞きそうな質問を整理しました。追加や修正があれば、1行に1つずつ編集してください。" }
  ];

  var answers = {}, history = [];

  function esc(x) { return String(x).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function active() { return STEPS.filter(function (st) { return !st.when || st.when(answers); }); }
  function nextStep() { var a = active(); for (var i = 0; i < a.length; i++) { if (!(a[i].id in answers)) return a[i]; } return null; }
  function setProgress(done) {
    var a = active(); var n = a.filter(function (st) { return st.id in answers; }).length;
    var label = done ? "完了" : Math.min(n + 1, a.length) + " / " + a.length;
    prog.innerHTML = "<span>" + label + "</span><span class=\"hp-bar\"><i style=\"width:" + (done ? 100 : Math.round(n / a.length * 100)) + "%\"></i></span>";
  }
  function toBottom() { body.scrollTop = body.scrollHeight; }

  // 想定質問の生成
  function nouns() {
    var ind = answers.industry;
    if (ind === "工務店・リフォーム") return ["工務店", "リフォーム会社"];
    if (ind === "不動産") return ["不動産会社"];
    if (ind === "士業（税理士・社労士・行政書士など）") return ["事務所", "専門家"];
    if (ind === "製造業") return ["製造会社", "加工会社"];
    if (ind === "BtoBサービス") return ["会社"];
    return [answers.industryText ? answers.industryText : "会社"];
  }
  function genQuestions() {
    var n = nouns(), n1 = n[0], n2 = n[1] || n[0];
    var area = (answers.area || "").trim(), st = (answers.strength || "").trim();
    var nationwide = /全国|オンライン|日本全国/.test(area);
    var qs = [];
    qs.push(nationwide ? "おすすめの" + n1 + "を教えて" : area + "でおすすめの" + n1 + "は？");
    if (st) qs.push(st + "が得意な" + n2 + "を教えて");
    if (st) qs.push(nationwide ? st + "をオンラインで相談できる" + n1 + "は？" : area + "で" + st + "を相談できる" + n1 + "は？");
    qs.push(n1 + "を選ぶときに比較すべきポイントは？");
    return qs;
  }

  function start() {
    intro.hidden = true; foot.hidden = false; answers = {}; history = []; log.innerHTML = ""; res.hidden = true; res.innerHTML = ""; cur.hidden = false;
    render();
  }
  function render(prev) {
    var st = nextStep(); setProgress(!st);
    if (!st) { showResult(); return; }
    cur.hidden = false; cur.innerHTML = "";
    cur.appendChild(el("div", "hc-q", esc(st.q)));
    var ctl = el("div", "hc-ctl"); cur.appendChild(ctl);
    build(st, ctl, prev);
    toBottom();
    var f = ctl.querySelector("input,textarea,button"); if (f) f.focus({ preventScroll: true });
  }
  function commit(st, value, label, extra) {
    answers[st.id] = value; if (extra) for (var k in extra) answers[k] = extra[k];
    history.push(st.id);
    log.appendChild(el("li", "h-q", esc(st.q)));
    log.appendChild(el("li", "h-a", esc(label)));
    render();
  }
  function err(ctl, msg) { var e = ctl.querySelector(".hc-err"); if (!e) { e = el("p", "hc-err"); ctl.appendChild(e); } e.textContent = msg; }

  function build(st, ctl, prev) {
    if (st.type === "chips") {
      var wrap = el("div", "chips");
      st.options.forEach(function (o) {
        var b = el("button", "chip", esc(o)); b.type = "button";
        b.addEventListener("click", function () {
          if (st.other && o === st.other) { showOther(st, ctl, wrap); return; }
          commit(st, o, o, st.other ? { industryText: "" } : null);
        });
        wrap.appendChild(b);
      });
      ctl.appendChild(wrap);
      if (prev && st.other && prev === st.other) showOther(st, ctl, wrap);
    } else if (st.type === "text" || st.type === "url") {
      var row = el("div", "hc-row");
      var inp = el("input"); inp.type = st.type === "url" ? "url" : "text"; inp.placeholder = st.placeholder || ""; inp.setAttribute("aria-label", st.q);
      if (st.type === "url") inp.inputMode = "url";
      if (prev) inp.value = prev;
      var go = el("button", "hc-btn", "次へ"); go.type = "button";
      row.appendChild(inp); row.appendChild(go);
      if (st.skip) { var sk = el("button", "hc-btn ghost", "スキップ"); sk.type = "button"; sk.addEventListener("click", function () { commit(st, "", "（スキップ）"); }); row.appendChild(sk); }
      ctl.appendChild(row);
      if (st.hint) ctl.appendChild(el("p", "hc-hint", esc(st.hint)));
      function submit() {
        var v = inp.value.trim();
        if (!v) { if (st.skip) { commit(st, "", "（スキップ）"); return; } err(ctl, "入力してください。"); inp.focus(); return; }
        if (st.type === "url") { if (!/^https?:\/\//i.test(v)) v = "https://" + v; if (!/^https?:\/\/[^\s]+\.[^\s]+/i.test(v)) { err(ctl, "URLの形式を確認してください。"); return; } }
        commit(st, v, v);
      }
      go.addEventListener("click", submit);
      inp.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); submit(); } });
    } else if (st.type === "multi") {
      var sel = (prev || []).slice();
      var wrapM = el("div", "chips");
      st.options.forEach(function (o) {
        var b = el("button", "chip", esc(o.t)); b.type = "button"; b.setAttribute("aria-pressed", sel.indexOf(o.k) >= 0 ? "true" : "false");
        b.addEventListener("click", function () {
          var i = sel.indexOf(o.k); if (i >= 0) sel.splice(i, 1); else sel.push(o.k);
          b.setAttribute("aria-pressed", i >= 0 ? "false" : "true");
        });
        wrapM.appendChild(b);
      });
      ctl.appendChild(wrapM);
      var rowM = el("div", "hc-row");
      var goM = el("button", "hc-btn", "次へ"); goM.type = "button";
      goM.addEventListener("click", function () {
        var labels = st.options.filter(function (o) { return sel.indexOf(o.k) >= 0; }).map(function (o) { return o.t; });
        commit(st, sel.slice(), labels.length ? labels.length + "項目：" + labels.join("、") : "当てはまるものはない");
      });
      var noneB = el("button", "hc-btn ghost", esc(st.none)); noneB.type = "button";
      noneB.addEventListener("click", function () { commit(st, [], "当てはまるものはない"); });
      rowM.appendChild(goM); rowM.appendChild(noneB); ctl.appendChild(rowM);
      ctl.appendChild(el("p", "hc-hint", "複数選べます。分からない項目は選ばなくて大丈夫です。"));
    } else if (st.type === "questions") {
      var ta = el("textarea", "hc-ta"); ta.setAttribute("aria-label", st.q);
      ta.value = (prev && prev.length ? prev : genQuestions()).join("\n");
      ctl.appendChild(ta);
      var rowQ = el("div", "hc-row");
      var goQ = el("button", "hc-btn", "結果を見る"); goQ.type = "button";
      goQ.addEventListener("click", function () {
        var lines = ta.value.split(/\n/).map(function (l) { return l.trim(); }).filter(Boolean);
        if (!lines.length) { err(ctl, "質問を1つ以上入力してください。"); return; }
        commit(st, lines, lines.length + "件の質問を設定");
      });
      rowQ.appendChild(goQ); ctl.appendChild(rowQ);
      ctl.appendChild(el("p", "hc-hint", "業種・地域・強みから自動で整理しました。実際のお客様の言い方に近づけると、より役立つ診断になります。"));
    }
  }
  function showOther(st, ctl, wrap) {
    wrap.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", c.textContent === st.other ? "true" : "false"); });
    var old = ctl.querySelector(".hc-row"); if (old) old.remove();
    var row = el("div", "hc-row");
    var inp = el("input"); inp.type = "text"; inp.placeholder = st.otherPlaceholder || ""; inp.setAttribute("aria-label", "業種"); if (answers.industryText) inp.value = answers.industryText;
    var go = el("button", "hc-btn", "次へ"); go.type = "button";
    function submit() { var v = inp.value.trim(); if (!v) { err(ctl, "業種を入力してください。"); inp.focus(); return; } commit(st, st.other, v, { industryText: v }); }
    go.addEventListener("click", submit);
    inp.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); submit(); } });
    row.appendChild(inp); row.appendChild(go); ctl.appendChild(row); inp.focus({ preventScroll: true });
  }

  function summaryText() {
    var lines = [];
    lines.push("【セルフ診断の回答】");
    lines.push("業種：" + (answers.industry === "その他" ? answers.industryText : answers.industry));
    lines.push("対応地域：" + answers.area);
    lines.push("サービス・強み：" + answers.strength);
    lines.push("主なお客様：" + answers.customer);
    lines.push("ホームページ：" + answers.site + (answers.url ? "（" + answers.url + "）" : ""));
    if (answers.site === "ある") {
      var have = SITE_ITEMS.filter(function (o) { return (answers.state || []).indexOf(o.k) >= 0; }).map(function (o) { return o.t; });
      lines.push("当てはまる項目：" + (have.length ? have.join("、") : "なし"));
    }
    lines.push("想定質問：" + (answers.questions || []).join(" ／ "));
    return lines.join("\n");
  }

  function showResult() {
    cur.hidden = true; res.hidden = false; res.innerHTML = "";
    var hasSite = answers.site === "ある";
    var checked = hasSite ? (answers.state || []) : [];
    var score = checked.length, total = SITE_ITEMS.length;
    var level = !hasSite ? "土台づくりから" : score <= 2 ? "整理が必要" : score <= 5 ? "一部整理済み" : "よく整理されている";

    var head = el("div", "hr-head");
    head.appendChild(el("b", null, "簡易チェックの結果"));
    head.appendChild(el("span", "hr-level", esc(level)));
    res.appendChild(head);

    if (hasSite) {
      var meter = el("div", "hr-meter"); meter.setAttribute("role", "img"); meter.setAttribute("aria-label", "情報の整理状況：" + total + "項目のうち" + score + "項目に該当");
      for (var i = 0; i < total; i++) meter.appendChild(el("i", i < score ? "on" : ""));
      res.appendChild(meter);
      res.appendChild(el("p", "hr-p", "今のホームページは、AIに読み取られやすい情報の要素 " + total + " 項目のうち <b>" + score + " 項目</b> に当てはまります。"));
      res.appendChild(el("p", "hr-sub", "AIから見たときの改善ポイント"));
      var list = el("ul", "hr-list");
      SITE_ITEMS.forEach(function (o) {
        var ok = checked.indexOf(o.k) >= 0;
        var li = el("li", "hr-item");
        li.appendChild(el("span", ok ? "ok" : "ng", ok ? "✓" : "!"));
        var d = el("div"); d.appendChild(el("b", null, esc(o.t)));
        if (!ok) d.appendChild(el("span", null, esc(o.why.replace("○○（地域）", answers.area || "地域"))));
        li.appendChild(d); list.appendChild(li);
      });
      res.appendChild(list);
    } else {
      res.appendChild(el("p", "hr-p", "AIに見つけてもらうには、まず情報の土台となるWebサイトが必要です。「" + esc(answers.area) + "」「" + esc(answers.strength) + "」「" + esc(answers.customer) + "」といった情報を、AIにも人にも伝わる形で設計するところから始められます。"));
    }

    res.appendChild(el("p", "hr-sub", "お客様がAIに聞きそうな質問（診断で確認する想定質問）"));
    var qs = el("ul", "hr-qs");
    (answers.questions || []).forEach(function (q) { qs.appendChild(el("li", null, esc(q))); });
    res.appendChild(qs);

    res.appendChild(el("p", "hr-caveat", "この結果は、ご入力いただいた内容にもとづく簡易チェックです。ChatGPTなどのAI上で御社が実際にどう表示されているか、競合はどう見えているかは、無料AI検索診断のレポートで確認します。特定のAIサービスでの表示を保証するものではありません。"));

    var act = el("div", "hr-actions");
    var apply = el("button", "btn btn-primary", "この内容で無料AI検索診断を申し込む"); apply.type = "button";
    apply.addEventListener("click", prefill);
    act.appendChild(apply);
    // オンライン診断API（window.AIRW_CONFIG.CHECK_API を設定した場合のみ表示）
    var API = (window.AIRW_CONFIG || {}).CHECK_API;
    if (API) {
      var live = el("button", "btn btn-ghost", "AIに今すぐ聞いてみる（β・最大5問）"); live.type = "button";
      var liveOut = el("div", "hr-live"); liveOut.hidden = true;
      live.addEventListener("click", function () {
        var company = window.prompt("確認する会社名を入力してください（AIの回答にこの名前が出るかを調べます）", "");
        if (!company) return;
        live.disabled = true; live.textContent = "AIに質問しています…（30〜60秒）";
        fetch(API, { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ company: company, domain: (answers.url || "").replace(/^https?:\/\//, "").split("/")[0], questions: (answers.questions || []).slice(0, 5) }) })
        .then(function (r) { if (!r.ok) throw new Error(r.status === 429 ? "回数の上限に達しました。しばらくしてからお試しください。" : "確認に失敗しました（" + r.status + "）"); return r.json(); })
        .then(function (d) {
          liveOut.hidden = false; liveOut.innerHTML = "";
          liveOut.appendChild(el("p", "hr-sub", "AIの回答での登場状況（調査時点の傾向・保証ではありません）"));
          var ul = el("ul", "hr-list");
          d.items.forEach(function (it) {
            it.results.forEach(function (r) {
              var li = el("li", "hr-item");
              var ok = r.mention === 1;
              li.appendChild(el("span", ok ? "ok" : "ng", ok ? "✓" : "—"));
              var dd = el("div"); dd.appendChild(el("b", null, esc(it.question) + "（" + esc(r.ai) + "）"));
              dd.appendChild(el("span", null, r.error ? "エラー：" + esc(r.error) : (ok ? "回答に登場しました" + (r.rank ? "（" + r.rank + "番目）" : "") : "回答に登場しませんでした") + (r.competitors && r.competitors.length ? "／登場した他社：" + esc(r.competitors.join("、")) : "")));
              li.appendChild(dd); ul.appendChild(li);
            });
          });
          liveOut.appendChild(ul);
          liveOut.appendChild(el("p", "hr-caveat", esc(d.disclaimer)));
          live.textContent = "AIに今すぐ聞いてみる（β・最大5問）"; live.disabled = false; toBottom();
        })
        .catch(function (e) { liveOut.hidden = false; liveOut.innerHTML = ""; liveOut.appendChild(el("p", "hc-err", esc(e.message))); live.textContent = "AIに今すぐ聞いてみる（β・最大5問）"; live.disabled = false; });
      });
      act.appendChild(live); res.appendChild(act); res.appendChild(liveOut);
    } else {
      res.appendChild(act);
    }
    toBottom();
    apply.focus({ preventScroll: true });
  }

  function prefill() {
    var topic = document.getElementById("f-topic");
    if (topic) { topic.value = "check"; topic.dispatchEvent(new Event("change")); }
    var url = document.getElementById("f-url"); if (url && answers.url) url.value = answers.url;
    var q = document.getElementById("f-question"); if (q) q.value = (answers.questions || []).join("\n");
    var hid = document.getElementById("f-hearing"); if (hid) hid.value = summaryText();
    var note = document.getElementById("f-hearing-note"); if (note) note.hidden = false;
    var contact = document.getElementById("contact");
    if (contact) contact.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    setTimeout(function () { var c = document.getElementById("f-company"); if (c) c.focus({ preventScroll: true }); }, reduce ? 0 : 650);
  }

  function back() {
    if (!history.length) { restart(); return; }
    var id = history.pop(); var prev = answers[id]; delete answers[id];
    if (id === "industry") delete answers.industryText;
    // 戻った先より後の回答は無効化
    var order = STEPS.map(function (s) { return s.id; }); var idx = order.indexOf(id);
    order.slice(idx + 1).forEach(function (k) { if (k in answers) { delete answers[k]; var h = history.indexOf(k); if (h >= 0) history.splice(h, 1); } });
    if (log.lastElementChild) log.removeChild(log.lastElementChild);
    if (log.lastElementChild) log.removeChild(log.lastElementChild);
    res.hidden = true; res.innerHTML = "";
    render(prev);
  }
  function restart() { start(); }

  document.getElementById("h-start").addEventListener("click", start);
  document.getElementById("h-back").addEventListener("click", back);
  document.getElementById("h-restart").addEventListener("click", restart);

  // 「無料で診断する」系のCTA → セルフ診断へ移動し、未開始なら開始
  document.querySelectorAll('a[href="#check"]').forEach(function (a) {
    a.addEventListener("click", function () {
      setTimeout(function () { if (!intro.hidden) { start(); } else { root.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" }); } }, reduce ? 0 : 500);
    });
  });
})();
