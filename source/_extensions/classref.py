"""Generate class references and use their canonical labels for title links."""
from pathlib import Path
import sys

from docutils import nodes
from docutils.nodes import make_id

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from generate_classref import generate


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


def setup(app):
    generate()
    # Normalize before Sphinx collects section links for sidebars and local TOCs.
    app.connect('doctree-read', canonical_class_title, priority=100)
    return {'version': '2', 'parallel_read_safe': True, 'parallel_write_safe': True}
