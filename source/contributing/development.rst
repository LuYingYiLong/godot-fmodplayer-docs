.. _contributing-development:

开发 Godot-FmodPlayer
==============================================

从插件仓库构建扩展，再把完整插件部署到测试项目。以下命令默认在插件仓库根目录执行，日常验证流程见 :doc:`testing`。

准备环境
----------------

- Godot 4.7.2 或更新版本、Git、Python 3 和 SCons。
- 支持 C++17 的编译器：Windows 使用 MSVC，Linux 使用 GCC 或 Clang；Android 使用 NDK 工具链。
- 目标平台的 FMOD Core SDK 2.04；头文件、链接库和运行库使用同一 SDK 发布版本。

只修改网站内容时，使用文档仓库的 Python 3.12 或更新版本环境即可，无需插件编译器和 FMOD SDK。

.. code-block:: sh

    git clone --recurse-submodules https://github.com/LuYingYiLong/Godot-FmodPlayer.git
    cd Godot-FmodPlayer
    python -m pip install scons

已有工作副本可运行 ``git submodule update --init --recursive``，恢复项目固定的 godot-cpp 提交。godot-cpp 10.x 的版本号与 Godot 独立；项目 ``SConstruct`` 默认使用 ``api_version=4.7``，扩展配置的最低 Godot 运行版本仍为 4.7.2。通常无需自行导出 API JSON，也不再依赖旧的 ``api/godot_4_7_2.json``。

Windows 可使用 Visual Studio 的“使用 C++ 的桌面开发”工作负载，并安装 Windows SDK。可打开仓库中的 ``Godot-FmodPlayer.slnx``，或使用其他编辑器后从命令行构建。

.. image:: ../_static/contributing/vs_install_cpp_package.png
   :align: center
   :alt: Visual Studio C++ workload

Windows
----------------------

将 Windows SDK 的 ``api/core/inc`` 复制到 ``src/thirdparty/fmod/inc``，将 ``api/core/lib/x64`` 中的文件复制到 ``src/thirdparty/fmod/lib/x64``。把其中的 ``fmod.dll`` 放入 ``addons/fmod_player/bin``。

.. code-block:: sh

    scons platform=windows target=template_debug arch=x86_64 copy_to_tests=yes
    scons platform=windows target=template_release arch=x86_64

``template_debug`` 用于编辑器和调试运行，``template_release`` 用于发布导出。输出文件位于 ``addons/fmod_player/bin``；对应文件名与架构必须匹配 ``fmod_player.gdextension``。

Linux
------------------

使用 FMOD Linux Core SDK。在 Git 忽略的根目录 ``custom.py`` 中指定 SDK 根目录或其 ``api/core`` 目录：

.. code-block:: python

    fmod_linux_sdk = "/path/to/fmodstudioapi20400linux"

.. code-block:: sh

    scons platform=linux target=template_debug arch=x86_64 copy_to_tests=yes
    scons platform=linux target=template_release arch=x86_64

也可通过 ``FMOD_LINUX_SDK`` 环境变量配置路径。Debug 运行需要 ``libfmodL.so.15``，Release 需要 ``libfmod.so.15``；放在扩展库旁，保留正确的文件名或符号链接。构建时 ``copy_to_tests=yes`` 会从本地 SDK 复制对应运行库。

Android
----------------------

安装 Android SDK、NDK 和 FMOD Android Core SDK。``ANDROID_HOME`` 指向 SDK 根目录；NDK 位于其 ``ndk/<版本号>`` 子目录。已设置正确的 ``ANDROID_HOME`` 时，通常只需在项目的 ``custom.py`` 中固定已安装的 ``ndk_version``。

下面的路径和版本号仅为示例，请替换为本机实际值：

.. code-block:: python

    ANDROID_HOME = r"C:\Android\Sdk"
    ndk_version = "30.0.16248370"
    fmod_android_sdk = r"C:\SDKs\FMOD-Android"

``fmod_android_sdk`` 接受 SDK 根目录或 ``api/core``，也可通过 ``FMOD_ANDROID_SDK`` 环境变量提供默认路径。固定并保留已验证的 NDK，可避免 godot-cpp 默认 NDK 版本变化影响本项目。

.. code-block:: sh

    scons platform=android target=template_debug arch=arm64
    scons platform=android target=template_release arch=arm64

构建产物和 FMOD 运行库必须使用相同 ABI。其他架构使用 ``arch`` 选择，并检查扩展配置中的库条目。Java 与原生运行库的导出配置见 :doc:`../export`。

同步到测试项目
----------------------

``copy_to_tests=yes`` 在构建成功后同步完整插件到 ``tests/addons/fmod_player``，即使二进制无需重编译，也会复制修改过的脚本、翻译和资源。Windows 和 Linux 同时复制本地 SDK 运行库；可用 ``fmod_runtime=/path/to/runtime`` 覆盖其来源。

替换原生库前先关闭测试项目，完成构建后重新打开 ``tests/project.godot`` 并按 F5。无需另行运行外部测试脚本，菜单和编辑器检查步骤见 :doc:`testing`。

代码风格与接口变更
--------------------------

- C++ 沿用当前文件的命名、缩进和指针引用写法，避免无关格式化。新增或修改 API 时，同时更新注册、XML、翻译和受影响示例。
- GDScript 使用 UTF-8、LF、Tab 缩进和完整类型提示；函数与类定义前后留两个空行。
- 多行数组、字典和枚举保留末尾逗号；信号使用英文过去时名称；硬编码资源路径优先使用 UID。
- 浮点数保留前导和后缀零，例如 ``0.0``；变量不重复声明默认值；中文注释末尾不加句号。
- 先声明信号和属性，再写方法；公共成员在前，私有成员在后；先初始化与虚函数回调，再写类接口。
- DSP 改动说明线程归属和缓冲区单位，区分字节、采样和完整音频帧；音频回调中减少分配与锁竞争，遵守 Godot 对象和脚本回调的线程约束。

构建与加载排查
----------------------

- 找不到 NDK：确认 ``ANDROID_HOME`` 是 SDK 根目录，且 ``ndk_version`` 与本机安装目录一致。
- 提示旧 API JSON 文件不存在：检查本地配置是否仍设置 ``custom_api_file``。显式设置会覆盖 ``api_version``，普通构建可使用项目内置的 API 配置。
- 动态库加载失败：检查平台、架构、Debug/Release 条目和 FMOD 运行库，查看 Godot 输出面板，参见 :ref:`faq-module-no-found`。
