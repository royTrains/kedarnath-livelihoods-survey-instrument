# Publishing the survey form

The form is a single self-contained page with no server. GitHub Pages serves it; nothing else is
needed and nothing runs on anyone's behalf. Responses live on the tablet until an enumerator
exports them.

---

## 1. Connect the repo and push

Replace `<you>` and `<repo>` with your GitHub username and the repository you created.

```bash
cd "D:\OneDrive\Desktop\vulnerability-2-poverty"
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

**If git asks for a password, it will fail.** GitHub stopped accepting account passwords over
HTTPS. Use a personal access token instead:

1. github.com → Settings → Developer settings → Personal access tokens → **Tokens (classic)**
2. Generate new token, tick the **`repo`** scope, copy it
3. Paste the token when git asks for the *password*; your username is the *username*

If you get `remote origin already exists`, you set it earlier — replace it rather than adding:

```bash
git remote set-url origin https://github.com/<you>/<repo>.git
```

Expect **4 commits, 91 files**. If it tries to push thousands, stop — `.gitignore` is not being
applied and you are about to publish microdata. Check with `git ls-files | wc -l` first.

## 2. Turn on Pages

In the repository: **Settings → Pages**

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/docs`
- **Save**

The first build takes a minute or two. A green tick appears under **Actions** when it is live.
Your form is then at:

```
https://<you>.github.io/<repo>/
```

## 3. Check it actually works

Do these in order. Step 3 is the one that matters.

1. **Open the URL on a phone or tablet, online.** This is when the service worker caches the app.
2. **Add to Home Screen.** On iOS: Share → Add to Home Screen. On Android: ⋮ → Install app / Add to
   Home screen. This is not cosmetic — an installed app gets more durable storage than a browser
   tab, which on iOS is the difference between surviving Safari's storage eviction and not.
3. **Turn the wifi and mobile data off. Open it from the home screen icon.** It must load fully and
   let you start an interview. If this fails, the offline story is not true and nothing else about
   the setup matters.
4. **Do one dummy interview**, finish it, then ☰ → Export all (CSV). Open the file and confirm the
   columns look right.
5. **Delete the dummy** before real fieldwork: ☰ → Clear exported.

Do step 3 on **every** tablet, not one. iOS and Android handle storage differently enough that one
passing does not prove the others will.

## 4. Daily routine in the field

- Each enumerator selects their own name at the first question. That is what identifies who
  collected what; there is no login.
- Interviews save continuously, on every field change. A flat battery loses nothing.
- **Export the CSV every evening**, without exception, wherever there is connectivity — and send it
  somewhere off the device the same night.
- The badge at the top counts interviews not yet exported. It turns red past five.

The single real risk in this setup is a lost or wiped tablet holding unexported interviews. Nothing
in the software prevents that; the evening export does.

## 5. When the form changes

Rebuild, commit, push. Pages redeploys on its own.

```bash
cd replication/final_instrument
python questionnaire/build_webform.py      # writes questionnaire/ and docs/
cd ../..
git add -A && git commit -m "..." && git push
```

Tablets do **not** pick the change up mid-interview, by design. The new version installs quietly, a
banner appears saying a new version is ready, and it takes effect once the form is fully closed and
reopened. Tell enumerators to close and reopen at the start of a day, not during one.

The service worker's cache name carries a hash of the page, so a rebuild invalidates the old cache
automatically — there is no version number to remember to bump.

## 6. If something goes wrong

| Symptom | Cause |
|---|---|
| 404 at the Pages URL | Pages not enabled, or folder set to `/` instead of `/docs`. First build can also take a few minutes. |
| Page loads online but not offline | Step 3 was skipped, or it was opened from a bookmark rather than the home-screen icon. Open online once more, then retest. |
| Hindi shows as boxes | The device lacks a Devanagari font. Rare on Android and iOS; update the OS. |
| Export button does nothing | No interviews saved yet, or the browser blocked the download. Try from the installed app rather than a tab. |
| "STORAGE FULL / BLOCKED" | Export immediately, then ☰ → Clear exported. Also check the device is not in private browsing. |

## 7. What is public

The Pages site is **public even if the repository is private** — that is how GitHub Pages works on
free accounts. This is acceptable here: the page is a blank questionnaire with no backend, so there
is nothing to leak and nowhere for a stranger's answers to go. It does mean the instrument itself is
visible before publication. If that is a problem, do not use Pages — serve the same `index.html`
from a password-protected host, or copy the file onto each tablet and open it from local storage.
