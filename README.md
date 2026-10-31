<p align="center">
  <img alt="fmodplayer_docs_banner" src="https://github.com/user-attachments/assets/f8fc2752-90db-4e5c-a35c-90c9ce5ad027" />
</p>
<h1 align="center">Godot-FmodPlayer Docs</h1>

## 构建

在文档仓库根目录运行，Python 3.12 或更新版本：

```sh
python -m pip install -r requirements.txt
python scripts/build_docs.py
```

Windows 虚拟环境可用以下命令：

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe scripts/build_docs.py
```

中英文页面分别输出到 `build/html/zh_CN/` 和 `build/html/en/`，构建日志放在 `build/logs/`。构建会检查 XML 快照、绑定方法、生成结果、类页面锚点和全站链接；Sphinx 警告会使构建失败。

仅构建一种语言：`python scripts/build_docs.py --language en`。原有 `make html`、`make.bat html` 和 Read the Docs 构建也会自动生成类页面。

## 贡献指南

贡献文档按工作流程分为[开始之前](source/contributing/before_you_start.rst)、[开发插件](source/contributing/development.rst)、[在 Godot 中测试](source/contributing/testing.rst)和[翻译与文档维护](source/contributing/translation.rst)。修改指南只需文档环境；插件验证从 `tests/project.godot` 的 F5 菜单和编辑器检查进入。

## 类参考

全部 47 个已注册类按 XML 生成独立页面，包括运行时 API 和编辑器集成类。英文说明和签名维护在插件仓库的 `doc_classes/*.xml`；API 中文统一维护在插件的 `addons/fmod_player/translations/documentation/zh_CN.po`，编辑器离线帮助和网站共用。生成的类页面和分类目录不手改。

`classref/xml/` 和 `classref/translations/` 是发布快照，由脚本同步并记录校验值；`classref/api.json` 记录对应插件构建的 ClassDB 接口，包括动态 EQ 属性。普通网站构建只需要本仓库和 Python 依赖。

中文构建先在内存中的 XML 副本上应用 PO，再通过 Godot 生成器转换为 RST。Sphinx 扩展在读取类页面时提供中文内容，源文件仍为英文，页面路径和锚点保持一致。`make_rst --lang` 负责模板标题，描述的翻译由生成器适配层完成。

更新 XML 后，在文档仓库运行以下 PowerShell 命令。示例假定插件与文档仓库并列，插件的测试项目已部署当前版本扩展：

```powershell
$plugin = (Resolve-Path ../godot-fmodplayer).Path
$godot = 'C:/path/to/Godot_v4.7.2-stable_win64_console.exe'
New-Item -ItemType Directory -Force "$plugin/tests/logs" | Out-Null
& $godot --headless --editor --path "$plugin/tests" --script "$PWD/scripts/export_classref_api.gd" --log-file "$plugin/tests/logs/classref_export.log" -- "$plugin/tests/logs/classref_api.json"
python scripts/sync_classref.py --plugin-root "$plugin" --api "$plugin/tests/logs/classref_api.json"
python scripts/build_docs.py
```

同步脚本会记录插件提交和 XML 校验值。若接口改动，需要先构建并部署测试扩展，再导出 ClassDB；只修改说明时仍可使用同一构建的接口导出。

在文档仓库更新插件的 API 中文，示例假设两个仓库并列。先更新消息，翻译新增条目并复核 fuzzy 标记，再执行严格检查：

```powershell
$plugin = (Resolve-Path ../godot-fmodplayer).Path
python scripts/documentation_translations.py update --xml-dir "$plugin/doc_classes" --po "$plugin/addons/fmod_player/translations/documentation/zh_CN.po"
# 翻译新增条目，复核并移除已确认条目的 fuzzy 标记
python scripts/documentation_translations.py check --xml-dir "$plugin/doc_classes" --po "$plugin/addons/fmod_player/translations/documentation/zh_CN.po" --strict
```

每条消息对应完整的 XML 描述，保留 `[param]`、`[method]` 等标记和换行。未翻译或带 `fuzzy` 的条目在编辑器中回退英文；网站的完整性检查要求全部译文已确认。只修改 PO 不需要重编译插件，重新同步快照后构建网站即可。`scripts/documentation_translations.py` 由文档仓库保留维护；同步旧插件版本时仍兼容其 `tools/` 中的工具副本。

入门指南、用户指南和目录文字继续使用 `locales/` 中的 Sphinx PO。刷新模板使用 `python scripts/build_docs.py --gettext`，再运行 `sphinx-intl update -p build/gettext -l zh_CN -l en`。gettext 构建跳过逐类 API 页面，避免生成第二份 API 翻译目录。

类、方法、属性、信号和常量使用 Godot 的 `class_*` 锚点，枚举使用 `enum_*` 锚点。手册和翻译直接引用这些标签；分类页仅提供导航。

生成器基于固定版本的 Godot `make_rst.py`，来源与校验值见 `scripts/vendor/godot/PROVENANCE.json`。适配逻辑在 `scripts/classref_generator.py`，负责移除链接图标和生成目录。新增类时更新 `classref/manifest.json` 的类列表和分类，重新导出接口、同步 XML 并更新翻译。清单中的 `unnamed_arguments` 为两个原生绑定未提供名称的参数指定文档名；原始名称保留在接口快照中。
