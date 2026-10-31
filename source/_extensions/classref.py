"""Generate class references and use their canonical labels for title links."""
from pathlib import Path
import sys

from docutils import nodes
from docutils.nodes import make_id
from sphinx.builders.gettext import MessageCatalogBuilder

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from generate_classref import generate
from classref_generator import ROOT, render_classes


class GuideMessageCatalogBuilder(MessageCatalogBuilder):
    """API messages are extracted from XML by the plugin's catalog tool."""

    def write_doc(self, docname, doctree):
        if not docname.startswith('classes/class_'):
            super().write_doc(docname, doctree)


def canonical_class_title(app, doctree):
    if not app.env.docname.startswith('classes/class_'):
        return
    section = next(doctree.findall(nodes.section), None)
    if section is None:
        return
    canonical = make_id(Path(app.env.docname).name)
    if canonical not in section['ids']:
        raise ValueError(f'Missing canonical class label: {app.env.docname}')
    automatic_ids = set(section['ids']) - {canonical}
    section['ids'] = [canonical]
    for identifier in automatic_ids:
        doctree.ids.pop(identifier, None)
    for name, identifier in list(doctree.nameids.items()):
        if identifier in automatic_ids:
            doctree.nameids.pop(name)
            doctree.nametypes.pop(name, None)
            if name in section['names']:
                section['names'].remove(name)
    doctree.ids[canonical] = section
    for node in doctree.findall(nodes.Element):
        if node.get('refid') in automatic_ids:
            node['refid'] = canonical


def prepare_translated_sources(app):
    # Class descriptions are translated before BBCode becomes RST. Guides still use Sphinx PO.
    language = app.config.language
    app._fmod_class_sources = (render_classes(language) if language != 'en' and
                              app.builder.name != 'gettext' else {})
    if app.builder.name == 'gettext':
        for stale in (Path(app.outdir) / 'classes').glob('class_*.pot'):
            stale.unlink()


def translate_class_source(app, docname, source):
    if not docname.startswith('classes/class_'):
        return
    app.env.note_dependency(str(ROOT / 'classref/manifest.json'))
    app.env.note_dependency(str(ROOT / 'scripts/documentation_translations.py'))
    if app.config.language != 'en':
        app.env.note_dependency(str(ROOT / 'classref/translations' / (app.config.language + '.po')))
    classes = getattr(app, '_fmod_class_sources', {})
    for name, content in classes.items():
        if docname == 'classes/class_' + name.lower():
            source[0] = content
            break


def setup(app):
    app.add_builder(GuideMessageCatalogBuilder, override=True)
    generate()
    app.connect('builder-inited', prepare_translated_sources)
    app.connect('source-read', translate_class_source)
    # Normalize before Sphinx collects section links for sidebars and local TOCs.
    app.connect('doctree-read', canonical_class_title, priority=100)
    return {'version': '3', 'parallel_read_safe': True, 'parallel_write_safe': True}
