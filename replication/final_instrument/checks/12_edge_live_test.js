// Drive the form in a REAL Microsoft Edge instance over the DevTools Protocol.
//
// Checks 07 and 08 drive the form's functions against a stubbed DOM. This one loads the built page in
// an actual browser, so it exercises what those cannot: real rendering, real event listeners, real
// clicks, real CSS, and whatever the console says while it happens. It is the check that would have
// caught a question rendering with no usable input.
//
// Prerequisite: Edge listening on 9222 with the form open. Launch it with
//   msedge.exe --remote-debugging-port=9222 --user-data-dir=<a scratch dir> <file:// url to index.html>
//
// Usage: node checks/12_edge_live_test.js [port]

const PORT = process.argv[2] || 9222;
const results = [];
const consoleErrors = [];
let ws, nextId = 1;
const pending = new Map();

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error("timeout " + method)) } }, 20000);
  });
}

// Evaluate in the page and return the value. Throws if the page threw, so a broken rule surfaces
// here instead of being swallowed.
async function js(expr) {
  const r = await send("Runtime.evaluate", {
    expression: `(() => { ${expr} })()`,
    returnByValue: true, awaitPromise: true,
  });
  if (r.exceptionDetails) {
    throw new Error("page threw: " + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
  }
  return r.result.value;
}

function ok(n, label, cond, detail = "") {
  results.push({ n, label, pass: !!cond, detail });
  console.log(`  ${cond ? "PASS" : "FAIL"}  ${n}. ${label}${detail ? "  — " + detail : ""}`);
}

async function main() {
  const targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
  const page = targets.find(t => t.type === "page" && /index\.html/.test(t.url));
  if (!page) throw new Error("the form is not open in Edge; launch it on the file:// URL first");
  console.log("\n  attached to: " + page.title + "\n");

  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener("open", r));
  ws.addEventListener("message", ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { resolve, reject } = pending.get(m.id);
      pending.delete(m.id);
      m.error ? reject(new Error(m.error.message)) : resolve(m.result);
    } else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") {
      consoleErrors.push(m.params.args.map(a => a.value || a.description).join(" "));
    } else if (m.method === "Runtime.exceptionThrown") {
      consoleErrors.push("uncaught: " + (m.params.exceptionDetails.exception?.description || ""));
    }
  });
  await send("Runtime.enable");
  await send("Page.enable");

  // 1 — the page is alive and the form booted
  await send("Page.reload", { ignoreCache: true });
  await new Promise(r => setTimeout(r, 1800));
  const boot = await js("return { q: CFG.q.length, mods: modList().length, title: document.title }");
  ok(1, "Edge loads the page and the form boots",
     boot.q > 200 && boot.mods === 13, `${boot.q} questions, ${boot.mods} modules`);

  // 2 — the consent script is on screen before anything is asked
  await js("start(); return 1");
  await new Promise(r => setTimeout(r, 400));
  const consent = await js(`
    const b = document.querySelector('#app .consent');
    return { present: !!b, words: b ? b.innerText.trim().split(/\\s+/).length : 0,
             label: b ? (b.querySelector('.lead')||{}).innerText : '' };`);
  ok(2, "the consent script renders as a verbatim read-aloud block",
     consent.present && consent.words > 40, `${consent.words} words, labelled "${(consent.label||'').trim()}"`);

  // 3 — module P will not advance with consent unanswered
  const pBlocked = await js(`
    delete D.consent; applyGates();
    const before = curMod; next();
    return { before, after: curMod, errs: moduleErrors().length };`);
  ok(3, "module P refuses to advance while consent is unanswered",
     pBlocked.before === pBlocked.after && pBlocked.errs > 0, `${pBlocked.errs} blocking question(s)`);

  // 4 — THE REPORTED BLOCKER: the shock list must be answerable by a household with no shock
  const shock = await js(`
    const q = QBY['distress_event_last365d'];
    const esc = q.c.filter(c => /nothing|none/i.test(c[1]));
    D.distress_event_last365d = esc.length ? String(esc[0][0]) : '';
    return { options: q.c.length, escapes: esc.length,
             label: esc.length ? esc[0][1] : null,
             required: !q.opt, validates: validate(q) === null };`);
  ok(4, "the shock list offers a no-shock option and accepts it",
     shock.escapes === 1 && shock.validates,
     `required=${shock.required}, option "${shock.label}"`);

  // 5 — and refuses it alongside a real shock
  const excl = await js(`
    const q = QBY['distress_event_last365d'];
    const esc = q.c.find(c => /nothing|none/i.test(c[1]));
    const real = q.c.find(c => !/nothing|none/i.test(c[1]));
    D.distress_event_last365d = esc[0] + ' ' + real[0];
    const msg = validate(q);
    return { refused: msg !== null, msg: msg || '' };`);
  ok(5, "ticking it alongside a real shock is refused, with a message",
     excl.refused, excl.msg.slice(0, 54));

  // 6 — THE REPORTED FILTER BUG: in the real DOM, on one screen, by clicking
  const filt = await js(`
    const occMod = CFG.q.find(q => q.n === 'occupation').m;
    curMod = occMod; render();
    D.n_other_activities = '2'; applyGates();
    const occCard = document.querySelector("[data-q='occupation']");
    const radios = [...occCard.querySelectorAll('input')];
    const chosen = radios[2].value;
    radios[2].click();                                  // a real click, real listener, real handler
    const oatCard = document.querySelector("[data-q='other_activity_types']");
    const shown = [...oatCard.querySelectorAll('input')].map(i => i.value);
    return { chosen, total: QBY['other_activity_types'].c.length,
             shownCount: shown.length, stillThere: shown.includes(chosen),
             occValue: D.occupation };`);
  ok(6, "clicking a primary occupation removes it from the other-activities list on the same screen",
     !filt.stillThere && filt.shownCount === filt.total - 1,
     `occupation=${filt.chosen}; list ${filt.total} -> ${filt.shownCount}; still present: ${filt.stillThere}`);

  // 7 — a stale answer equal to the new occupation is dropped
  const stale = await js(`
    const oat = QBY['other_activity_types'];
    const a = String(oat.c[5][0]), b = String(oat.c[6][0]);
    D.other_activity_types = a + ' ' + b;
    D.occupation = a; applyGates();
    return { after: String(D.other_activity_types || ''), dropped: a, kept: b };`);
  ok(7, "an other-activity answer equal to the occupation is dropped",
     !stale.after.split(/\s+/).includes(stale.dropped) && stale.after.includes(stale.kept),
     `"${stale.after}" no longer holds ${stale.dropped}`);

  // 8 — a module intro renders, and looks unlike a question
  const intro = await js(`
    curMod = 'C'; render();
    const b = document.querySelector('#app .intro');
    const cs = b ? getComputedStyle(b) : null;
    return { present: !!b, words: b ? b.innerText.trim().split(/\\s+/).length : 0,
             bg: cs ? cs.backgroundColor : '', border: cs ? cs.borderLeftWidth : '' };`);
  ok(8, "a module intro renders as a styled read-aloud block",
     intro.present && intro.words > 20 && intro.border !== "0px",
     `${intro.words} words, left rule ${intro.border}`);

  // 9 — the enumerator hint renders and says not to read it out
  const hint = await js(`
    curMod = QBY['job_permanence'].m; render(); applyGates();
    const card = document.querySelector("[data-q='job_permanence']");
    const h = card ? card.querySelector('.hint') : null;
    return { present: !!h, label: h ? (h.querySelector('b')||{}).innerText : '',
             words: h ? h.innerText.trim().split(/\\s+/).length : 0 };`);
  ok(9, "the enumerator hint renders on job_permanence, marked do-not-read",
     // the Hindi reads "पढ़कर न सुनाएँ" -- the negation follows the verb, so match on सुनाएँ
     hint.present && /do not read|न सुनाएँ/i.test(hint.label || ""),
     `"${(hint.label || '').trim()}", ${hint.words} words`);

  // 10 — a gate reshapes its module in place without losing a typed value
  const gate = await js(`
    curMod = QBY['knows_monthly_income'].m; render();
    const vis = () => CFG.q.filter(q => q.m === curMod && visible(q)).length;
    D.knows_monthly_income = '1'; applyGates(); const withMonthly = vis();
    const card = document.querySelector("[data-q='income_m5']");
    if (card){ const inp = card.querySelector('input'); inp.value = '4321';
               inp.dispatchEvent(new Event('input', {bubbles:true})); }
    const typed = D.income_m5;
    D.knows_monthly_income = '0'; applyGates(); const withAnnual = vis();
    D.knows_monthly_income = '1'; applyGates();
    return { withMonthly, withAnnual, typed, back: vis() };`);
  ok(10, "a gate reshapes the module in place and the value typed into it was captured",
     gate.withMonthly > gate.withAnnual && gate.back === gate.withMonthly && gate.typed === "4321",
     `${gate.withMonthly} vs ${gate.withAnnual} questions; typed value ${gate.typed}`);

  // 11 — a whole interview, then both exports
  const run = await js(`
    localStorage.clear(); start(); D.consent = 1;
    let hops = 0;
    while (hops++ < 40) {
      const mod = curMod;
      for (let pass = 0; pass < 4; pass++) {
        CFG.q.filter(q => q.m === mod && visible(q)).forEach(q => {
          if (D[q.n] !== undefined && D[q.n] !== '') return;
          if (q.n === 'consent') { D[q.n] = 1; return }
          if (q.t === 'one' || q.t === 'multi') {
            let opts = q.c;
            const drop = q.cfx ? String(D[q.cfx] ?? '') : '';
            const only = q.cfo ? SEL(q.cfo) : null;
            if (drop) opts = opts.filter(c => String(c[0]) !== drop);
            if (only) opts = opts.filter(c => only.includes(String(c[0])));
            if (opts.length) D[q.n] = String(opts[0][0]);
          } else if (q.t === 'text') { D[q.n] = 'likha hua jawab'; }
          else { D[q.n] = '5'; }
        });
        applyGates();
      }
      let errs = moduleErrors();
      for (let t = 0; t < 10 && errs.length; t++) {
        errs.forEach(([q]) => { for (const v of [1,0,2,3,5,7,10,25,50]) { D[q.n] = v; if (!validate(q)) break } });
        errs = moduleErrors();
      }
      if (errs.length) return { stuck: mod, errs: errs.map(e => e[0].n + ': ' + e[1]).slice(0,3) };
      next();
      if (screen === 'done') break;
      if (curMod === mod) return { stuck: mod, errs: ['next() did not advance'] };
    }
    return { stuck: null, stored: all().length, screen };`);
  ok(11, "a full interview completes in the browser",
     !run.stuck && run.stored >= 1,
     run.stuck ? `stuck in module ${run.stuck}: ${(run.errs||[]).join('; ')}` : `${run.stored} record stored`);

  const exp = await js(`
    let names = [];
    const realCreate = document.createElement.bind(document);
    document.createElement = tag => { const el = realCreate(tag);
      if (tag === 'a'){ const c = el.click.bind(el); el.click = () => { names.push(el.download) } } return el };
    exportCsv(); exportCsv(1);
    document.createElement = realCreate;
    return names;`);
  ok(12, "both exports fire, coded and labelled",
     exp.length === 2 && exp.some(n => /_labels_/.test(n || "")), exp.join(" , "));

  ok(13, "no uncaught JavaScript errors during the whole run",
     consoleErrors.length === 0,
     consoleErrors.length ? consoleErrors.slice(0, 2).join(" | ") : "console clean");

  const failed = results.filter(r => !r.pass);
  console.log(`\n  ${results.length - failed.length} passed, ${failed.length} failed\n`);
  ws.close();
  process.exit(failed.length ? 1 : 0);
}

main().catch(e => { console.error("\n  HARNESS ERROR: " + e.message + "\n"); process.exit(2) });
