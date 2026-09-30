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
eval(js + "\n;module.exports={get D(){return D},set D(v){D=v},get curMod(){return curMod},set curMod(v){curMod=v},get screen(){return screen},CFG,QBY,visible,validate,moduleErrors,modList,start,next,finish,exportCsv,all,render};");
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
// The form shows one MODULE per screen, so a filled interview is: answer every question the module is
// currently showing, press Next, repeat. Gates inside a module reshape it as answers land, so the
// visible set is recomputed after each answer rather than once per module.
for (let i = 0; i < 50; i++){
  A.start();
  let hops = 0, stuck = false;
  while (hops++ < 40){
    const mod = A.curMod;
    // several passes: answering one question can open another in the same module
    for (let pass = 0; pass < 4; pass++){
      A.CFG.q.filter(q => q.m === mod && A.visible(q)).forEach(q => {
        if (A.D[q.n] !== undefined && A.D[q.n] !== "") return;
        A.D[q.n] = q.n === "consent" ? 1 : answerFor(q);
      });
    }
    // clear anything that fails its own constraint, then retry a few sane values
    let errs = A.moduleErrors();
    for (let tries = 0; tries < 12 && errs.length; tries++){
      errs.forEach(([q]) => {
        for (const v of [1, 0, 2, 3, 5, 7, 10, 12, 25, 50, 100]){
          A.D[q.n] = v;
          if (!A.validate(q)) return;
        }
      });
      errs = A.moduleErrors();
    }
    if (errs.length){
      guardTrips++;
      if (guardTrips <= 3) console.log("    dead-end in module", mod, "->", errs.map(e => e[0].n + ": " + e[1]).join("; ").slice(0,160));
      stuck = true; break;
    }
    A.next();
    if (A.screen === "done") break;
    if (A.curMod === mod){ guardTrips++; stuck = true; break }
  }
  if (!stuck && A.screen !== "done") A.finish();
  filled++;
}
console.log(`  interviews completed: ${filled} / 50   (validation dead-ends: ${guardTrips})`);
console.log(`  records in storage:   ${A.all().length}`);
A.exportCsv();
if (!CSV) { console.error("  exportCsv produced nothing"); process.exit(1) }
fs.writeFileSync(process.argv[3], CSV, "utf8");
const lines = CSV.replace(/^\ufeff/,"").trim().split("\n");
console.log(`  CSV written: ${lines.length-1} data rows x ${lines[0].split(",").length} columns  (codes)`);

// ---- the same rows again, with the chosen option written out in words ------------------------
// Same column order, same row order; only coded columns differ. Written next to the coded file with
// a _labels suffix so the two can be diffed, which is what proves the mapping is a pure relabelling
// and not a different extract.
A.exportCsv(1);
const LAB = CSV;
const labPath = process.argv[3].replace(/\.csv$/i, "") + "_labels.csv";
fs.writeFileSync(labPath, LAB, "utf8");
const cl = lines[0].split(",");
const ll = LAB.replace(/^\ufeff/,"").trim().split("\n");
console.log(`  CSV written: ${ll.length-1} data rows x ${ll[0].split(",").length} columns  (labels)  -> ${labPath}`);

let bad = [];
if (ll[0] !== lines[0]) bad.push("header row differs between the two exports");
if (ll.length !== lines.length) bad.push("row count differs between the two exports");
// every coded column must have changed from a bare number to text somewhere in the file, and every
// uncoded column must be byte-identical -- that is exactly what "only relabelled" means
const coded = new Set(Object.keys(A.CFG.labs));
// A real CSV field splitter is needed here, not a regex: several option labels contain a comma
// ("Wage labour, staying at home"), so csvCell quotes them and the labelled file has quoted fields
// exactly where the coded file does not. Splitting on bare commas misaligns every later column and
// reports the whole row as changed.
function splitCsv(row){
  const out = []; let cur = "", q = false;
  for (let i = 0; i < row.length; i++){
    const ch = row[i];
    if (q){
      if (ch === '"' && row[i+1] === '"'){ cur += '"'; i++ }
      else if (ch === '"') q = false;
      else cur += ch;
    } else if (ch === '"') q = true;
    else if (ch === ","){ out.push(cur); cur = "" }
    else cur += ch;
  }
  out.push(cur);
  return out;
}
const C1 = lines.slice(1).map(splitCsv), L1 = ll.slice(1).map(splitCsv);
cl.forEach((name, j) => {
  const same = C1.every((r, i) => r[j] === L1[i][j]);
  if (!coded.has(name) && !same) bad.push(`uncoded column changed: ${name}`);
  if (coded.has(name) && same && C1.some(r => r[j] !== "")) bad.push(`coded column not relabelled: ${name}`);
});
if (bad.length){ console.error("  LABEL EXPORT FAILED:\n   " + bad.slice(0,8).join("\n   ")); process.exit(1) }
console.log(`  labels check: ${coded.size} coded columns relabelled, ${cl.length - coded.size} left byte-identical`);
