"""Check generated URLs for GitHub account sites, project sites and custom domains."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class DeploymentTests(unittest.TestCase):
    def test_deployment_addresses_and_complete_source_download(self):
        cases = [
            ('https://example.github.io', 'https://example.github.io/'),
            ('https://example.github.io/portfolio', 'https://example.github.io/portfolio/'),
            ('https://chriscox.example/', 'https://chriscox.example/'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'portfolio'
            shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns('.git', '.openai', '__pycache__'))
            for configured, expected in cases:
                with self.subTest(site_url=configured):
                    result = subprocess.run(
                        [sys.executable, 'generate.py'], cwd=project,
                        env={**os.environ, 'SITE_URL': configured},
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    dist = project / 'dist'
                    home = (dist / 'index.html').read_text(encoding='utf-8')
                    card = (dist / 'card/index.html').read_text(encoding='utf-8')
                    self.assertIn(f'<link rel="canonical" href="{expected}">', home)
                    self.assertIn(f'<meta property="og:url" content="{expected}">', home)
                    self.assertIn(f'<link rel="canonical" href="{expected}card/">', card)
                    self.assertIn(f'content="{expected}assets/chris-cox-portrait.webp"', card)
                    self.assertIn('<base href="../">', card)
                    data = (dist / 'data.js').read_text(encoding='utf-8').removeprefix('window.PORTFOLIO_DATA = ').rstrip(';\n')
                    self.assertEqual(json.loads(data)['contact']['siteUrl'], expected)
                    vcard = (dist / 'assets/chris-cox.vcf').read_bytes().decode().replace('\r\n ', '')
                    self.assertIn('URL:' + expected + '\r\n', vcard)
                    self.assertIn(expected + 'card/', vcard)
                    self.assertIn('Chris.Cox@wcmo.edu', vcard)
                    for text in [home, card, data, vcard]:
                        self.assertNotIn('localhost', text)
                        self.assertNotIn('.chatgpt.site', text)
                        self.assertNotIn('{{', text)
                    with zipfile.ZipFile(dist / 'assets/portfolio-source.zip') as archive:
                        self.assertIn('.github/workflows/deploy-pages.yml', archive.namelist())
                        self.assertIn('START_HERE.md', archive.namelist())
                        self.assertNotIn('dist/assets/portfolio-source.zip', archive.namelist())
                        self.assertFalse(any(name.startswith(('.git/', '.openai/')) for name in archive.namelist()))
                        self.assertEqual(archive.read('dist/card/index.html').decode(), card)

    def test_ci_cannot_silently_publish_preview_urls(self):
        result = subprocess.run(
            [sys.executable, 'generate.py'], cwd=ROOT,
            env={**os.environ, 'GITHUB_ACTIONS': 'true', 'SITE_URL': ''},
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SITE_URL is required', result.stderr)


if __name__ == '__main__':
    unittest.main()
