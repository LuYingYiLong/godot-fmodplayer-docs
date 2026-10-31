"""Check canonical API anchors, translations and every local HTML link."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import re
import sys

from babel.messages.pofile import read_po
from docutils.nodes import make_id
from generate_classref import ROOT, VENDOR, generate
from classref_generator import check_translations


class Page(HTMLParser):
    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.text: list[str] = []
        source = path.read_text(encoding='utf-8')
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if 'id' in attributes:
            identifier = attributes['id']
            assert identifier not in self.ids, f'Duplicate HTML id: {identifier}'
            self.ids.add(identifier)
        if tag == 'a' and 'href' in attributes:
            self.links.append(attributes['href'])

    def handle_data(self, data):
        self.text.append(data)


def check(languages: list[str]) -> None:
    generate(check=True)
    manifest = json.loads((ROOT / 'classref/manifest.json').read_text(encoding='utf-8'))
    provenance = json.loads((VENDOR / 'PROVENANCE.json').read_text(encoding='utf-8'))
    for file, digest in provenance['files'].items():
        assert hashlib.sha256((VENDOR / file).read_bytes()).hexdigest() == digest, file
    check_translations(manifest, strict=True)
    legacy = list((ROOT / 'locales/zh_CN/LC_MESSAGES/classes').glob('class_*.po'))
    assert not legacy, 'Retired API catalogs must not be maintained alongside the shared XML PO'
    for language in languages:
        directory = ROOT / 'build/html' / language
        pages: dict[Path, Page] = {}

        def page(path):
            path = path.resolve()
            if path not in pages:
                assert path.is_file(), f'Missing link target: {path}'
                pages[path] = Page(path)
            return pages[path]

        anchor_count = 0
        for name in manifest['classes']:
            basename = f'class_{name.lower()}'
            current = page(directory / 'classes' / (basename + '.html'))
            assert make_id(name) not in current.ids, f'Noncanonical class title ID: {name}'
            assert '🔗' not in ''.join(current.text), f'Unexpected link emoji: {basename}'
            source = (ROOT / 'source/classes' / (basename + '.rst')).read_text(encoding='utf-8')
            labels = re.findall(r'(?m)^\.\. _([^:]+):', source)
            assert all(label.startswith(('class_', 'enum_')) for label in labels), basename
            for label in labels:
                assert make_id(label) in current.ids, f'Missing HTML anchor: {label}'
            anchor_count += len(labels)
        for file in directory.rglob('*.html'):
            current = page(file)
            for link in current.links:
                url = urlsplit(link)
                if url.scheme or url.netloc or (url.path and not url.path.endswith('.html')):
                    continue
                target = page(file.parent / unquote(url.path)) if url.path else current
                if url.fragment:
                    assert unquote(url.fragment) in target.ids, f'{file.relative_to(directory)}: {link}'
        capture = page(directory / 'classes/class_fmodaudioeffectcapture.html')
        assert ('丢弃新帧' if language == 'zh_CN' else 'incoming frames are discarded') in ''.join(capture.text)
        print(f'{language}: {len(manifest["classes"])} classes, {anchor_count} canonical anchors, '
              f'{len(pages)} HTML pages and local links passed')


if __name__ == '__main__':
    check(sys.argv[1:] or ['zh_CN', 'en'])
