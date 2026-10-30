安装指南
========

本页说明如何把 Godot-FmodPlayer 安装到 Godot 项目中，并补齐 FMOD Core API
运行库。推荐优先使用预编译版本；只有需要修改插件源码或自行适配平台时，才需要从源码构建。

安装前确认
----------

开始前请确认：

- Godot 版本为 4.7.2 或更高版本；当前编辑器 Dock 使用 4.7.2 的公开 API。
- 目标平台目前为 Windows x86_64 或 Android arm64。
- 已准备好从 FMOD 官网下载 FMOD Engine。

.. important::

   Godot-FmodPlayer 插件本身不包含 FMOD 运行库。由于 FMOD 的许可要求，
   你需要自行从 `FMOD 下载页面 <https://www.fmod.com/download>`_ 获取
   FMOD Engine，并把对应平台的运行库复制到项目中。

预编译版本（推荐）
------------------

下载插件
~~~~~~~~

#. 从 `Godot Asset Library <https://godotengine.org/asset-library/asset/4905>`_
   下载插件，或从
   `GitHub Releases <https://github.com/LuYingYiLong/Godot-FmodPlayer/releases>`_
   下载发布包。
#. 解压后，将 ``addons/fmod_player`` 复制到你的 Godot 项目：

   .. code-block:: text

      res://
      └── addons/
          └── fmod_player/
              ├── plugin.cfg
              ├── fmod_check.gd
              ├── fmod_player_main.gd
              └── bin/
                  ├── fmod_player.gdextension
                  ├── fmod_player.windows.template_debug.x86_64.dll
                  ├── fmod_player.windows.template_release.x86_64.dll
                  ├── libfmod_player.android.template_debug.arm64.so
                  └── libfmod_player.android.template_release.arm64.so

补齐 FMOD 运行库
~~~~~~~~~~~~~~~~

访问 `FMOD 下载页面 <https://www.fmod.com/download>`_，登录账户后下载
**FMOD Engine**。解压后，根据目标平台复制运行库。

.. list-table::
   :header-rows: 1

   * - 平台
     - 需要的文件
     - 放置位置
   * - Windows x86_64
     - ``fmod.dll``
     - ``res://addons/fmod_player/bin/``
   * - Android arm64
     - ``libfmod.so``、``fmod.jar``
     - 参见 :doc:`../export` 的 Android 导出配置

Windows 项目安装完成后，目录通常类似这样：

.. code-block:: text

   res://
   └── addons/
       └── fmod_player/
           └── bin/
               ├── fmod_player.gdextension
               ├── fmod.dll
               ├── fmod_player.windows.template_debug.x86_64.dll
               └── fmod_player.windows.template_release.x86_64.dll

.. note::

   编辑器插件会在启用时检查 ``fmod.dll``、``libfmod.so`` 或 ``libfmod.dylib``。
   如果没有找到 FMOD 运行库，Godot 会显示提示窗口，并引导你前往 FMOD 下载页面。

启用插件
~~~~~~~~

#. 打开 Godot 编辑器。
#. 进入 **项目 > 项目设置 > 插件**。
#. 找到 ``FMOD Player`` 并启用。
#. 如果刚刚复制了 FMOD 运行库，建议重启一次 Godot 编辑器。

验证安装
--------

启用成功后，可以用下面几项快速确认插件是否可用：

#. 在添加节点面板中搜索 ``Fmod``，应能看到：

   - ``FmodAudioStreamPlayer``
   - ``FmodAudioStreamPlayer2D``
   - ``FmodAudioStreamPlayer3D``

#. 在资源创建菜单中搜索 ``Fmod``，应能看到：

   - ``FmodAudioStream``
   - ``FmodAudioBusLayout``

#. 打开 Godot 输出面板，确认没有 FMOD 运行库缺失或 GDExtension 加载失败的错误。

如果节点或资源类型没有出现，通常是 FMOD 运行库缺失、平台架构不匹配，或
``addons/fmod_player`` 没有放在项目的 ``res://addons/`` 目录下。

从源码构建
----------

只有在需要修改 C++ 源码、调试 GDExtension，或自行生成平台二进制文件时，才需要从源码构建。

前置要求
~~~~~~~~

- Python 3.11 或更高版本
- SCons 4.10 或更高版本
- Git
- C++17 编译环境
- Windows 构建需要 MSVC
- Android 构建需要 Android SDK、NDK 与 JDK

获取源码
~~~~~~~~

.. code-block:: bash

   git clone --recursive https://github.com/LuYingYiLong/Godot-FmodPlayer.git
   cd Godot-FmodPlayer

Windows 构建
~~~~~~~~~~~~

.. code-block:: bash

   scons platform=windows target=template_debug arch=x86_64
   scons platform=windows target=template_release arch=x86_64

Android 构建
~~~~~~~~~~~~

.. code-block:: bash

   scons platform=android target=template_debug arch=arm64
   scons platform=android target=template_release arch=arm64

构建输出
~~~~~~~~

构建完成后，将生成的二进制文件放入 ``addons/fmod_player/bin/``。当前插件的
``fmod_player.gdextension`` 默认引用以下文件名：

.. code-block:: text

   addons/fmod_player/bin/
   ├── fmod_player.windows.template_debug.x86_64.dll
   ├── fmod_player.windows.template_release.x86_64.dll
   ├── libfmod_player.android.template_debug.arm64.so
   └── libfmod_player.android.template_release.arm64.so

如果你修改了输出文件名或目标平台，需要同步更新 ``bin/fmod_player.gdextension``。

构建选项
~~~~~~~~

.. list-table::
   :header-rows: 1

   * - 选项
     - 常用值
     - 说明
   * - ``platform``
     - ``windows``、 ``android``
     - 构建目标平台
   * - ``target``
     - ``template_debug``、 ``template_release``
     - 调试版或发布版
   * - ``arch``
     - ``x86_64``、 ``arm64``
     - 构建目标架构

FMOD 授权说明
-------------

Godot-FmodPlayer 使用 MIT 许可证；FMOD Engine 使用 Firelight Technologies Pty Ltd
的独立许可。发布、商业化或面向特定平台分发项目前，请阅读
`FMOD Licensing <https://www.fmod.com/licensing>`_ 与
`FMOD Legal Information <https://www.fmod.com/legal>`_。

下一步
------

安装完成后，请阅读 :doc:`quick_start` 播放第一段音频。

遇到问题时，可以查看 :ref:`常见问题 <faq>`，尤其是运行库缺失、导出后无声音和
平台架构不匹配相关条目。
