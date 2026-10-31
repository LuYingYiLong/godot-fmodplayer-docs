.. _contributing-translation:

翻译与文档维护
======================

手册、API 描述和编辑器界面使用不同的源文件。先确认内容归属，避免重复维护同一份翻译。

源文件与生成结果
------------------------

.. list-table::
   :header-rows: 1

   * - 内容
     - 维护源文件
   * - 中文手册
     - 文档仓库的 ``source/*.rst`` 及其子目录，使用 reStructuredText。
   * - 英文手册
     - 文档仓库的 ``locales/en/LC_MESSAGES/**/*.po``，由中文手册提取消息。
   * - API 英文说明
     - 插件仓库的 ``doc_classes/*.xml``。
   * - API 中文说明
     - 插件仓库的 ``addons/fmod_player/translations/documentation/zh_CN.po``，供内置帮助和网站共用。
   * - 编辑器属性与界面
     - 插件中的属性与界面 CSV，使用 FMOD Translations 面板维护。

``classref/xml/``、``classref/translations/``、``classref/api.json`` 是文档发布快照；``source/classes/class_*.rst`` 是生成结果。API 内容先在插件仓库修改，再同步快照和生成页面。

修改手册与英文翻译
--------------------------

以下命令在文档仓库根目录执行。普通手册改动不需要安装 Godot 或 FMOD SDK：

.. code-block:: sh

    python -m pip install -r requirements.txt
    python scripts/build_docs.py --gettext
    sphinx-intl update -p build/gettext -l en

在对应 ``.po`` 文件中翻译新增或变更的消息，复核模糊匹配后移除 ``fuzzy`` 标记，再构建两种语言：

.. code-block:: sh

    python scripts/build_docs.py

中文输出位于 ``build/html/zh_CN/``，英文位于 ``build/html/en/``；日志位于 ``build/logs/``。构建会把 Sphinx 警告视为失败，并检查类参考、锚点和本地链接。

- 手册 PO 保留 ``msgid``，只修改 ``msgstr``。源文档变化后重新提取消息，不另外复制一套英文 RST。
- 保留 API 名称、代码示例、``:ref:``、``:doc:`` 和链接目标，使用 :doc:`../glossary` 中一致的术语。
- API 类页面不进入手册 gettext 目录，它们直接使用插件 XML 和共享 API PO。

维护 API 描述与中文类帮助
--------------------------------------

英文 XML 的签名、默认值、单位、返回值和线程说明应与绑定一致。中文 PO 的每条消息对应完整 XML 描述，保留 ``[param]``、``[method]`` 等标记和格式占位符。

文档仓库保留了 API 翻译维护工具。下面示例在文档仓库运行，假设插件仓库与之并列：

.. code-block:: powershell

    $plugin = (Resolve-Path ../godot-fmodplayer).Path
    python scripts/documentation_translations.py update --xml-dir "$plugin/doc_classes" --po "$plugin/addons/fmod_player/translations/documentation/zh_CN.po"
    # Translate new messages and review fuzzy entries before checking.
    python scripts/documentation_translations.py check --xml-dir "$plugin/doc_classes" --po "$plugin/addons/fmod_player/translations/documentation/zh_CN.po" --strict

更新后的 PO 提交到插件仓库。未翻译或带 ``fuzzy`` 的条目在编辑器中回退英文；网站发布前的严格检查要求译文完整且已确认。

API 接口变更时先构建并同步测试插件，再用文档仓库的 ``scripts/export_classref_api.gd`` 导出 ClassDB，运行 ``scripts/sync_classref.py`` 同步 XML、API 和 PO 快照。完整导出命令见 `文档仓库 README 的类参考说明 <https://github.com/LuYingYiLong/godot-fmodplayer-docs#%E7%B1%BB%E5%8F%82%E8%80%83>`_。

只修改说明或 PO 时无需重编译插件，可使用同一接口构建的 ClassDB 导出。同步后运行 ``python scripts/build_docs.py``，通过 :ref:`class_* <class_FmodServer>` 和 ``enum_*`` 标签引用类与枚举，不手改生成页面。

编辑器属性与界面翻译
----------------------------

打开 **项目 > 工具 > FMOD Translations**，选择属性、编辑器界面或 API 文档目录。修改现有条目后保存，并切换编辑器语言检查实际显示。PO 编辑需要 Python 与 Babel，可使用文档环境中的 Python。

属性与界面翻译分别使用 ``godot.properties`` 和 ``godot.editor`` 域；类帮助使用 ``godot.documentation``。修改显示文本时保留运行时标识符、资源路径和枚举值，保持简体中文、繁体中文、日文和俄文界面目录一致。

从 XML 刷新 API 消息使用上面的文档仓库工具；插件界面的源码提取依赖相应的源码工具，缺少工具时可先维护已有条目，不必恢复已移除的外部测试脚本。

提交前检查
------------------

- 中英文页面均可构建，变更页面无未翻译或未经确认的条目。
- 表格、代码块、目录、内部引用和英文页面的段落均正常显示。
- 在 Godot 中检查变更涉及的属性、菜单或类帮助；步骤见 :doc:`testing`。
- 说明修改的是手册、插件翻译还是 API 源文件；需要跨仓库同步时链接对应 PR。
