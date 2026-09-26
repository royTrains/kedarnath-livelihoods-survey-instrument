"""Shared helpers for building the plain-language PDFs. Numbers always come from data files, never typed by hand."""
import os, re, subprocess, shutil

PDFLATEX = r"C:\Users\HP\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
HERE = os.path.dirname(os.path.abspath(__file__))

_SPECIAL = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}

def esc(s):
    s = str(s)
    s = s.replace("\\", r"\textbackslash{}")
    return "".join(_SPECIAL.get(c, c) for c in s)

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs,longtable,array,graphicx,enumitem}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\renewcommand{\arraystretch}{1.15}
\newcommand{\plainbox}[1]{\par\vspace{2pt}\noindent\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{#1}}\par\vspace{2pt}}
"""

def header(title, subtitle):
    return (PREAMBLE + "\\begin{document}\n"
            "{\\Large\\textbf{" + esc(title) + "}}\\par\n"
            "{\\large " + esc(subtitle) + "}\\par\\vspace{4pt}\\hrule\\vspace{8pt}\n")

def compile_tex(tex_path):
    """Compile twice, keep only the PDF."""
    d, name = os.path.split(tex_path)
    env = os.environ.copy()   # a PATH entry that points at an .exe (not a folder) makes MiKTeX fail at exit; drop it
    env["PATH"] = os.pathsep.join(x for x in env.get("PATH", "").split(os.pathsep) if not x.lower().rstrip("\/").endswith(".exe"))
    for _ in range(2):
        r = subprocess.run([PDFLATEX, "-interaction=nonstopmode", "-halt-on-error", name], cwd=d, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(r.stdout[-2500:])
            raise SystemExit(f"LaTeX failed for {name}")
    base = os.path.splitext(name)[0]
    for ext in (".aux", ".log", ".out", ".toc"):
        p = os.path.join(d, base + ext)
        if os.path.exists(p):
            os.remove(p)
    return os.path.join(d, base + ".pdf")

def fmt(x, nd=1):
    return f"{x:.{nd}f}"
