"""Generate the complete class reference and category pages from XML."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

from documentation_translations import load_catalog, source_messages, translated_tree, translations, validate

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'scripts/vendor/godot'
MANIFEST = ROOT / 'classref/manifest.json'
CATEGORY_TITLES = {'core': 'Core API', 'audio': 'Audio resources', 'playback': 'Playback',
                   'nodes': 'Nodes', 'dsp': 'DSP effects', 'mixer': 'Audio buses',
                   'spatial': 'Spatial audio', 'additional': 'Editor integration'}


def native_type(value: dict, result: bool = False) -> str:
    if value['type'] == 0:
        return 'Variant' if value.get('usage', 0) & 131072 else 'void' if result else 'Variant'
    return (value['class_name'] or 'Object') if value['type'] == 24 else value['type_name']


def check_type(xml: ET.Element, value: dict, context: str, result: bool = False) -> None:
    expected = native_type(value, result)
    actual = xml.get('type')
    if actual != expected and not (expected == 'Array' and actual.endswith('[]')):
        raise ValueError(f'{context}: XML type {actual} != ClassDB type {expected}')


def check_inputs(manifest: dict) -> dict[str, ET.Element]:
    trees = {}
    for filename, checksum in manifest['xml_sha256'].items():
        file = ROOT / 'classref/xml' / filename
        if hashlib.sha256(file.read_bytes()).hexdigest() != checksum:
            raise ValueError(f'Snapshot changed: {file}. Run sync_classref.py instead of editing snapshots.')
        node = ET.parse(file).getroot()
        trees[node.get('name')] = node
    api = json.loads((ROOT / 'classref/api.json').read_text(encoding='utf-8'))
    if set(trees) != set(manifest['classes']) or set(api) != set(trees):
        raise ValueError('XML, manifest and ClassDB class lists differ')
    for name, tree in trees.items():
        native = api[name]
        if tree.get('inherits') != native['inherits']:
            raise ValueError(f'{name}: parent class mismatch')
        methods = {node.get('name'): node for node in tree.findall('methods/method')}
        exported = {item['name']: item for item in native['methods']}
        if methods.keys() != exported.keys():
            raise ValueError(f'{name}: XML/API method mismatch: {methods.keys() ^ exported.keys()}')
        for method_name, node in methods.items():
            method = exported[method_name]
            context = f'{name}.{method_name}'
            check_type(node.find('return'), method['return'], context + ' return', True)
            parameters = node.findall('param')
            if [p.get('name') for p in parameters] != [p['name'] for p in method['args']]:
                raise ValueError(f'{context}: argument names differ')
            for parameter, argument in zip(parameters, method['args']):
                check_type(parameter, argument, context + '.' + argument['name'])
            for qualifier, flag in [('const', 4), ('static', 32), ('vararg', 16)]:
                if (qualifier in node.get('qualifiers', '').split()) != bool(method['flags'] & flag):
                    raise ValueError(f'{context}: {qualifier} qualifier mismatch')
            defaults = [p.get('default') for p in parameters if p.get('default') is not None]
            if defaults != method['default_args_repr']:
                raise ValueError(f'{context}: default arguments differ')
        properties = {node.get('name'): node for node in tree.findall('members/member') if not node.get('overrides')}
        exported_properties = {p['name']: p for p in native['properties'] if p['type'] != 0}
        exported_properties.update({p['name']: p for p in native.get('dynamic_properties', [])})
        if properties.keys() != exported_properties.keys():
            raise ValueError(f'{name}: XML/API property mismatch: {properties.keys() ^ exported_properties.keys()}')
        for property_name, node in properties.items():
            check_type(node, exported_properties[property_name], f'{name}.{property_name}')
        constants = {node.get('name'): int(node.get('value')) for node in tree.findall('constants/constant')}
        if constants != {node['name']: node['value'] for node in native['constants']}:
            raise ValueError(f'{name}: XML/API constants differ')
        if {s.get('name') for s in tree.findall('signals/signal')} != {s['name'] for s in native['signals']}:
            raise ValueError(f'{name}: XML/API signals differ')
    return trees


def load_generator():
    spec = importlib.util.spec_from_file_location('godot_classref_generator', VENDOR / 'doc/tools/make_rst.py')
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def catalog_element(info: dict) -> ET.Element:
    attributes = {'name': info['name']}
    if info['inherits']:
        attributes['inherits'] = info['inherits']
    element = ET.Element('class', attributes)
    constants = ET.SubElement(element, 'constants')
    for attributes in info.get('constants', []):
        ET.SubElement(constants, 'constant', attributes)
    for section, tag in [('methods', 'method'), ('members', 'member'), ('signals', 'signal')]:
        parent = ET.SubElement(element, section)
        for name in info.get(section, []):
            node = ET.SubElement(parent, tag, {'name': name})
            if tag == 'method':
                ET.SubElement(node, 'return', {'type': 'void'})
            elif tag == 'member':
                node.set('type', 'Variant')
    return element


def check_translations(manifest: dict, strict: bool = False) -> dict:
    helper = ROOT / 'scripts/documentation_translations.py'
    if hashlib.sha256(helper.read_bytes()).hexdigest() != manifest['localization_tool_sha256']:
        raise ValueError('Localization helper changed. Run sync_classref.py.')
    reports = {}
    for filename, digest in manifest['translation_sha256'].items():
        path = ROOT / 'classref/translations' / filename
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Translation snapshot changed. Run sync_classref.py.')
        reports[filename] = validate(source_messages(ROOT / 'classref/xml'), load_catalog(path), strict)
    return reports


def render_classes(language: str = 'en') -> dict[str, str]:
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    trees = check_inputs(manifest)
    check_translations(manifest)
    mapping = translations(ROOT / 'classref/translations' / (language + '.po')) if language != 'en' else {}
    upstream = load_generator()
    upstream.strings_l10n.update(mapping)
    state = upstream.State()
    for info in json.loads((VENDOR / 'types.json').read_text(encoding='utf-8')):
        state.parse_class(catalog_element(info), 'godot-catalog/' + info['name'] + '.xml')
    for name, element in trees.items():
        state.parse_class(translated_tree(element, mapping), str(ROOT / 'classref/xml' / (name + '.xml')))
    state.sort_classes()
    contents: dict[str, str] = {}
    temporary_root = ROOT / 'build/.classref-tmp'
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temporary_root) as temporary:
        assert Path(temporary).resolve().is_relative_to(temporary_root.resolve())
        for name in manifest['classes']:
            state.current_class = name
            state.classes[name].update_class_group(state)
            upstream.make_rst_class(state.classes[name], state, False, temporary)
            filename = f'class_{upstream.sanitize_class_name(name, True)}.rst'
            content = (Path(temporary) / filename).read_text(encoding='utf-8')
            content = re.sub(r'\.\. Generated automatically.*?\n\n', '.. Generated from plugin XML; do not edit.\n.. XML source: ' + manifest['repository'] + '/blob/' + manifest['plugin_revision'] + '/doc_classes/' + name + '.xml\n\n', content, count=1, flags=re.S)
            content = re.sub(r' ?:ref:`🔗<[^>]+>`', '', content)
            contents[name] = content
    if state.num_errors or state.num_warnings:
        raise ValueError(f'Godot XML generator: {state.num_errors} errors, {state.num_warnings} warnings')
    return contents


def generate(check: bool = False) -> list[Path]:
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    contents = render_classes()
    generated: dict[Path, str] = {}
    for name, content in contents.items():
        generated[ROOT / 'source/classes' / f'class_{name.lower()}.rst'] = content
    for category, title in CATEGORY_TITLES.items():
        names = manifest['categories'].get(category, [])
        content = title + '\n' + '=' * len(title) + '\n\n.. toctree::\n   :maxdepth: 1\n\n'
        content += ''.join(f'   ../classes/class_{name.lower()}\n' for name in names)
        generated[ROOT / 'source/api_reference' / (category + '.rst')] = content
    title = 'Class reference'
    index = title + '\n' + '=' * len(title) + '\n\n.. toctree::\n   :maxdepth: 2\n\n'
    index += ''.join(f'   ../api_reference/{category}\n' for category in CATEGORY_TITLES)
    generated[ROOT / 'source/classes/index.rst'] = index
    for path, content in generated.items():
        if check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                raise ValueError(f'Stale generated file: {path}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                path.write_text(content, encoding='utf-8', newline='\n')
    return list(generated)
