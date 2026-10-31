导出说明
================

导出项目需同时包含完整插件、目标平台的 GDExtension 二进制、FMOD 运行库和音频资源。环境要求为 Godot 4.7.2 或更新版本及匹配的 FMOD Core SDK 2.04；安装步骤见 :doc:`getting_started/installation`。

导出前检查
------------------

当前提供 Windows x86_64、Linux x86_64 和 Android arm64 配置。其他 Android ABI 可自行构建；macOS / iOS 为实验性支持，需自行配置 SDK、链接项与扩展库条目。平台状态见 :ref:`platform-support`。

复制完整的 ``addons/fmod_player``，保留 ``fmod_check.gd``、``fmod_player_main.gd``、导入器、翻译、图标及原生库。扩展配置的版本、库名和依赖应与当前插件一致：

.. code-block:: ini

    [configuration]
    entry_symbol = "fmod_player_init"
    compatibility_minimum = "4.7.2"
    reloadable = false

    [libraries]
    windows.debug.x86_64 = "fmod_player.windows.template_debug.x86_64.dll"
    windows.release.x86_64 = "fmod_player.windows.template_release.x86_64.dll"
    linux.debug.x86_64 = "libfmod_player.linux.template_debug.x86_64.so"
    linux.release.x86_64 = "libfmod_player.linux.template_release.x86_64.so"
    android.debug.arm64 = "libfmod_player.android.template_debug.arm64.so"
    android.release.arm64 = "libfmod_player.android.template_release.arm64.so"

    [dependencies]
    windows.debug.x86_64 = { "fmod.dll" : "" }
    windows.release.x86_64 = { "fmod.dll" : "" }
    linux.debug.x86_64 = { "libfmodL.so.15" : "" }
    linux.release.x86_64 = { "libfmod.so.15" : "" }

``template_debug`` 对应编辑器和调试导出，``template_release`` 对应发布导出。当前插件关闭原生库热重载，替换库文件前关闭使用它的 Godot 项目，再重新打开。

资源与导出预设
----------------------

- 在 **项目 > 导出** 中选择目标平台，并确认其架构与扩展及 FMOD 运行库一致。
- 使用资源引用保存已导入音频。通过 FileAccess 动态读取原始文件时，将文件加入导出规则。
- 仅导出选定场景时，在资源包含过滤器中加入 ``*.gdextension``，使 Godot 的原生扩展导出器处理扩展和依赖。
- 独立 FMOD 总线的默认布局及其资源依赖由插件的导出集成包含。布局设置与保存方式见 :doc:`user_guide/mixer`。

Windows 导出
----------------------------

Windows x86_64 的 Debug 和 Release 均使用 ``fmod.dll``。把 Windows SDK 的运行库放在 ``addons/fmod_player/bin``，并保留当前目标的扩展 DLL。发布导出选择 ``fmod_player.windows.template_release.x86_64.dll``。

先导出到空目录，再运行导出的可执行文件，确认无 GDExtension 或 FMOD 依赖加载错误，并测试播放和停止。

Linux 导出
------------------------

.. list-table::
   :header-rows: 1

   * - 导出类型
     - 扩展库
     - FMOD 依赖
   * - Debug
     - ``libfmod_player.linux.template_debug.x86_64.so``
     - ``libfmodL.so.15``
   * - Release
     - ``libfmod_player.linux.template_release.x86_64.so``
     - ``libfmod.so.15``

使用 FMOD Linux Core SDK 的对应运行库，放在扩展库旁。保留版本化共享库及其符号链接，或把链接目标复制为上表中的文件名。扩展通过 ``$ORIGIN`` 查找同目录运行库；复制导出结果时保留原生库目录结构。

Linux x86_64 已在 Ubuntu 26.04 测试。仍需在目标发行版运行导出项目，检查系统依赖、播放、总线路由及效果器。

Android 导出
----------------------------

Android 需要匹配 ABI 的插件库、FMOD 原生运行库和 ``fmod.jar``。本页使用 ``arm64-v8a``；Debug/dev 使用 ``libfmodL.so``，Release 使用 ``libfmod.so``。

使用配置工具
~~~~~~~~~~~~~~~~~~~~

先通过 **项目 > 安装 Android 构建模板** 安装与当前 Godot 版本匹配的模板。工具要求项目中已经存在 ``android/build``，不会自动安装模板。

.. image:: _static/install_android_template.png
   :align: center

- 打开 **项目 > 工具 > Configure FMOD Android Export**，选择 FMOD Android SDK 目录，或下载的 ``.tar.gz`` / ``.tgz`` 包。
- 点击 **Review Changes**，核对运行库复制位置及 ``gradle.properties``、``build.gradle`` 和 ``GodotApp.java`` 的修改。
- 点击 **Apply Changes** 应用修改。工具会加入 ``fmod.jar`` 依赖，并让 Debug/dev 加载 ``fmodL``、Release 加载 ``fmod``，在 Godot 启动前完成加载。

工具仅复制已有的 arm64 插件二进制，不会编译缺失的扩展库。查看完成报告中的跳过或失败项目；更换二进制后需重新同步到构建模板。已有自定义 Gradle 或 Java 修改时，也应先复核变更内容。

手动维护自定义模板
~~~~~~~~~~~~~~~~~~~~~~~~~~

如果自行维护构建模板，需保留以下对应关系。FMOD 文件取自同一 Android SDK，插件库来自相应的 SCons 构建目标：

.. code-block:: text

    android/build/libs/
    ├── fmod.jar
    ├── debug/arm64-v8a/
    │   ├── libfmodL.so
    │   └── libfmod_player.android.template_debug.arm64.so
    ├── dev/arm64-v8a/
    │   ├── libfmodL.so
    │   └── libfmod_player.android.template_debug.arm64.so
    └── release/arm64-v8a/
        ├── libfmod.so
        └── libfmod_player.android.template_release.arm64.so

在 ``android/build/build.gradle`` 的 ``dependencies`` 中加入：

.. code-block:: groovy

    implementation files("libs/fmod.jar")

在 ``GodotApp.java`` 的 ``onCreate`` 中、``super.onCreate`` 之前按构建类型加载对应运行库，与配置工具的行为一致：

.. code-block:: java

    @Override
    public void onCreate(Bundle savedInstanceState) {
        if (BuildConfig.DEBUG) {
            System.loadLibrary("fmodL");
        } else {
            System.loadLibrary("fmod");
        }
        super.onCreate(savedInstanceState);
    }

其他 ABI 需要自行构建对应插件库，检查 ``fmod_player.gdextension``、模板目录与导出预设三者一致。不要把 Windows 或 Linux SDK 的运行库复制到 Android 模板。

.. _set-android-export:

导出设置
~~~~~~~~~~~~~~~~

- 在 Android 导出预设中选择 ``arm64-v8a`` 并启用 Gradle 构建。
- 导出 APK 或 AAB，在真机检查启动、播放、停止、总线效果和空间音频。

.. image:: _static/use_gradle_build.png
   :align: center

源码构建发布库
----------------------

修改 C++ 后，在插件仓库中为目标平台构建发布库。SDK 路径和 Android NDK 版本配置见 :doc:`contributing/development`。

.. code-block:: sh

    scons platform=windows target=template_release arch=x86_64
    scons platform=linux target=template_release arch=x86_64
    scons platform=android target=template_release arch=arm64

构建直接输出到插件仓库的 ``addons/fmod_player/bin``。将完整插件更新到实际游戏项目；Android 还需更新构建模板内已复制的扩展库。

验证与排错
------------------

发布前先按 :doc:`contributing/testing` 打开测试项目、按 F5 试听并运行 8 项数值回归。然后在实际目标设备上验证导出结果，不能用编辑器测试代替平台导出验证。

- 加载失败：确认 Godot 不低于 4.7.2，扩展库与 FMOD 运行库的版本、架构和 Debug/Release 目标匹配。
- Linux 找不到运行库：检查扩展旁的 ``libfmodL.so.15`` 或 ``libfmod.so.15``，以及符号链接目标和系统依赖。
- Android 启动崩溃：检查 APK/AAB 的 ABI、Debug/dev 的 ``libfmodL.so`` 或 Release 的 ``libfmod.so``、``fmod.jar`` 及 Java 加载分支，并查看 Logcat。
- 只有导出后无声：检查音频资源、原始文件过滤和独立总线默认布局是否包含，参见 :ref:`faq-export-audio-missing`。

许可与署名
------------------

插件使用 MIT 许可证，FMOD 单独授权。发布前阅读 `FMOD Licensing <https://www.fmod.com/licensing>`_、`FMOD Legal Information <https://www.fmod.com/legal>`_ 和 `FMOD Attribution <https://www.fmod.com/attribution>`_，以官方当前条款为准。
