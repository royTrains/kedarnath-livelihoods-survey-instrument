/**
 * Kedarnath Yatra Worker Survey -- Google Sheets sink.
 *
 * Paste this into Extensions > Apps Script on the receiving spreadsheet and deploy it as a web app
 * (see SETUP.md). The tablet form POSTs one finished interview per request; this writes it to two
 * tabs of the same sheet:
 *
 *   answers  -- every answer as the WORDS the respondent chose ("Own-account worker", "Firewood")
 *   codes    -- the same rows as the numeric codes the Stata build reads
 *
 * Both tabs are written from one POST, so they can never fall out of step. The words tab is the one
 * a human reads; the codes tab exists because a sheet in words alone is not analysable, and if a
 * tablet is lost before its CSV export the sheet is the only copy left.
 *
 * WHY THE VALIDATION IS ALL ON THIS SIDE
 * The form is served from GitHub Pages, so anything the form knows is public -- the deployment URL
 * and any token shipped inside the page can be read from its source. There is no way around that
 * for a static page, so the token is only a speed bump and the real defences are here, where the
 * code is not published: an allow-list of enumerator ids, a column allow-list, a cap on how many
 * rows one caller can add in a day, and an upsert that makes a replayed POST a no-op instead of a
 * duplicate. Anything rejected is written to `rejected` rather than dropped, so an attempt is
 * visible and a false rejection of real field data is recoverable.
 */

var PROPS = PropertiesService.getScriptProperties();

// Server-side timestamp and provenance, prepended to both tabs. Named with a leading underscore so
// they sort away from the instrument's own variables and can never collide with a column name.
var META = ["_received_at", "_sync_count", "_form_build"];

var ID = "resp_id";

// ---------------------------------------------------------------- helpers

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function book_() {
  var id = (PROPS.getProperty("SHEET_ID") || "").trim();
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function tab_(book, name) {
  var sh = book.getSheetByName(name);
  if (!sh) {
    sh = book.insertSheet(name);
    sh.setFrozenRows(1);
  }
  return sh;
}

/** Header name -> 1-based column. Read once per request per tab, not once per field. */
function header_(sh) {
  var n = sh.getLastColumn();
  if (n === 0) return {};
  var row = sh.getRange(1, 1, 1, n).getValues()[0];
  var map = {};
  for (var i = 0; i < row.length; i++) {
    var k = String(row[i]).trim();
    if (k) map[k] = i + 1;
  }
  return map;
}

/**
 * Make sure every name in `names` has a column, appending any that are missing.
 *
 * Columns are addressed BY NAME, never by position. The instrument gains and loses questions
 * between builds -- a module added mid-fieldwork shifts every column after it -- and a sink that
 * trusted position would silently write the new module's answers into the old module's columns for
 * every tablet still running the previous build. Appending keeps old rows valid and leaves the new
 * columns blank for them, which is the truth: those respondents were never asked.
 */
function ensure_(sh, names) {
  var map = header_(sh);
  var add = [];
  for (var i = 0; i < names.length; i++) if (!map[names[i]]) add.push(names[i]);
  if (!add.length) return map;
  var from = sh.getLastColumn() + 1;
  sh.getRange(1, from, 1, add.length).setValues([add]);
  sh.getRange(1, 1, 1, sh.getLastColumn()).setFontWeight("bold");
  for (var j = 0; j < add.length; j++) map[add[j]] = from + j;
  return map;
}

/** 1-based sheet row holding this resp_id, or 0. */
function findRow_(sh, map, id) {
  var col = map[ID];
  var last = sh.getLastRow();
  if (!col || last < 2) return 0;
  var vals = sh.getRange(2, col, last - 1, 1).getValues();
  for (var i = 0; i < vals.length; i++) if (String(vals[i][0]) === String(id)) return i + 2;
  return 0;
}

/**
 * Insert or overwrite the row for this resp_id.
 *
 * Overwriting is deliberate and is what makes the client safe to retry: the tablet only marks an
 * interview as sent once it has read an acknowledgement, so a reply lost to a dropped connection
 * means the same interview is POSTed again. Appending there would put a duplicate in the sheet for
 * every flaky moment on the route.
 */
function write_(sh, obj) {
  var names = Object.keys(obj);
  var map = ensure_(sh, names);
  var at = findRow_(sh, map, obj[ID]);
  var fresh = !at;
  if (fresh) at = Math.max(sh.getLastRow() + 1, 2);
  var width = sh.getLastColumn();
  var line = fresh ? new Array(width) : sh.getRange(at, 1, 1, width).getValues()[0];
  for (var i = 0; i < names.length; i++) line[map[names[i]] - 1] = obj[names[i]];
  for (var j = 0; j < width; j++) if (line[j] === undefined) line[j] = "";
  // setValues on a plain string array, with the column formatted as text: a sheet left on
  // automatic formatting reads "01" as 1 and "1-2" as a date, and both of those are real answers
  // here (a multi-select code list, a verbatim).
  sh.getRange(at, 1, 1, width).setNumberFormat("@").setValues([line]);
  return { row: at, action: fresh ? "inserted" : "updated" };
}

function reject_(book, why, payload) {
  var sh = tab_(book, "rejected");
  if (sh.getLastRow() === 0) {
    sh.getRange(1, 1, 1, 4).setValues([["_received_at", "reason", "resp_id", "payload"]])
      .setFontWeight("bold");
  }
  var id = "";
  try { id = String((payload && payload.row && payload.row.resp_id) || ""); } catch (e) {}
  sh.appendRow([new Date().toISOString(), why, id,
                String(JSON.stringify(payload || null)).slice(0, 40000)]);
  return json_({ ok: false, error: why });
}

// ---------------------------------------------------------------- entry points

/** Health check, so a tablet can prove the address works before anyone walks up the valley. */
function doGet() {
  var book, tabs = {};
  try {
    book = book_();
    ["answers", "codes"].forEach(function (n) {
      var sh = book.getSheetByName(n);
      tabs[n] = sh ? Math.max(sh.getLastRow() - 1, 0) : 0;
    });
  } catch (e) {
    return json_({ ok: false, error: "no spreadsheet: " + e.message });
  }
  return json_({
    ok: true,
    service: "kedarnath-survey-sink",
    sheet: book.getName(),
    interviews: tabs,
    token_required: !!(PROPS.getProperty("TOKEN") || "").trim(),
    now: new Date().toISOString()
  });
}

function doPost(e) {
  var book;
  try { book = book_(); } catch (err) { return json_({ ok: false, error: "no spreadsheet" }); }

  var body;
  try { body = JSON.parse(e.postData.contents); } catch (err) {
    return reject_(book, "unparseable body", { raw: String(e && e.postData && e.postData.contents).slice(0, 2000) });
  }

  var want = (PROPS.getProperty("TOKEN") || "").trim();
  if (want && String(body.token || "") !== want) return reject_(book, "bad token", body);

  var row = body.row;
  if (!row || !row.words || !row.codes) return reject_(book, "no row", body);

  var id = String(row.resp_id || "").trim();
  if (!/^[0-9A-Za-z_-]{4,32}$/.test(id)) return reject_(book, "bad resp_id", body);

  // Enumerator allow-list. A row claiming to come from somebody who is not on the team is the
  // cheapest signal that something other than a tablet is posting.
  var ok_enum = (PROPS.getProperty("ENUM_IDS") || "1,2,3,4").split(",").map(function (s) { return s.trim(); });
  var who = String(row.codes.enum_id === undefined ? "" : row.codes.enum_id).trim();
  if (ok_enum.indexOf(who) < 0) return reject_(book, "enum_id not on the team: " + who, body);

  // Column allow-list. COLUMNS is set once at setup from the build's own column list; until it is,
  // anything is accepted, so a first deployment works before the property is filled in.
  var allow = (PROPS.getProperty("COLUMNS") || "").trim();
  if (allow) {
    var ok_col = {};
    allow.split(",").forEach(function (s) { ok_col[s.trim()] = 1; });
    var bad = Object.keys(row.codes).filter(function (k) { return !ok_col[k]; });
    if (bad.length) return reject_(book, "unknown columns: " + bad.slice(0, 8).join(","), body);
  }

  // Daily cap. Four enumerators cannot physically produce hundreds of 45-minute interviews in a
  // day, so a day that looks like that is either a loop in the client or somebody else posting.
  var day = Utilities.formatDate(new Date(), "Asia/Kolkata", "yyyy-MM-dd");
  var cap = parseInt(PROPS.getProperty("DAILY_CAP") || "200", 10);
  var seen = parseInt(PROPS.getProperty("count_" + day) || "0", 10);

  // One writer at a time. Four tablets coming back into signal together was otherwise two requests
  // both reading lastRow, both deciding the same row was free, and one interview overwriting the
  // other.
  var lock = LockService.getScriptLock();
  try { lock.waitLock(25000); } catch (err) { return json_({ ok: false, error: "busy, retry" }); }

  try {
    var answers = tab_(book, "answers"), codes = tab_(book, "codes");

    // Collision guard. resp_id is nine random digits generated on the tablet, so a clash is
    // improbable but not impossible, and silently upserting one interview over a DIFFERENT one
    // would destroy field data. __start is the tablet's own clock at the moment the interview
    // began; if it disagrees, these are two interviews, not one, and the second gets its own id.
    var map = header_(answers);
    var at = findRow_(answers, map, id);
    if (at && map.__start) {
      var had = String(answers.getRange(at, map.__start).getValue() || "").trim();
      var now = String(row.start || "").trim();
      if (had && now && had !== now) {
        var alt = id + "-b";
        tab_(book, "collisions").appendRow([new Date().toISOString(), id, had, now, alt]);
        id = alt;
        row.words[ID] = alt;
        row.codes[ID] = alt;
        at = 0;   // the renamed interview is a NEW row; `at` still points at the one it clashed with
      }
    }

    // Checked here rather than after the write: a cap enforced once the row is already on the
    // sheet rejects nothing and just tells the tablet to send it again forever.
    if (!at && seen + 1 > cap) return reject_(book, "daily cap " + cap + " reached", { row: { resp_id: id } });

    var stamp = new Date().toISOString();
    var n = 0;
    if (at) {
      var c = header_(answers)["_sync_count"];
      if (c) n = parseInt(answers.getRange(at, c).getValue() || "0", 10) || 0;
    }

    var meta = {};
    meta._received_at = stamp;
    meta._sync_count = String(n + 1);
    meta._form_build = String(body.build || "");

    var w = {}, k;
    for (k in meta) w[k] = meta[k];
    w[ID] = id;
    w.__start = String(row.start || "");
    // The tablet has always stamped __end; nothing on this side read it, so the sheet had no
    // end time and interview_duration_min was permanently empty -- the 45-minute cap had
    // never once been measured. Duration is computed on the tablet, where both clocks agree.
    w.__end = String(row.end || "");
    w.__duration_min = String(row.duration_min === 0 ? 0 : (row.duration_min || ""));
    for (k in row.words) w[k] = row.words[k] === null || row.words[k] === undefined ? "" : String(row.words[k]);

    var cc = {};
    for (k in meta) cc[k] = meta[k];
    cc[ID] = id;
    cc.__start = String(row.start || "");
    cc.__end = String(row.end || "");
    cc.__duration_min = String(row.duration_min === 0 ? 0 : (row.duration_min || ""));
    for (k in row.codes) cc[k] = row.codes[k] === null || row.codes[k] === undefined ? "" : String(row.codes[k]);

    var r1 = write_(answers, w);
    write_(codes, cc);

    if (r1.action === "inserted") PROPS.setProperty("count_" + day, String(seen + 1));

    return json_({ ok: true, resp_id: id, row: r1.row, action: r1.action, received_at: stamp });
  } catch (err) {
    return reject_(book, "write failed: " + err.message, body);
  } finally {
    lock.releaseLock();
  }
}
