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
eval(js + "\n;module.exports={get D(){return D},set D(v){D=v},get curMod(){return curMod},set curMod(v){curMod=v},get screen(){return screen},CFG,QBY,visible,validate,moduleErrors,modList,start,next,back,render,setL:v=>{L=v}};");
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

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
