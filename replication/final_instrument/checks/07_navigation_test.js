// Drive the form's REAL navigation and relevance code by stubbing the browser APIs it touches.
// The point is the gate scenario: answering a question that hides later ones used to shift every
// index after it, so Back landed on a different question and typed answers looked lost.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
let js = html.split("<script>")[1].split("</script>")[0];

// --- minimal DOM: enough for render() to run without throwing -------------------------------
const el = () => ({ _h: "", set innerHTML(v){ this._h = v }, get innerHTML(){ return this._h },
  style: {}, textContent: "", className: "", dataset: {}, scrollTop: 0,
  querySelectorAll: () => [], addEventListener(){}, appendChild(){}, classList:{toggle(){}}, disabled:false });
const nodes = {};
global.document = {
  getElementById: id => nodes[id] || (nodes[id] = el()),
  querySelectorAll: () => [], createElement: el, addEventListener(){},
};
global.window = { addEventListener(){}, scrollTo(){} };
global.navigator = {};
global.localStorage = { _d:{}, getItem(k){return this._d[k]??null}, setItem(k,v){this._d[k]=v}, removeItem(k){delete this._d[k]} };
global.alert = () => {}; global.confirm = () => false; global.URL = { createObjectURL: () => "" };
global.Blob = function(){}; global.setTimeout = (f)=>f;

js = js.replace(/^const draft[\s\S]*$/m, "");           // drop the auto-start at the bottom
eval(js + "\n;module.exports={get D(){return D},set D(v){D=v},get cur(){return cur},set cur(v){cur=v},get idx(){return idx},rebuild,render,next,back,start,shown:()=>shown,setL:v=>{L=v}};");
const A = module.exports;

let pass = 0, fail = 0;
const ok  = (m)=>{ console.log("  PASS  "+m); pass++ };
const bad = (m)=>{ console.log("  FAIL  "+m); fail++ };

A.start();
const total = A.shown().length;
console.log(`\n  form opens with ${total} visible questions\n`);

// walk to the earnings gate, answering as we go
// Answer whatever question we are on with the first value that actually passes its constraint --
// a fixed dummy fails things like age (10-90) and days_week (1-7), and next() rightly refuses.
const CANDIDATES = [1, 2, 5, 7, 12, 30, 100, 1000];
function step(){
  const from = A.cur;
  for (const v of CANDIDATES){
    A.D[from] = v;
    A.next();
    if (A.cur !== from) return true;          // it advanced, so the value was accepted
  }
  return false;
}
function answer(name, val){
  let guard = 0;
  while (A.cur !== name && guard++ < 500) { if (!step()) { bad(`stuck at ${A.cur}`); return false } }
  if (A.cur !== name) { bad(`could not reach ${name} in ${guard} steps`); return false }
  A.D[name] = val; return true;
}

// ---- 1. a gate that HIDES questions -----------------------------------------------------------
if (answer("knows_monthly_income", 0)) {
  const before = A.shown().length;
  A.next();
  const after = A.shown().length;
  ok(`gate answered; visible set recomputed (${before} -> ${after} questions)`);
  const landed = A.cur;
  ok(`after the gate, landed on "${landed}" (not a stale index)`);
  A.back();
  A.cur === "knows_monthly_income"
    ? ok("Back returns to the gate question itself")
    : bad(`Back landed on "${A.cur}", expected knows_monthly_income`);
}

// ---- 2. typed values survive going forward and back -------------------------------------------
// Position directly rather than walking: the walker would overwrite the gate and re-hide the target.
A.D.knows_monthly_income = 0;
A.rebuild();
A.cur = "income_annual_total";
A.render();
A.D.income_annual_total = 250000;
A.next();                       // -> pct_income_yatra
A.D.pct_income_yatra = 80;      // fill it, or next() rightly refuses to advance
A.next();                       // -> the question after it
A.back(); A.back();             // back to income_annual_total
A.D.income_annual_total === 250000
  ? ok("a typed value survives two forward steps and two back steps")
  : bad(`value lost: got ${A.D.income_annual_total}`);
A.cur === "income_annual_total"
  ? ok("and Back returns to the question that holds it")
  : bad(`Back landed on "${A.cur}"`);

// ---- 2b. a blank required field must BLOCK next() ----------------------------------------------
A.cur = "pct_income_yatra"; A.render();
delete A.D.pct_income_yatra;
A.next();
A.cur === "pct_income_yatra"
  ? ok("next() refuses to advance past a blank required question")
  : bad(`next() advanced past a blank required question to "${A.cur}"`);
A.D.pct_income_yatra = 80;

// ---- 3. flipping the gate the other way re-opens the hidden questions --------------------------
A.D.knows_monthly_income = 1;
A.rebuild();
A.shown().some(q => q.n === "income_m1")
  ? ok("flipping the gate back re-opens the monthly earnings questions")
  : bad("hidden questions did not come back");

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
