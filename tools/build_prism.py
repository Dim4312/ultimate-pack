"""Build dist/UltimatePack-prism.zip: a Prism Launcher instance that syncs the pack on every launch."""
import pathlib
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BOOTSTRAP_URL = "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar"

DIST.mkdir(exist_ok=True)
jar = DIST / "packwiz-installer-bootstrap.jar"
if not jar.exists():
    urllib.request.urlretrieve(BOOTSTRAP_URL, jar)

out = DIST / "UltimatePack-prism.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(ROOT / "prism" / "instance.cfg", "instance.cfg")
    z.write(ROOT / "prism" / "mmc-pack.json", "mmc-pack.json")
    z.write(jar, ".minecraft/packwiz-installer-bootstrap.jar")
print(out)
