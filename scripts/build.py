"""Create a static production artifact from an explicit allowlist; no deployment."""
import shutil
import subprocess
import sys
from pathlib import Path
from validate_catalog import ROOT, validate
from render_catalog_audit import render

def build():
    validate()
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT/'tests'), '-p', 'test_*.py'], check=True)
    for filename in ['app.js', 'sw.js', 'tests/catalog.test.cjs']:
        subprocess.run(['node', '--check', str(ROOT/filename)], check=True)
    subprocess.run(['node', '--test', str(ROOT/'tests/catalog.test.cjs')], check=True)
    render()
    files = ['index.html', 'app.js', 'style.css', 'sw.js', 'manifest.webmanifest', 'icon.svg',
             'questions.json', 'betriebs-u-fragen.pdf', 'examples/questions.demo.json',
             'imported-questions/grundlagen_der_betriebs_und_unternehmensfuerung_fragenkatalog.json',
             'reports/question-catalog-audit.md', 'reports/question-catalog-audit.json',
             'reports/question-catalog-validation.json']
    # Never recursively clear an existing directory: reject unexpected contents.
    dest = ROOT/'dist'
    allowed = set(files)
    if dest.is_symlink():
        raise RuntimeError('dist must not be a symlink')
    if dest.exists():
        unexpected = [str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file() and str(p.relative_to(dest)) not in allowed]
        if unexpected:
            raise RuntimeError('Unexpected files in dist; inspect manually: '+str(unexpected))
    for filename in files:
        target = dest/filename
        if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != ROOT):
            raise RuntimeError('Refusing symlink target: '+str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/filename, target)
    print(f'Production artifact: {dest} ({len(files)} explicitly selected files). No deployment.')

if __name__ == '__main__':
    build()
