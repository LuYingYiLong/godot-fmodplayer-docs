Godot-FmodPlayer 文档
=====================

.. figure:: _static/banner.png
   :alt: Godot-FmodPlayer Banner
   :align: center
   :width: 100%

Godot-FmodPlayer 是一个 Godot 4 GDExtension 插件，基于 FMOD Core API 提供音频播放、
混音、DSP 效果、3D 音频和性能监控功能。

适合用于需要比 Godot 原生音频系统更细致控制的项目，例如动态混音、实时音效处理、
长音频流式播放、空间音频和 FMOD 底层 API 集成。

主要功能
--------

- 支持 MP3、WAV、OGG、FLAC、MOD、XM、S3M、IT、MIDI 等音频格式
- 支持流式加载、样本加载、内存加载和 Godot PCK 资源加载
- 提供 ``FmodAudioStreamPlayer``、``FmodAudioStreamPlayer2D`` 和 ``FmodAudioStreamPlayer3D`` 播放节点
- 支持通道、通道组、音频总线和实时混音控制
- 提供混响、EQ、滤波、延迟、失真、压缩、频谱分析等 DSP 效果
- 支持 FMOD CPU 与文件读取性能监控
- 提供编辑器导入器、音频预览和自定义资源类型

平台支持
--------

.. list-table::
   :header-rows: 1

   * - 平台
     - 架构
     - 状态
   * - Windows
     - x86_64
     - 支持
   * - Android
     - arm64
     - 支持

开始使用
--------

如果你是第一次使用，建议按下面顺序阅读：

#. :doc:`getting_started/installation`
#. :doc:`getting_started/quick_start`
#. :doc:`user_guide/audio_resources`
#. :doc:`user_guide/playback`
#. :doc:`user_guide/faq`

.. note::

   本插件使用 **FMOD Core API**，不是 FMOD Studio API。
   如果你的项目依赖 FMOD Studio Event、Bank 或 Studio 工作流，
   可以参考 `fmod-gdextension <https://github.com/utopia-rise/fmod-gdextension>`_。

.. important::

   Godot-FmodPlayer 插件本身使用 MIT 许可证。
   FMOD Engine 是 Firelight Technologies Pty Ltd 的专有音频引擎。
   商业项目请阅读 `FMOD Licensing <https://www.fmod.com/licensing>`_。

文档导航
--------

.. toctree::
   :maxdepth: 2
   :caption: 入门指南

   getting_started/installation
   getting_started/quick_start

.. toctree::
   :maxdepth: 2
   :caption: 用户指南

   user_guide/audio_resources
   user_guide/playback
   user_guide/mixer
   user_guide/dsp_effects
   user_guide/faq

.. toctree::
   :maxdepth: 2
   :caption: API 参考

   classes/index

.. toctree::
   :maxdepth: 2
   :caption: 贡献

   contributing/before_you_start
   contributing/development
   contributing/translation

.. toctree::
   :maxdepth: 1
   :caption: 其他

   glossary
   export

相关链接
--------

- `GitHub 仓库 <https://github.com/LuYingYiLong/Godot-FmodPlayer>`_
- `FMOD Core API 文档 <https://www.fmod.com/docs/2.03/api/core-api.html>`_
- :ref:`genindex`
- :ref:`search`