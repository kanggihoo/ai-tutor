// 디코딩 시뮬레이터: 토큰을 하나씩 생성하며 K·V 행이 쌓이는 모습.
// <div data-decode-sim='{"words":["나는","오늘"],"heads":8}'></div>
// 모드 토글: 캐시 있음(새 행 1개만 계산) / 캐시 없음(전체 행 다시 계산)
(function () {
  function mount(root, cfg) {
    const H = cfg.heads || 8, words = cfg.words;
    let n = 1, cache = true, total = { on: 1, off: 1 };
    root.innerHTML = `
      <div class="controls">
        <button type="button" data-a="next">다음 토큰 생성</button>
        <button type="button" class="ghost" data-a="mode"></button>
        <button type="button" class="ghost" data-a="reset">처음으로</button>
      </div>
      <div class="scroll"><div class="dsim"></div></div>
      <div class="stats">
        <div class="stat good"><b data-s="new"></b><span>이번 스텝에 계산한 K·V 행</span></div>
        <div class="stat"><b data-s="reuse"></b><span>캐시에서 꺼내 쓴 행</span></div>
        <div class="stat warn"><b data-s="totOff"></b><span>캐시 없이 누적 계산 (행)</span></div>
        <div class="stat good"><b data-s="totOn"></b><span>캐시 있을 때 누적 계산 (행)</span></div>
      </div>`;
    const grid = root.querySelector(".dsim");
    const seg = () => Array.from({ length: H }, (_, i) => `<div class="h${i % 8}"></div>`).join("");
    const $ = s => root.querySelector(`[data-s="${s}"]`);
    function render() {
      let html = `<div class="trow"><div></div><div class="hd">K (head ${H}조각)</div><div class="hd">V (head ${H}조각)</div></div>`;
      for (let i = 0; i < n; i++) {
        const cls = i === n - 1 ? "newrow" : (cache ? "" : "recalc");
        html += `<div class="trow ${cls}"><div class="tok">${words[i]}</div><div class="cell">${seg()}</div><div class="cell">${seg()}</div></div>`;
      }
      html += `<div class="trow qrow"><div class="tok" style="color:var(--new);font-size:12px">Q (지금 토큰)</div><div class="cell">${seg()}</div><div class="hd" style="text-align:left">← 위 K 전부와 head별로 내적, V를 가중합</div></div>`;
      grid.innerHTML = html;
      $("new").textContent = cache ? 1 : n;
      $("reuse").textContent = cache ? n - 1 : 0;
      $("totOff").textContent = total.off;
      $("totOn").textContent = total.on;
      root.querySelector('[data-a="mode"]').textContent = cache ? "모드: 캐시 있음 (바꾸기)" : "모드: 캐시 없음 (바꾸기)";
      root.querySelector('[data-a="next"]').disabled = n >= words.length;
    }
    root.querySelector('[data-a="next"]').onclick = () => { if (n < words.length) { n++; total.on += 1; total.off += n; render(); } };
    root.querySelector('[data-a="mode"]').onclick = () => { cache = !cache; render(); };
    root.querySelector('[data-a="reset"]').onclick = () => { n = 1; total = { on: 1, off: 1 }; render(); };
    render();
  }
  document.querySelectorAll("[data-decode-sim]").forEach(el => mount(el, JSON.parse(el.dataset.decodeSim)));
})();
