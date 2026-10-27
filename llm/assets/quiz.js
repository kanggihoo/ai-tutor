// 공용 퀴즈 위젯. 즉시 피드백.
// <div class="quiz" data-quiz='{"q":"...","options":["a","b"],"answer":1,"why":"..."}'></div>
// <div class="quiz" data-num='{"q":"...","answer":114688,"tol":0.02,"unit":"바이트","why":"..."}'></div>
(function () {
  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

  function choice(el, d) {
    el.innerHTML = `<div class="qq">${d.q}</div><div class="opts"></div><div class="fb" aria-live="polite"></div>`;
    const opts = el.querySelector(".opts"), fb = el.querySelector(".fb");
    d.options.forEach((o, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "opt"; b.textContent = o;
      b.onclick = () => {
        if (i === d.answer) {
          b.classList.add("right");
          opts.querySelectorAll("button").forEach(x => x.disabled = true);
          fb.className = "fb ok"; fb.innerHTML = "맞아요. " + (d.why || "");
        } else {
          b.classList.add("wrong"); b.disabled = true;
          fb.className = "fb no"; fb.textContent = "아니에요. 다시 골라 보세요." + (d.hint ? " 힌트: " + d.hint : "");
        }
      };
      opts.appendChild(b);
    });
  }

  function numeric(el, d) {
    const id = "n" + Math.random().toString(36).slice(2, 8);
    el.innerHTML = `<div class="qq">${d.q}</div>
      <div class="numq"><label for="${id}" class="src">답 (${esc(d.unit || "")})</label>
      <input id="${id}" type="number" inputmode="decimal" style="width:12em">
      <button type="button">확인</button></div><div class="fb" aria-live="polite"></div>`;
    const inp = el.querySelector("input"), fb = el.querySelector(".fb");
    const check = () => {
      const v = parseFloat(inp.value);
      if (isNaN(v)) { fb.className = "fb no"; fb.textContent = "숫자를 넣어 주세요."; return; }
      const ok = Math.abs(v - d.answer) <= Math.abs(d.answer) * (d.tol ?? 0.01);
      fb.className = "fb " + (ok ? "ok" : "no");
      fb.innerHTML = ok ? "맞아요. " + (d.why || "") : "아니에요. " + (d.hint || "식에 넣은 숫자를 하나씩 다시 확인해 보세요.");
    };
    el.querySelector("button").onclick = check;
    inp.addEventListener("keydown", e => { if (e.key === "Enter") check(); });
  }

  document.querySelectorAll(".quiz").forEach(el => {
    if (el.dataset.quiz) choice(el, JSON.parse(el.dataset.quiz));
    else if (el.dataset.num) numeric(el, JSON.parse(el.dataset.num));
  });
})();
