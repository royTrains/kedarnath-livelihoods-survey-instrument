// Fill the form 50 times by driving its OWN code -- the same relevance engine, the same validate(),
// the same exportCsv() that writes the file on a tablet. Nothing here reimplements the form.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
let js = html.split("<script>")[1].split("</script>")[0];

let CSV = null;
const el = () => ({ _h:"", set innerHTML(v){this._h=v}, get innerHTML(){return this._h},
  style:{}, textContent:"", className:"", dataset:{}, scrollTop:0, disabled:false,
  querySelectorAll:()=>[], addEventListener(){}, appendChild(){}, classList:{toggle(){}}, click(){} });
const nodes = {};
global.document = { getElementById: id => nodes[id] || (nodes[id] = el()),
  querySelectorAll: () => [], createElement: el, addEventListener(){} };
global.window = { addEventListener(){}, scrollTo(){} };
global.navigator = {};
global.localStorage = { _d:{}, getItem(k){return this._d[k]??null}, setItem(k,v){this._d[k]=v}, removeItem(k){delete this._d[k]} };
global.alert = m => { throw new Error("form alerted: " + m) };
global.confirm = () => false;
global.Blob = function(parts){ CSV = parts.join("") };          // capture what exportCsv writes
global.URL = { createObjectURL: () => "blob:x" };
global.setTimeout = f => f;

js = js.replace(/^const draft[\s\S]*$/m, "");
eval(js + "\n;module.exports={get D(){return D},set D(v){D=v},get cur(){return cur},get shown(){return shown},CFG,start,next,finish,exportCsv,all,rebuild};");
const A = module.exports;
const Q = Object.fromEntries(A.CFG.q.map(q => [q.n, q]));

// plausible answers, so the Stata build sees a realistic spread rather than constants
const rnd = (a,b) => a + Math.floor(Math.random()*(b-a+1));
const pick = arr => arr[rnd(0, arr.length-1)];
const TEXTS = { occupation_detail:["ghoda hankta hoon","porter ka kaam","chai ki dukan","jeep chalata hoon","apni dukan hai"],
  prev_occ:["kheti","construction mazdoori","dukan par kaam",""], target_occ:["kheti","dihadi","pata nahi","koi kaam nahi"],
  native_language_other:["Awadhi","Tharu"], govt_scheme_which:["ration card","ujjwala",""],
  work_equipment_detail:["auzar","chai ka saman",""], migration_referral_other:["gaon ka pradhan"],
  training_type_other:["photography"] };

function answerFor(q){
  if (q.t === "text") return pick(TEXTS[q.n] || ["likha hua jawab"]);
  if (q.t === "multi") { const c = q.c.map(x=>x[0]); const k = rnd(1, Math.min(3, c.length));
    return [...new Set(Array.from({length:k}, () => pick(c)))].sort((a,b)=>a-b).join(" ") }
  if (q.t === "one") return pick(q.c.map(x=>x[0]));
  // numerics: respect the constraint when there is one, otherwise something sane
  if (q.con){ for (const v of [0,1,2,3,5,7,12,20,30,45,80,100,180,300]){ const x=v; try{ if(eval(q.con)) return v }catch(e){} } }
  if (q.t === "int" && /_pm$|_12m$|income|amount|spend/.test(q.n)) return rnd(0,60)*50;
  return rnd(1, 9);
}

let filled = 0, guardTrips = 0;
for (let i = 0; i < 50; i++){
  A.start();
  let steps = 0;
  while (steps++ < 600){
    const name = A.cur;
    if (!name) break;
    const q = Q[name];
    if (!q) break;
    if (name === "consent") A.D[name] = 1;                 // always consent, or the interview ends
    else A.D[name] = answerFor(q);
    const before = A.cur;
    A.next();
    if (A.cur === before){                                  // validate() refused -- try another value
      let fixed = false;
      for (const v of [0,1,2,3,5,10,25,50,100]){ A.D[name] = v; A.next(); if (A.cur !== before){ fixed = true; break } }
      if (!fixed){ guardTrips++; if(guardTrips<=3) console.log("    dead-end at:", name, "con:", q.con, "hhsize:", A.D.hhsize); break }
    }
    if (A.cur === null) break;                              // finish() ran
  }
  if (A.cur === null) filled++;
  else { A.finish(); filled++ }
}
console.log(`  interviews completed: ${filled} / 50   (validation dead-ends: ${guardTrips})`);
console.log(`  records in storage:   ${A.all().length}`);
A.exportCsv();
if (!CSV) { console.error("  exportCsv produced nothing"); process.exit(1) }
fs.writeFileSync(process.argv[3], CSV, "utf8");
const lines = CSV.replace(/^\ufeff/,"").trim().split("\n");
console.log(`  CSV written: ${lines.length-1} data rows x ${lines[0].split(",").length} columns`);
