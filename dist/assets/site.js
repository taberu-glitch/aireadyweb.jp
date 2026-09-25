/* AI Ready Web — 共通スクリプト（下層ページ） */
(function () {
  var CONFIG = window.AIRW_CONFIG || { FORM_ENDPOINT: "" };

  // 年号
  var y = document.getElementById("copy-year");
  if (y) y.textContent = String(new Date().getFullYear());

  // スマホメニュー
  var menuBtn = document.getElementById("menu-btn");
  var nav = document.getElementById("site-nav");
  if (menuBtn && nav) {
    function closeMenu() { nav.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); }
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", closeMenu); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("is-open")) { closeMenu(); menuBtn.focus(); } });
  }

  // 「〜について相談する」→ フォームのご相談内容に反映
  var topic = document.getElementById("f-topic");
  var formTitle = document.getElementById("form-title");
  var submitBtn = document.getElementById("form-submit");
  function syncTopic() {
    if (!topic) return;
    var isCheck = topic.value === "check";
    if (formTitle) formTitle.textContent = isCheck ? "無料AI検索診断を申し込む" : "料金・制作について相談する";
    if (submitBtn) submitBtn.textContent = isCheck ? "無料診断を申し込む" : "この内容で相談する";
  }
  document.querySelectorAll("a[data-topic]").forEach(function (a) {
    a.addEventListener("click", function () {
      var v = a.getAttribute("data-topic");
      if (topic && topic.querySelector('option[value="' + v + '"]')) { topic.value = v; syncTopic(); }
    });
  });
  if (topic) { topic.addEventListener("change", syncTopic); }

  // フォーム送信（送信先未設定のときはプレビュー扱い）
  var form = document.getElementById("contact-form");
  if (form) {
    var status = document.getElementById("form-status");
    var preview = document.getElementById("form-preview");
    var hasEndpoint = typeof CONFIG.FORM_ENDPOINT === "string" && CONFIG.FORM_ENDPOINT.trim() !== "";
    if (hasEndpoint) { form.action = CONFIG.FORM_ENDPOINT; if (preview) preview.hidden = true; }
    form.addEventListener("submit", function (e) {
      if (status) status.hidden = true;
      if (!form.checkValidity()) { e.preventDefault(); form.reportValidity(); return; }
      if (!hasEndpoint) {
        e.preventDefault();
        if (status) {
          status.textContent = "プレビュー表示のため、送信は行われていません。公開前に、フォームの送信先を設定してください。";
          status.hidden = false; status.focus();
        }
      }
    });
  }
})();
