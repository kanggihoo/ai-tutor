// Attention 시각화 컴포넌트 2개.
// 1) <div data-attn-demo='{"tokens":[...],"heads":{"이름":{"ask":"...","scores":[[...]]}}}'></div>
//    지금 위치(행)를 고르면 head별 점수 → softmax → V 가중합 비율을 막대로. mask 켜고 끄기.
// 2) <div data-causal-grid='{"tokens":[...],"layers":3,"extra":["토큰"]}'></div>
//    층 × 위치 격자. 칸을 누르면 그 칸이 의존하는 칸 표시. 토큰을 추가하면 바뀌는 칸 표시.
(function () {
  function softmax(xs) { const m = Math.max(...xs); const e = xs.map(x => Math.exp(x - m)); const s = e.reduce((a, b) => a + b, 0); return e.map(x => x / s); }

  function attnDemo(root, cfg) {
    const T = cfg.tokens, names = Object.keys(cfg.heads);
    let cur = T.length - 1, head = names[0], mask = true;
    root.innerHTML = `
      <div class="controls" data-r="tok"></div>
      <div class="controls" data-r="head"></div>
      <div class="controls"><button type="button" class="ghost" data-r="mask"></button></div>
      <div class="attn" data-r="out"></div>
      <p class="src" data-r="sum"></p>`;
    const r = k => root.querySelector(`[data-r="${k}"]`);
    function render() {
      r("tok").innerHTML = `<span class="src">지금 위치(Q):</span>` + T.map((t, i) => `<button type="button" class="${i === cur ? "" : "ghost"}" data-i="${i}">${t}</button>`).join("");
      r("head").innerHTML = `<span class="src">head:</span>` + names.map(n => `<button type="button" class="${n === head ? "" : "ghost"}" data-h="${n}">${n}</button>`).join("");
      r("mask").textContent = mask ? "causal mask 켜짐 (GPT) — 끄기" : "causal mask 꺼짐 (BERT처럼) — 켜기";
      const h = cfg.heads[head], row = h.scores[cur];
      const vis = row.map((_, j) => !mask || j <= cur);
      const w = softmax(row.map((s, j) => vis[j] ? s : -1e9));
      r("out").innerHTML = `<div class="attn-ask">Q(${T[cur]}, ${head})가 묻는 것: <b>${h.ask}</b></div>` +
        T.map((t, j) => `<div class="attn-row ${vis[j] ? "" : "masked"}">
          <div class="attn-tok">K(${t})</div>
          <div class="attn-score mono">${vis[j] ? "점수 " + row[j] : "−∞ (가림)"}</div>
          <div class="attn-bar"><div style="width:${(w[j] * 100).toFixed(1)}%"></div></div>
          <div class="attn-w mono">${(w[j] * 100).toFixed(0)}%</div></div>`).join("");
      const top = T.map((t, j) => [t, w[j]]).filter(x => x[1] > 0.005).sort((a, b) => b[1] - a[1]);
      r("sum").innerHTML = `결과 = ` + top.map(([t, x]) => `${(x * 100).toFixed(0)}% × V(${t})`).join(" + ");
      r("tok").querySelectorAll("[data-i]").forEach(b => b.onclick = () => { cur = +b.dataset.i; render(); });
      r("head").querySelectorAll("[data-h]").forEach(b => b.onclick = () => { head = b.dataset.h; render(); });
    }
    r("mask").onclick = () => { mask = !mask; render(); };
    render();
  }

  function causalGrid(root, cfg) {
    const base = cfg.tokens.slice(), extra = cfg.extra || ["?"], L = cfg.layers || 3;
    let n = base.length, mask = true, sel = null, changed = new Set();
    const all = base.concat(extra);
    root.innerHTML = `
      <div class="controls">
        <button type="button" data-r="add">토큰 하나 추가</button>
        <button type="button" class="ghost" data-r="mask"></button>
        <button type="button" class="ghost" data-r="reset">처음으로</button>
      </div>
      <div class="scroll"><div class="cgrid" data-r="g"></div></div>
      <p class="src" data-r="msg"></p>`;
    const r = k => root.querySelector(`[data-r="${k}"]`);
    const rowName = l => l === 0 ? "임베딩 (+위치)" : `${l}층 출력`;
    function deps(l, i) { // (l,i)가 의존하는 칸
      const s = new Set();
      (function walk(l, i) { s.add(l + "," + i); if (l === 0) return; for (let j = 0; j < n; j++) if (!mask || j <= i) walk(l - 1, j); })(l, i);
      return s;
    }
    function render() {
      const g = r("g");
      g.style.gridTemplateColumns = `120px repeat(${n}, minmax(64px, 1fr))`;
      const dep = sel ? deps(sel[0], sel[1]) : new Set();
      let h = "";
      for (let l = L; l >= 0; l--) {
        h += `<div class="cg-lab">${rowName(l)}</div>`;
        for (let i = 0; i < n; i++) {
          const k = l + "," + i;
          const cls = ["cg-cell", dep.has(k) ? "dep" : "", sel && sel[0] === l && sel[1] === i ? "sel" : "", changed.has(k) ? "chg" : ""].join(" ");
          h += `<button type="button" class="${cls}" data-l="${l}" data-i="${i}" aria-label="${rowName(l)} ${all[i]}">x${i + 1}</button>`;
        }
      }
      h += `<div></div>` + Array.from({ length: n }, (_, i) => `<div class="cg-tok">${all[i]}</div>`).join("");
      g.innerHTML = h;
      g.querySelectorAll(".cg-cell").forEach(b => b.onclick = () => { sel = [+b.dataset.l, +b.dataset.i]; changed.clear(); render(); });
      r("mask").textContent = mask ? "causal mask 켜짐 (GPT) — 끄기" : "causal mask 꺼짐 (BERT처럼) — 켜기";
      r("add").disabled = n >= all.length;
      let msg = "";
      if (changed.size) {
        const old = [...changed].filter(k => +k.split(",")[1] < n - 1).length;
        msg = old === 0 ? "주황 칸만 새로 생겼습니다. 기존 칸은 하나도 바뀌지 않았으므로 기존 K·V를 그대로 재사용할 수 있습니다."
          : `기존 칸 ${old}개가 바뀌었습니다(주황). 위 층의 과거 K·V도 바뀌므로 캐시를 재사용할 수 없습니다.`;
      } else if (sel) msg = `${rowName(sel[0])}의 x${sel[1] + 1}는 파란 칸들로만 계산됩니다. 그 칸에서 만든 K·V도 마찬가지입니다.`;
      else msg = "칸을 하나 눌러 보세요. 그 칸을 계산하는 데 쓰이는 칸이 파랗게 표시됩니다.";
      r("msg").textContent = msg;
    }
    r("add").onclick = () => {
      if (n >= all.length) return;
      n++; sel = null; changed = new Set();
      for (let l = 0; l <= L; l++) for (let i = 0; i < n; i++) {
        if (i === n - 1) changed.add(l + "," + i);
        else if (!mask && l > 0) changed.add(l + "," + i);
      }
      render();
    };
    r("mask").onclick = () => { mask = !mask; changed.clear(); render(); };
    r("reset").onclick = () => { n = base.length; sel = null; changed.clear(); render(); };
    render();
  }

  document.querySelectorAll("[data-attn-demo]").forEach(el => attnDemo(el, JSON.parse(el.dataset.attnDemo)));
  document.querySelectorAll("[data-causal-grid]").forEach(el => causalGrid(el, JSON.parse(el.dataset.causalGrid)));
})();
