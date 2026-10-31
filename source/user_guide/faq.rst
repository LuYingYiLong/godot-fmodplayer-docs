.. _faq:

常见问题
============

安装与运行库
----------------

.. _faq-version-requirements:

版本要求与构建目标
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

当前插件要求 Godot 4.7.2 或更新版本及匹配的 FMOD Core SDK 2.04。``api_version=4.7`` 选择用于生成绑定的 Godot API；``fmod_player.gdextension`` 中的 ``compatibility_minimum=4.7.2`` 声明最低运行版本，两者用途不同。构建配置见 :doc:`../contributing/development`。

.. _faq-module-no-found:

加载时提示找不到模块
~~~~~~~~~~~~~~~~~~~~~~~~

查看输出面板中第一条动态库加载错误，检查：

- 完整插件位于 ``res://addons/fmod_player/``。
- ``fmod_player.gdextension`` 指定的扩展和 FMOD 依赖均存在于 bin 目录。
- 架构、Debug/Release 类型和 FMOD 版本匹配。
- 复制运行库后已重新启动编辑器。

各平台文件名见 :doc:`../getting_started/installation`，导出配置见 :doc:`../export`。

播放与资源
--------------

.. _faq-no-sound:

播放时没有声音
~~~~~~~~~~~~~~~~~~

#. 确认音频重新导入为 FMOD Audio，且播放器的 Stream 有效。
#. 检查 ``stream_paused``、``volume_db`` 和总线 Mute/Solo 状态。分贝音量 ``0.0`` 表示单位增益。
#. 空间音频检查当前相机、声源距离和衰减设置。
#. 查看输出面板中的文件、解码和 FMOD 错误。

.. _faq-stream-vs-sample:

首次播放延迟或音乐内存占用高
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

短音效使用 Sample 并提前 ``preload()``；长音频可使用 Stream 减少完整解码样本的开销。FmodAudioStream 仍保留文件字节，两种模式的内存区别见 :doc:`audio_resources`。

.. _faq-release-audio-resources:

何时释放资源和临时播放器
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

自然播放结束可通过 ``finished`` 回收临时节点，手动停止需自行回收。播放期间保留音频资源和 Sound 的所有者引用，停止所有使用者后再清理。服务器创建的总线和槽位实例由服务器管理，详见 :doc:`playback` 与 :doc:`mixer`。

总线与效果器
----------------

.. _faq-bus-panel-empty:

FMOD Audio 只显示同步提示
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``audio/fmod/sync_godot_audio_buses`` 默认为 true，此模式在原生 Audio 面板编辑。需要独立 FMOD 布局时关闭该设置并重新加载项目，再打开 FMOD Audio。

.. _faq-editor-meter:

运行游戏后看不到 FMOD 电平
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FMOD Audio 当前显示编辑器内试听电平。F5/F6 启动的独立游戏进程尚未接入远程电平。独立模式下，可展开 Stream 子检查器试听并在 FMOD Audio 中查看 Master。

.. _faq-dsp-not-working:

效果或实时数据没有变化
~~~~~~~~~~~~~~~~~~~~~~~~~~

检查声音经过的总线、槽位启用状态、总线旁路和效果顺序。通过布局添加 Capture、SpectrumAnalyzer 或 Record 后，从 ``FmodServer.get_bus_effect_instance()`` 获取运行实例；读取配置资源得不到槽位的实时数据。示例见 :doc:`dsp_effects`。

.. _faq-native-audio-mix:

能否与原生 AudioStreamPlayer 混用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

可以，两套系统分别管理播放、音量和 DSP。总线同步转换配置，不会将原生音频信号送入 FMOD，或将 FMOD 信号送入 Godot 总线。

导出与性能
--------------

.. _faq-export-audio-missing:

编辑器可播放，导出后失败
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

检查目标架构和 Release 运行库、资源导出过滤以及动态读取的原始文件。项目内已导入资源使用资源引用，独立总线默认布局由导出插件包含；完整步骤见 :doc:`../export`。

.. _faq-mobile-platforms:

移动设备上卡顿或延迟较高
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

预加载高频短音效，限制同时播放数量，检查 DSP CPU 和流式解码开销。在目标设备上使用同一段音频和相同通道数比较；模拟器和编辑器的结果用于辅助排查。

.. _faq-crash-debugging:

如何报告错误或崩溃
~~~~~~~~~~~~~~~~~~~~~~

保留完整日志、Godot/FMOD/插件版本、平台架构及最小复现场景，说明是否仅在导出版本出现。可在 `GitHub Issues <https://github.com/LuYingYiLong/Godot-FmodPlayer/issues>`_ 提交；日志中附上首次错误及复现步骤。

源码构建与测试
----------------------

.. _faq-build-configuration:

找不到旧 API 文件或 NDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

普通构建使用内置 ``api_version=4.7``。若仍提示旧 JSON 路径不存在，检查 ``custom.py`` 或命令行是否设置了 ``custom_api_file``；它会覆盖内置 API 选择。Android 构建确认 ``ANDROID_HOME`` 指向 SDK，并在 ``custom.py`` 中固定本机已安装的 ``ndk_version``，参见 :doc:`../contributing/development`。

.. _faq-testing-entry:

如何运行测试
~~~~~~~~~~~~~~~~~~~~

构建时使用 ``copy_to_tests=yes`` 同步完整插件，随后在 Godot 中打开 ``tests/project.godot``，按 F5 进入试听场景或点击“运行数值回归（8 项）”。效果器、总线和翻译直接在编辑器中检查；无需运行已移除的 PowerShell、Shell 或 Python 测试脚本，完整流程见 :doc:`../contributing/testing`。

接口与许可
--------------

.. _faq-fmod-studio-bank:

是否支持 Studio Event 和 Bank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

插件封装 FMOD Core API，提供音频文件播放、通道、DSP、总线和空间音频。当前接口没有提供 FMOD Studio Event 和 Bank 工作流。

.. _faq-plugin-license:

插件和 FMOD 分别使用什么许可
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

插件使用 `MIT 许可证 <https://opensource.org/license/MIT>`_。FMOD Engine 的许可与项目注册信息请查阅 `FMOD Licensing <https://www.fmod.com/licensing>`_ 和 `FMOD Legal Information <https://www.fmod.com/legal>`_。
