.. _before_you_start:

开始之前
================

可以从问题复现、文档、翻译、示例或源码改进开始。先确定改动属于哪个仓库，再准备对应的环境。

选择贡献位置
--------------------

.. list-table::
   :header-rows: 1

   * - 内容
     - 维护位置
   * - 插件行为、编辑器集成与测试场景
     - `Godot-FmodPlayer <https://github.com/LuYingYiLong/Godot-FmodPlayer>`_ 的源码和 ``tests/``
   * - 入门指南、使用说明与英文手册
     - `文档仓库 <https://github.com/LuYingYiLong/godot-fmodplayer-docs>`_ 的 ``source/`` 和 ``locales/en/LC_MESSAGES/``
   * - API 英文描述与中文类帮助
     - 插件仓库的 ``doc_classes/*.xml`` 和 ``addons/fmod_player/translations/documentation/zh_CN.po``

修改指南或手册翻译只需要文档环境，不必先编译插件。修改插件源码参见 :doc:`development`；验证改动参见 :doc:`testing`；翻译与类参考维护参见 :doc:`translation`。

报告问题
----------------

提交 Issue 前先搜索现有讨论。播放、导入、空间音频或导出问题，尽量附上可直接打开的最小 Godot 项目，并写清以下信息：

- Godot 与 FMOD 版本、插件版本或提交号，以及操作系统和架构。
- 可以重复执行的操作步骤、预期结果和实际结果。
- 相关输出日志；界面问题附截图，音频问题说明音频格式、加载方式及总线和效果器配置。

准备 Pull Request
--------------------------------------

- 较大的功能或接口调整先在 Issue 中说明使用场景和实现方向。
- 每个 PR 聚焦一个问题，保留有助于审查的相关文档和测试改动。
- 描述触发条件、改动后的行为和验证方式，列出实际测试的平台及尚未验证的部分。
- API 变更同步更新绑定、XML 描述、翻译及相关示例；跨仓库修改互相链接对应 PR。
- 性能改动提供相同配置和工作负载下的前后测量，并确认音频正确性。

保持提交清晰
--------------------

沿用现有代码风格，避免把无关重构或整库格式化混入功能修复。不要提交本机的 ``custom.py``、SDK 文件、FMOD 运行库、``tests/addons/``、日志、缓存和临时生成结果。

插件使用 MIT 许可证，FMOD 单独授权。贡献内容需遵守项目许可，SDK 头文件、库文件和运行库由使用者自行取得。许可入口见 :ref:`faq-plugin-license`。
