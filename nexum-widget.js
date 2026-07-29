/**
 * Nexum AI Chat Widget
 * ─────────────────────────────────────────────────────
 * Paste ONE line into your website's <body> to embed:
 *
 *   <script src="https://YOUR-RENDER-URL/nexum-widget.js"></script>
 *
 * Or host this file yourself and update API_URL below.
 * ─────────────────────────────────────────────────────
 */

(function () {
  'use strict';

  /* ── CONFIG — change this to your Render deployment URL ── */
  var API_URL = 'https://YOUR-RENDER-URL/chat';

  /* ── Prevent double injection ── */
  if (document.getElementById('nexum-widget-root')) return;

  /* ════════════════════════════════════
     1. INJECT STYLES
     ════════════════════════════════════ */
  var style = document.createElement('style');
  style.textContent = [
    ':root{--nxc:#6c63ff;--nxc2:#a78bfa;--nxbg:#0d0f1a;--nxs:#13172b;--nxs2:#1a1f38;',
    '--nxborder:rgba(255,255,255,.07);--nxtext:#e8eaf6;--nxmuted:#8b8fad;',
    '--nxgreen:#4ade80;--nxgrad:linear-gradient(135deg,#6c63ff,#a78bfa);',
    '--nxshadow:0 8px 32px rgba(0,0,0,.45);}',

    /* Launcher button */
    '#nxc-launcher{position:fixed;bottom:24px;right:24px;z-index:99999;',
    'width:56px;height:56px;border-radius:50%;border:none;cursor:pointer;',
    'background:var(--nxgrad);color:#fff;font-size:24px;',
    'box-shadow:0 4px 20px rgba(108,99,255,.5);',
    'display:flex;align-items:center;justify-content:center;',
    'transition:transform .2s,box-shadow .2s;}',
    '#nxc-launcher:hover{transform:scale(1.08);box-shadow:0 6px 28px rgba(108,99,255,.65);}',

    /* Widget container */
    '#nxc-box{position:fixed;bottom:90px;right:24px;z-index:99998;',
    'width:370px;height:520px;border-radius:20px;overflow:hidden;',
    'background:var(--nxbg);border:1px solid var(--nxborder);',
    'box-shadow:var(--nxshadow);display:flex;flex-direction:column;',
    'font-family:"Inter",system-ui,sans-serif;',
    'transform:scale(.92) translateY(20px);opacity:0;pointer-events:none;',
    'transition:transform .25s cubic-bezier(.34,1.56,.64,1),opacity .2s;}',
    '#nxc-box.open{transform:scale(1) translateY(0);opacity:1;pointer-events:all;}',

    /* Mobile */
    '@media(max-width:480px){#nxc-box{width:calc(100vw - 20px);right:10px;bottom:80px;height:78vh;}}',

    /* Header */
    '#nxc-head{display:flex;align-items:center;gap:10px;padding:14px 16px;',
    'background:rgba(13,15,26,.95);border-bottom:1px solid var(--nxborder);}',
    '#nxc-head .nxc-logo{width:36px;height:36px;border-radius:10px;flex-shrink:0;',
    'background:var(--nxgrad);display:flex;align-items:center;justify-content:center;',
    'font-size:18px;box-shadow:0 0 14px rgba(108,99,255,.35);}',
    '#nxc-head .nxc-title{font-size:.9rem;font-weight:700;color:var(--nxtext);}',
    '#nxc-head .nxc-sub{font-size:.65rem;color:var(--nxmuted);margin-top:1px;}',
    '#nxc-head .nxc-dot{margin-left:auto;display:flex;align-items:center;gap:5px;',
    'font-size:.68rem;color:var(--nxgreen);}',
    '#nxc-head .nxc-dot span{width:6px;height:6px;border-radius:50%;',
    'background:var(--nxgreen);animation:nxblink 2s ease-in-out infinite;}',
    '@keyframes nxblink{0%,100%{opacity:1}50%{opacity:.35}}',
    '#nxc-close{background:none;border:none;color:var(--nxmuted);font-size:18px;',
    'cursor:pointer;padding:2px 6px;margin-left:8px;border-radius:6px;',
    'transition:color .15s,background .15s;}',
    '#nxc-close:hover{color:var(--nxtext);background:rgba(255,255,255,.06);}',

    /* Messages */
    '#nxc-msgs{flex:1;overflow-y:auto;padding:14px 12px;display:flex;',
    'flex-direction:column;gap:12px;}',
    '#nxc-msgs::-webkit-scrollbar{width:3px;}',
    '#nxc-msgs::-webkit-scrollbar-thumb{background:var(--nxs2);border-radius:10px;}',

    /* Bubbles */
    '.nxc-row{display:flex;gap:8px;align-items:flex-end;animation:nxup .25s ease;}',
    '.nxc-row.user{flex-direction:row-reverse;}',
    '@keyframes nxup{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}',
    '.nxc-av{width:28px;height:28px;border-radius:50%;flex-shrink:0;',
    'display:flex;align-items:center;justify-content:center;font-size:13px;}',
    '.nxc-av.bot{background:var(--nxs2);border:1px solid var(--nxborder);}',
    '.nxc-av.user{background:var(--nxgrad);}',
    '.nxc-bub{max-width:82%;padding:10px 13px;border-radius:16px;',
    'font-size:.82rem;line-height:1.6;word-break:break-word;}',
    '.nxc-bub.user{background:var(--nxgrad);color:#fff;border-bottom-right-radius:3px;}',
    '.nxc-bub.bot{background:var(--nxs2);border:1px solid var(--nxborder);',
    'color:var(--nxtext);border-bottom-left-radius:3px;}',

    /* Rendered HTML inside bot bubble */
    '.nxc-bub.bot p{margin:3px 0;}',
    '.nxc-bub.bot ul{list-style:none;margin:7px 0;padding:0;}',
    '.nxc-bub.bot ul li{position:relative;padding-left:16px;margin:5px 0;line-height:1.5;}',
    '.nxc-bub.bot ul li::before{content:"▸";position:absolute;left:0;',
    'color:var(--nxc2);font-size:.75em;top:2px;}',
    '.nxc-bub.bot ul ul{margin:3px 0 3px 8px;}',
    '.nxc-bub.bot ul ul li::before{content:"–";color:var(--nxc);}',
    '.nxc-bub.bot strong{color:var(--nxc2);font-weight:600;}',

    /* Typing indicator */
    '.nxc-typing{display:flex;align-items:center;gap:4px;padding:9px 12px;}',
    '.nxc-typing span{width:6px;height:6px;border-radius:50%;background:var(--nxc2);',
    'animation:nxbounce 1.2s ease-in-out infinite;}',
    '.nxc-typing span:nth-child(2){animation-delay:.2s;}',
    '.nxc-typing span:nth-child(3){animation-delay:.4s;}',
    '@keyframes nxbounce{0%,80%,100%{transform:translateY(0);opacity:.4}',
    '40%{transform:translateY(-5px);opacity:1}}',

    /* Input */
    '#nxc-foot{padding:10px;border-top:1px solid var(--nxborder);background:var(--nxbg);}',
    '#nxc-form{display:flex;align-items:center;gap:8px;background:var(--nxs);',
    'border:1px solid var(--nxborder);border-radius:14px;padding:6px 6px 6px 14px;',
    'transition:border-color .2s,box-shadow .2s;}',
    '#nxc-form:focus-within{border-color:var(--nxc);',
    'box-shadow:0 0 0 2px rgba(108,99,255,.2);}',
    '#nxc-inp{flex:1;background:transparent;border:none;outline:none;',
    'color:var(--nxtext);font-size:.82rem;font-family:inherit;',
    'resize:none;height:22px;max-height:88px;overflow-y:auto;line-height:1.4;}',
    '#nxc-inp::placeholder{color:var(--nxmuted);}',
    '#nxc-send{width:34px;height:34px;border-radius:10px;border:none;',
    'background:var(--nxgrad);color:#fff;font-size:15px;cursor:pointer;',
    'display:flex;align-items:center;justify-content:center;flex-shrink:0;',
    'transition:transform .15s,opacity .15s;}',
    '#nxc-send:hover:not(:disabled){transform:scale(1.07);}',
    '#nxc-send:disabled{opacity:.4;cursor:not-allowed;}',
    '#nxc-hint{text-align:center;font-size:.6rem;color:var(--nxmuted);margin-top:5px;}',
  ].join('');
  document.head.appendChild(style);

  /* ════════════════════════════════════
     2. BUILD HTML
     ════════════════════════════════════ */
  var root = document.createElement('div');
  root.id = 'nexum-widget-root';
  root.innerHTML = [
    /* Launcher */
    '<button id="nxc-launcher" aria-label="Open Nexum chat">',
    '  <span id="nxc-icon-open">&#128172;</span>',
    '  <span id="nxc-icon-close" style="display:none">&#10005;</span>',
    '</button>',

    /* Widget box */
    '<div id="nxc-box" role="dialog" aria-label="Nexum AI Chat">',

    /* Header */
    '  <div id="nxc-head">',
    '    <div class="nxc-logo">&#129504;</div>',
    '    <div>',
    '      <div class="nxc-title">Nexum AI</div>',
    '      <div class="nxc-sub">Intelligent Assistant</div>',
    '    </div>',
    '    <div class="nxc-dot"><span></span> Online</div>',
    '    <button id="nxc-close" aria-label="Close chat">&#10005;</button>',
    '  </div>',

    /* Messages */
    '  <div id="nxc-msgs">',
    '    <div class="nxc-row bot">',
    '      <div class="nxc-av bot">&#129504;</div>',
    '      <div class="nxc-bub bot">',
    '        <p>Hello! I\'m the <strong>Nexum AI Assistant</strong>. How can I help you today?</p>',
    '      </div>',
    '    </div>',
    '  </div>',

    /* Input */
    '  <div id="nxc-foot">',
    '    <div id="nxc-form">',
    '      <textarea id="nxc-inp" rows="1" placeholder="Ask about Nexum..." aria-label="Your message"></textarea>',
    '      <button id="nxc-send" aria-label="Send">&#10148;</button>',
    '    </div>',
    '    <p id="nxc-hint">Enter to send &middot; Shift+Enter for new line</p>',
    '  </div>',

    '</div>',
  ].join('');
  document.body.appendChild(root);

  /* ════════════════════════════════════
     3. LOGIC
     ════════════════════════════════════ */
  var box      = document.getElementById('nxc-box');
  var launcher = document.getElementById('nxc-launcher');
  var msgs     = document.getElementById('nxc-msgs');
  var inp      = document.getElementById('nxc-inp');
  var sendBtn  = document.getElementById('nxc-send');
  var icoOpen  = document.getElementById('nxc-icon-open');
  var icoClose = document.getElementById('nxc-icon-close');

  /* Toggle open/close */
  function toggleWidget() {
    var isOpen = box.classList.toggle('open');
    icoOpen.style.display  = isOpen ? 'none'   : '';
    icoClose.style.display = isOpen ? ''        : 'none';
    if (isOpen) { inp.focus(); scrollBottom(); }
  }
  launcher.addEventListener('click', toggleWidget);
  document.getElementById('nxc-close').addEventListener('click', toggleWidget);

  /* Scroll to bottom */
  function scrollBottom() { msgs.scrollTop = msgs.scrollHeight; }

  /* Strip accidental ```html``` fences the LLM might include */
  function sanitize(html) {
    return (html || '').replace(/^```html?\s*/i, '').replace(/```\s*$/, '').trim();
  }

  /* Add a message row */
  function addMsg(role, content, asHtml) {
    var row = document.createElement('div'); row.className = 'nxc-row ' + role;
    var av  = document.createElement('div'); av.className  = 'nxc-av ' + role;
    av.textContent = role === 'user' ? '\uD83D\uDC64' : '\uD83E\uDDE0';
    var bub = document.createElement('div'); bub.className = 'nxc-bub ' + role;
    if (asHtml) bub.innerHTML = content;
    else        bub.textContent = content;
    row.appendChild(av);
    row.appendChild(bub);
    msgs.appendChild(row);
    scrollBottom();
  }

  /* Typing indicator */
  function showTyping() {
    var row = document.createElement('div'); row.className = 'nxc-row bot'; row.id = 'nxc-typing';
    var av  = document.createElement('div'); av.className  = 'nxc-av bot'; av.textContent = '\uD83E\uDDE0';
    var bub = document.createElement('div'); bub.className = 'nxc-bub bot';
    bub.innerHTML = '<div class="nxc-typing"><span></span><span></span><span></span></div>';
    row.appendChild(av); row.appendChild(bub);
    msgs.appendChild(row); scrollBottom();
  }
  function hideTyping() { var e = document.getElementById('nxc-typing'); if (e) e.remove(); }

  /* Send a message */
  function send() {
    var q = inp.value.trim();
    if (!q) return;
    inp.value = ''; inp.style.height = '22px'; sendBtn.disabled = true;
    addMsg('user', q, false);
    showTyping();

    fetch(API_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ question: q })
    })
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function (data) {
      hideTyping();
      addMsg('bot', sanitize(data.answer || '<p>Sorry, no response received.</p>'), true);
    })
    .catch(function (err) {
      hideTyping();
      addMsg('bot', '<p>&#9888; Something went wrong. Please try again.</p>', true);
      console.error('[Nexum Widget]', err);
    })
    .finally(function () {
      sendBtn.disabled = false;
      inp.focus();
    });
  }

  sendBtn.addEventListener('click', send);

  /* Auto-resize textarea */
  inp.addEventListener('input', function () {
    this.style.height = '22px';
    this.style.height = Math.min(this.scrollHeight, 88) + 'px';
  });

  /* Enter = send, Shift+Enter = newline */
  inp.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });

})();
