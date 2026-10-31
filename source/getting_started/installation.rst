安装指南
============

将 ``addons/fmod_player`` 安装到项目，放入匹配的 FMOD 运行库，再启用编辑器插件。

环境要求
------------

- Godot 4.7.2 或更新版本；这是当前扩展配置要求的最低运行版本。
- 与扩展版本、操作系统和架构匹配的 FMOD Core SDK 2.04 运行库。
- 使用发布包中包含的平台二进制；自行构建时参见 :doc:`../contributing/development`。

完整平台状态见 :ref:`platform-support`。macOS / iOS 仍为实验性支持，需自行配置 SDK、链接项和扩展库条目。

复制插件
------------

#. 从 `GitHub Releases <https://github.com/LuYingYiLong/Godot-FmodPlayer/releases>`_ 或 `Godot Asset Library <https://godotengine.org/asset-library/asset/4905>`_ 获取插件。
#. 将完整的 ``addons/fmod_player`` 文件夹复制到项目的 ``addons`` 下，保留 ``bin``、脚本、图标和翻译目录。

.. code-block:: text

    res://
    └── addons/
        └── fmod_player/
            ├── plugin.cfg
            ├── fmod_check.gd
            ├── fmod_player_main.gd
            ├── translations/
            └── bin/
                ├── fmod_player.gdextension
                └── ...

放置 FMOD 运行库
--------------------------

运行库从 `FMOD 下载页面 <https://www.fmod.com/download>`_ 获取，放在 ``res://addons/fmod_player/bin/``。Debug 与 Release 使用的文件以 ``fmod_player.gdextension`` 为准。

.. list-table::
   :header-rows: 1

   * - 平台
     - 运行库
   * - Windows x86_64
     - ``fmod.dll``
   * - Linux x86_64
     - Debug 使用 ``libfmodL.so.15``，Release 使用 ``libfmod.so.15``
   * - Android arm64
     - Debug 使用 ``libfmodL.so``，Release 使用 ``libfmod.so``，另需 ``fmod.jar``；配置见 :doc:`../export`

Linux 的版本化共享库和符号链接需一起保留，或将链接目标复制为上表中的文件名。

启用并验证
--------------

#. 在 **项目 > 项目设置 > 插件** 中启用 **FMOD Player**。
#. 刚放入运行库或替换扩展 DLL 后，重新启动编辑器。
#. 在添加节点窗口搜索 ``FmodAudioStreamPlayer``，在资源创建窗口搜索 ``FmodAudioStream``。
#. 确认输出面板没有动态库加载或 FMOD 初始化错误。

加载失败时，检查运行库名称、架构及依赖；具体步骤见 :ref:`faq-module-no-found`。

下一步
----------

按 :doc:`quick_start` 导入音频并完成首次播放。发布配置见 :doc:`../export`；插件与 FMOD 的许可入口见 :ref:`faq-plugin-license`。
