"""Check manuscript compilation and bibliography; optionally inspect PDF tools."""
from pathlib import Path
import re
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
build = root / "build"
log = (build / "main.log").read_text(errors="replace")
errors = []
for phrase in ("Undefined control sequence", "undefined references", "undefined citations",
               "There were undefined", "multiply defined", "Fatal error"):
    if phrase.lower() in log.lower():
        errors.append(phrase)
overfull = re.findall(r"Overfull \\[hv]box \((\d+(?:\.\d+)?)pt too (?:wide|high)\)", log)
if any(float(x) > 0.5 for x in overfull):
    errors.append("Overfull boxes: " + ", ".join(overfull))
aux = (build / "main.aux").read_text()
body = re.search(r"\\newlabel\{end:body\}\{\{[^}]*\}\{(\d+)\}", aux)
if not body:
    errors.append("Missing body-end page marker")
elif int(body.group(1)) > 12:
    errors.append("Body exceeds EuroSys's 12-page technical-content limit")
else:
    print(f"Technical content: {body.group(1)} pages (EuroSys limit 12; references separate)")
pdf = build / "main.pdf"
if not pdf.is_file():
    errors.append("Missing main.pdf")
if shutil.which("pdfinfo") and pdf.is_file():
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    for line in info.splitlines():
        if line.startswith(("Pages:", "Page size:")):
            print(line)
    if not re.search(r"Page size:\s+612 x 792 pts", info):
        errors.append("PDF is not US Letter")
if shutil.which("pdffonts") and pdf.is_file():
    fonts = subprocess.check_output(["pdffonts", str(pdf)], text=True)
    for line in fonts.splitlines()[2:]:
        fields = line.split()
        if len(fields) >= 6 and fields[-5] != "yes":
            errors.append("Unembedded font: " + line)
    print("Font embedding checked")
if errors:
    raise SystemExit("Build check failed:\n" + "\n".join(errors))
print("No undefined references/citations or material box overflow")
