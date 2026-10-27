// KV Cache 크기 계산기. config.json 값을 넣으면 토큰당 크기, 총 토큰, 동시 요청 수.
// <div data-kv-calc='{"presets":{"이름":{"L":28,"H":8,"D":128,"B":2}}, "mem":3, "tokens":2000}'></div>
(function () {
  function fmt(b) { if (b >= 1048576) return (b / 1048576).toFixed(2) + " MB"; if (b >= 1024) return (b / 1024).toFixed(1) + " KB"; return b + " B"; }
  function mount(root, cfg) {
    const uid = Math.random().toString(36).slice(2, 7);
    const f = (k, label, val, extra = "") => `<label for="${k}${uid}" style="display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--muted)">${label}<input id="${k}${uid}" data-k="${k}" type="number" min="0" ${extra} value="${val}" style="width:100%"></label>`;
    const names = Object.keys(cfg.presets || {});
    const first = cfg.presets[names[0]] || { L: 28, H: 8, D: 128, B: 2 };
    root.innerHTML = `
      <div class="controls">${names.map(n => `<button type="button" class="ghost" data-p="${n}">${n}</button>`).join("")}</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px">
        ${f("L", "층 수 (num_hidden_layers)", first.L)}
        ${f("H", "KV head 수 (num_key_value_heads)", first.H)}
        ${f("D", "head 크기 (head_dim)", first.D)}
        ${f("B", "바이트/숫자 (BF16=2)", first.B)}
        ${f("M", "KV에 쓸 메모리 (GB)", cfg.mem ?? 3, 'step="0.1"')}
        ${f("T", "요청당 토큰", cfg.tokens ?? 2000)}
      </div>
      <div class="formula" data-o="f"></div>
      <div class="stats">
        <div class="stat"><b data-o="tok"></b><span>토큰 1개당 KV</span></div>
        <div class="stat"><b data-o="cap"></b><span>들어가는 총 토큰 수</span></div>
        <div class="stat good"><b data-o="req"></b><span>동시 요청 수 (요청당 토큰 기준)</span></div>
      </div>`;
    const v = k => +root.querySelector(`[data-k="${k}"]`).value;
    const o = k => root.querySelector(`[data-o="${k}"]`);
    function calc() {
      const per = 2 * v("L") * v("H") * v("D") * v("B");
      const cap = per > 0 ? Math.floor(v("M") * 1024 ** 3 / per) : 0;
      o("f").textContent = `2(K,V) × ${v("L")}층 × ${v("H")} KV head × ${v("D")} × ${v("B")}바이트 = ${per.toLocaleString()} 바이트/토큰`;
      o("tok").textContent = fmt(per);
      o("cap").textContent = cap.toLocaleString();
      o("req").textContent = v("T") > 0 ? Math.floor(cap / v("T")).toLocaleString() : "-";
    }
    root.querySelectorAll("input").forEach(i => i.addEventListener("input", calc));
    root.querySelectorAll("[data-p]").forEach(b => b.onclick = () => {
      const p = cfg.presets[b.dataset.p];
      ["L", "H", "D", "B"].forEach(k => root.querySelector(`[data-k="${k}"]`).value = p[k]);
      calc();
    });
    calc();
  }
  document.querySelectorAll("[data-kv-calc]").forEach(el => mount(el, JSON.parse(el.dataset.kvCalc)));
})();
