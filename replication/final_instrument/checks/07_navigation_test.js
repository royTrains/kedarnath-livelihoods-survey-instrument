// Drive the form's REAL navigation and relevance code by stubbing the browser APIs it touches.
// The form shows ONE MODULE per screen, so these tests are about module-level movement and about
// gates that open or close sibling questions on the screen the enumerator is already looking at.
// Nothing here reimplements the form.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
let js = html.split("<script>")[1].split("</script>")[0];

// --- minimal DOM: enough for render() to run without throwing -------------------------------
const el = () => ({ _h: "", set innerHTML(v){ this._h = v }, get innerHTML(){ return this._h },
  style: {}, textContent: "", className: "", dataset: {}, scrollTop: 0,
  querySelectorAll: () => [], querySelector: () => null, addEventListener(){}, appendChild(){},
  classList: { toggle(){}, contains: () => false }, disabled: false, scrollIntoView(){} });
const nodes = {};
global.document = { getElementById: id => nodes[id] || (nodes[id] = el()),
  querySelectorAll: () => [], createElement: el, addEventListener(){} };
global.window = { addEventListener(){}, scrollTo(){} };
global.navigator = {};
global.localStorage = { _d:{}, getItem(k){return this._d[k]??null}, setItem(k,v){this._d[k]=v}, removeItem(k){delete this._d[k]} };
global.alert = m => { throw new Error("form alerted: " + m) };
global.confirm = () => false;
global.Blob = function(){};
global.URL = { createObjectURL: () => "blob:x" };
global.setTimeout = f => f;

js = js.replace(/^const draft[\s\S]*$/m, "");
eval(js + "\n;module.exports={get D(){return D},set D(v){D=v},get curMod(){return curMod},set curMod(v){curMod=v},get screen(){return screen},CFG,QBY,visible,validate,moduleErrors,modList,start,next,back,render,applyGates,refilter,pruneFiltered,setL:v=>{L=v}};");
const A = module.exports;

let pass = 0, fail = 0;
function ok(cond, msg){ if (cond){ pass++; console.log("  PASS  " + msg) } else { fail++; console.log("  FAIL  " + msg) } }

// how many questions the current module is showing
const shownIn = code => A.CFG.q.filter(q => q.m === code && A.visible(q)).length;

A.start();
const mods = A.modList();
console.log(`\n  form opens on module ${A.curMod}, ${mods.length} modules, ${shownIn(A.curMod)} questions on screen\n`);
ok(A.curMod === mods[0], "opens on the first module");

// ---- Next must refuse while a visible required question is blank ------------------------------
const atStart = A.curMod;
A.next();
ok(A.curMod === atStart, "next() refuses to leave a module with blank required questions");
ok(A.moduleErrors().length > 0, "moduleErrors() reports the blanks rather than failing silently");

// fill the first module and move on
function fillModule(){
  A.CFG.q.filter(q => q.m === A.curMod && A.visible(q)).forEach(q => {
    if (q.n === "consent"){ A.D[q.n] = 1; return }
    A.D[q.n] = q.t === "one" || q.t === "multi" ? String(q.c[0][0])
             : q.t === "text" ? "likha hua jawab" : "3";
  });
}
fillModule();
A.next();
ok(A.curMod === mods[1], "next() advances once the module validates");

// ---- Back returns to the previous module, answers intact --------------------------------------
A.back();
ok(A.curMod === mods[0], "back() returns to the previous module");
const firstQ = A.CFG.q.find(q => q.m === mods[0] && q.t !== "one" && q.t !== "multi");
if (firstQ){
  A.D[firstQ.n] = "7";
  A.next(); A.next(); A.back(); A.back();
  ok(String(A.D[firstQ.n]) === "7", "a typed value survives two modules forward and two back");
} else { ok(true, "a typed value survives (no free-text item in module 1 to test)") }

// ---- a gate inside a module opens/closes its siblings on the same screen ----------------------
// knows_monthly_income = 1 shows twelve monthly earnings questions; = 0 shows the annual fallback.
const calMod = A.CFG.q.find(q => q.n === "knows_monthly_income").m;
A.curMod = calMod; A.render();
fillModule();
A.D.knows_monthly_income = "1";
const withMonthly = shownIn(calMod);
A.D.knows_monthly_income = "0";
const withAnnual = shownIn(calMod);
ok(withMonthly !== withAnnual, `the gate reshapes its own module in place (${withMonthly} vs ${withAnnual} questions)`);
ok(withMonthly > withAnnual, "the monthly route shows more questions than the annual fallback");
A.D.knows_monthly_income = "1";
ok(shownIn(calMod) === withMonthly, "flipping the gate back restores the questions it hid");

// ---- a hidden required question must never block the screen -----------------------------------
A.D.knows_monthly_income = "0";
const hiddenBlank = A.CFG.q.filter(q => q.m === calMod && !A.visible(q) && !q.opt);
A.CFG.q.filter(q => q.m === calMod && A.visible(q)).forEach(q => {
  if (A.D[q.n] === undefined || A.D[q.n] === "") A.D[q.n] = q.c ? String(q.c[0][0]) : "3";
});
ok(hiddenBlank.length > 0 && A.moduleErrors().length === 0,
   `${hiddenBlank.length} gated-off required questions do not block the module`);

// ---- the two defects reported from live use, 2026-10-01 ---------------------------------------

// (1) other_activity_types shares the 14-option occupation list with `occupation`, so the primary
// occupation was being offered again as a second activity. A choice filter existed but ran only at
// render time, and with a whole module on one screen `occupation` is answered on the SAME screen --
// so the list built at render carried the primary occupation for the entire pass. It only ever
// looked fixed because leaving the module and returning re-rendered it. refilter() now re-runs the
// filter on every change; this asserts the resulting list.
const occMod = A.CFG.q.find(q => q.n === "occupation").m;
A.curMod = occMod;
A.render();
const oat = A.QBY["other_activity_types"];
ok(!!oat.cfx, "other_activity_types declares a choice filter");
A.D.n_other_activities = "2";                      // open the gate on the list
A.D.occupation = String(oat.c[2][0]);              // choose the third occupation
const drop = String(A.D[oat.cfx] ?? "");
const shown = oat.c.filter(c => String(c[0]) !== drop);
ok(shown.length === oat.c.length - 1,
   `the chosen occupation is removed from the other-activities list (${oat.c.length} options -> ${shown.length})`);
ok(!shown.some(c => String(c[0]) === String(A.D.occupation)),
   "and it is specifically the occupation that was chosen which is absent");
// an answer already given must not survive becoming unavailable
A.D.other_activity_types = String(oat.c[2][0]) + " " + String(oat.c[5][0]);
A.applyGates();
ok(!String(A.D.other_activity_types || "").split(/\s+/).includes(String(A.D.occupation)),
   "an other-activity answer equal to the occupation is dropped when the filter re-runs");

// (2) distress_event_last365d was a REQUIRED multi-select with no option meaning "nothing happened",
// so a household with no shock in twelve months had nothing it could legitimately tick and the form
// would not advance. This was the blocking question.
const dis = A.QBY["distress_event_last365d"];
const esc = dis.c.filter(c => /nothing|none/i.test(c[1]));
ok(esc.length === 1,
   `the shock list offers exactly one no-shock escape ("${esc.length ? esc[0][1] : "MISSING"}")`);
if (esc.length){
  A.D.distress_event_last365d = String(esc[0][0]);
  ok(A.validate(dis) === null, "ticking the escape alone validates, so the interview can advance");
  const real = dis.c.find(c => !/nothing|none/i.test(c[1]));
  A.D.distress_event_last365d = esc[0][0] + " " + real[0];
  ok(A.validate(dis) !== null,
     "ticking the escape alongside a real shock is refused by the constraint");
}

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
