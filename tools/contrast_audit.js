/* WCAG contrast audit for the portfolio, in both themes.
 *
 * Usage: open the built site (http://localhost:8000), paste this whole file into the browser
 * console (or run it with the browser tool's JavaScript action), and read the returned array.
 * For each theme it reports how many text elements were checked, every failure (one per selector),
 * and the lowest ratio found. Pass = 4.5:1, or 3:1 for large text (>= 24px, or >= 18.66px bold).
 * Each element's colour is blended over its ancestors' real backgrounds (cards are translucent).
 * Afterwards it removes data-theme, so the page goes back to following the system setting.
 */
(async () => {
  const parse = s => { const m = s.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m[3] === undefined ? 1 : m[3] }; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
  const bgOf = el => {
    const chain = [];
    for (let e = el; e; e = e.parentElement) chain.push(parse(getComputedStyle(e).backgroundColor));
    let c = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = chain.length - 1; i >= 0; i--) if (chain[i].a > 0) c = blend(chain[i], c);
    return c;
  };

  async function audit(theme) {
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll(".rv").forEach(e => e.classList.add("is-in"));          // finish reveals
    document.querySelectorAll(".pipe li").forEach(e => e.classList.add("is-lit"));    // finish hero light-up
    await new Promise(r => setTimeout(r, 900));                                        // let transitions settle
    const res = [];
    for (const el of document.querySelectorAll("body *")) {
      if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden" || el.closest(".hp,.skip")) continue;
      const bg = bgOf(el), fg = blend(parse(cs.color), bg);
      const L1 = lum(fg), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const size = parseFloat(cs.fontSize), large = size >= 24 || (size >= 18.66 && +cs.fontWeight >= 700);
      const cls = typeof el.className === "string" && el.className ? "." + el.className.split(" ")[0] : "";
      res.push({ sel: el.tagName.toLowerCase() + cls, ratio: +ratio.toFixed(2), need: large ? 3 : 4.5 });
    }
    const fails = [...new Map(res.filter(r => r.ratio < r.need).map(f => [f.sel, f])).values()];
    const lowest = res.reduce((a, b) => (a.ratio < b.ratio ? a : b));
    return { theme, checked: res.length, fails, lowest };
  }

  const out = [await audit("dark"), await audit("light")];
  delete document.documentElement.dataset.theme;
  console.table(out.map(o => ({ theme: o.theme, checked: o.checked, failures: o.fails.length, lowest: `${o.lowest.sel} ${o.lowest.ratio}` })));
  return out;
})();
