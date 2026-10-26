# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# 将 _extensions 目录加入 Python 路径，以便加载本地 Sphinx 扩展
sys.path.insert(0, str(Path(__file__).resolve().parent / '_extensions'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Godot FmodPlayer'
copyright = '2026, LuYingYiLong'
author = 'LuYingYiLong'
html_logo = "_static/fmod_player_docs_logo.png"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_copybutton',
    'gdscript',
    'sphinx_tabs.tabs',
    'sphinx.ext.intersphinx',
    'classref',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

# 添加自定义 CSS 文件
html_css_files = [
    'custom.css',
]

html_theme_options = {
  "show_toc_level": 4,
  "use_repository_button": True,
  "repository_url": "https://github.com/LuYingYiLong/godot-fmodplayer-docs",
  "use_issues_button": True,
}

# 全局可用的外部链接别名（所有 .rst 文件均可使用）
rst_epilog = """
.. _int: https://docs.godotengine.org/en/4.x/classes/class_int.html
.. _float: https://docs.godotengine.org/en/4.x/classes/class_float.html
.. _bool: https://docs.godotengine.org/en/4.x/classes/class_bool.html
.. _Variant: https://docs.godotengine.org/en/4.x/classes/class_variant.html
.. _String: https://docs.godotengine.org/en/4.x/classes/class_string.html
.. _StringName: https://docs.godotengine.org/en/4.x/classes/class_string_name.html
.. _Dictionary: https://docs.godotengine.org/en/4.x/classes/class_dictionary.html
.. _Array: https://docs.godotengine.org/en/4.x/classes/class_array.html
.. _Vector3: https://docs.godotengine.org/en/4.x/classes/class_vector3.html
.. _Vector2: https://docs.godotengine.org/en/4.x/classes/class_vector2.html
.. _Transform3D: https://docs.godotengine.org/en/4.x/classes/class_transform3d.html
.. _Node: https://docs.godotengine.org/en/4.x/classes/class_node.html
.. _Node2D: https://docs.godotengine.org/en/4.x/classes/class_node2d.html
.. _Node3D: https://docs.godotengine.org/en/4.x/classes/class_node3d.html
.. _StaticBody3D: https://docs.godotengine.org/en/4.x/classes/class_staticbody3d.html
.. _NodePath: https://docs.godotengine.org/en/4.x/classes/class_nodepath.html
.. _Mesh: https://docs.godotengine.org/en/4.x/classes/class_mesh.html
.. _PackedVector3Array: https://docs.godotengine.org/en/4.x/classes/class_packedvector3array.html
.. _PackedVector2Array: https://docs.godotengine.org/en/4.x/classes/class_packedvector2array.html
.. _PackedFloat32Array: https://docs.godotengine.org/en/4.x/classes/class_packedfloat32array.html
.. _PackedByteArray: https://docs.godotengine.org/en/4.x/classes/class_packedbytearray.html
.. _AudioStreamWAV: https://docs.godotengine.org/en/4.x/classes/class_audiostreamwav.html
.. _Object: https://docs.godotengine.org/en/4.x/classes/class_object.html
.. _RefCounted: https://docs.godotengine.org/en/4.x/classes/class_refcounted.html
.. _Resource: https://docs.godotengine.org/en/4.x/classes/class_resource.html
.. _Callable: https://docs.godotengine.org/en/4.x/classes/class_callable.html
.. _SceneTree: https://docs.godotengine.org/en/stable/classes/class_scenetree.html#scenetree
.. _AudioServer: https://docs.godotengine.org/en/4.x/classes/class_audioserver.html#audioserver
.. _Camera2D: https://docs.godotengine.org/en/stable/classes/class_camera2d.html#camera2d
.. _MeshInstance3D: https://docs.godotengine.org/en/stable/classes/class_meshinstance3d.html#meshinstance3d
.. _CollisionShape3D: https://docs.godotengine.org/en/stable/classes/class_collisionshape3d.html#collisionshape3d
.. _GDExtension: https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/index.html
"""

# multi-language docs
# 检测 Read the Docs 的语言设置，默认为中文
language = os.getenv('READTHEDOCS_LANGUAGE', 'zh_CN')

# 搜索语言设置为英文，避免 Sphinx 中文搜索的 JS 错误
# (ChineseStemmer 未定义导致搜索功能完全失效)
html_search_language = 'en'

locale_dirs = ['../locales/']                   # 翻译文件存放目录
gettext_compact = False                         # 为每个源文件生成独立的 .po 文件
gettext_uuid = True                             # 为翻译字符串添加唯一标识符
gettext_additional_targets = ['literal-block']  # 允许翻译代码块


# Use the checked-in inventory so class references build without network access.
intersphinx_mapping = {
    'godot': ('https://docs.godotengine.org/en/stable/', str(Path(__file__).resolve().parents[1] / 'scripts/vendor/godot/objects.inv')),
}
sphinx_tabs_nowarn = True
