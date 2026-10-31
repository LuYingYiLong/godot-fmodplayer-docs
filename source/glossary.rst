术语表
======

本页整理使用 Godot-FmodPlayer 时常见的 FMOD 与音频术语。内容参考
`FMOD API Glossary <https://www.fmod.com/docs/2.04/api/glossary.html>`_，
并根据 Godot 引擎、FMOD Core API 与 Godot-FmodPlayer 的实际用法重新说明。

.. important::

   本页不是 FMOD 官方文档的中文翻译，也不替代 FMOD 官方许可、API 文档或技术支持。
   FMOD、FMOD Engine 等名称归 Firelight Technologies Pty Ltd 所有。发布项目时请以
   `FMOD Legal Information <https://www.fmod.com/legal>`_ 与
   `FMOD Licensing <https://www.fmod.com/licensing>`_ 为准。

.. _Glossary-2dvs3d:

2D 与 3D
--------

2D 声音不会参与空间定位。它通常适合 UI 音效、背景音乐、旁白、菜单音效等不需要跟随场景位置变化的声音。
在 Godot-FmodPlayer 中，:ref:`FmodAudioStreamPlayer<class_FmodAudioStreamPlayer>` 默认更接近 2D 播放用法。

3D 声音会根据声源和监听器之间的位置关系计算音量、声像、距离衰减、遮挡和多普勒效果。
在 Godot-FmodPlayer 中，:ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>` 会把 Godot 节点的全局位置同步到 FMOD 通道，
适合脚步、武器、环境物件、车辆、怪物叫声等来自世界空间的声音。

.. note::

   :ref:`FmodChannelControl.set_3d_level()<class_FmodChannelControl_method_set_3d_level>` 可以调整 3D 混合比例。
   这在需要让一个声音部分保持空间感、部分保持稳定声像时很有用。

.. _glossary-audio-asset:

音频资产
--------

音频资产是项目中可播放的声音数据。它可以是 ``wav``、``ogg``、``mp3``、``flac`` 等独立音频文件，
也可以是运行时已经能够读取的其他 FMOD 支持格式。

在 Godot-FmodPlayer 中，常见做法是把音频文件导入为 :ref:`FmodAudioStream<class_FmodAudioStream>`，
再交给 :ref:`FmodAudioStreamPlayer<class_FmodAudioStreamPlayer>`、:ref:`FmodAudioStreamPlayer2D<class_FmodAudioStreamPlayer2D>`
或 :ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>` 播放。

.. _glossary-audio-channel:

音频通道
--------

音频通道可以指两种不同概念，需要区分：

- **声道**：音频信号里的扬声器通道，例如单声道、左声道、右声道、5.1 环绕声中的多个输出通道。
- **FMOD Channel**：FMOD 中的一次声音播放实例，对应 Godot-FmodPlayer 的 :ref:`FmodChannel<class_FmodChannel>`。

例如，一个立体声音效文件有两个声道；当它被播放一次时，FMOD 会为这次播放创建或分配一个 Channel。
同一个声音同时播放三次，就可能对应三个不同的 :ref:`FmodChannel<class_FmodChannel>`。

.. _glossary-bus:

Bus
---

Bus 即音频总线，用来把一组声音集中到同一个混音路径上。常见总线包括 ``Music``、``SFX``、``Voice`` 和 ``Ambient``。

默认开启 ``audio/fmod/sync_godot_audio_buses``，将 Godot 的 `AudioServer`_ 配置同步到 FMOD。关闭同步并重新加载项目后，可在 FMOD Audio 面板中编辑独立的 :ref:`FmodAudioBusLayout<class_FmodAudioBusLayout>`。:ref:`FmodAudioBus<class_FmodAudioBus>` 和 :ref:`FmodChannelGroup<class_FmodChannelGroup>` 管理实际混音，详见 :ref:`混音系统<mixer>`。

.. _glossary-channel:

Channel
-------

Channel 是 FMOD 中一次正在播放或由虚拟语音系统托管的声音实例。它可以控制音量、暂停、音高、循环点、播放位置、
3D 属性、DSP 链和回调。

在 Godot-FmodPlayer 中，播放节点内部会维护一个 :ref:`FmodChannel<class_FmodChannel>`。
如果需要更细的控制，可以取得当前播放通道，再调用 :ref:`FmodChannelControl<class_FmodChannelControl>`
或 :ref:`FmodChannel<class_FmodChannel>` 的方法。

.. _glossary-channelgroup:

ChannelGroup
------------

ChannelGroup 是多个 Channel 或子 ChannelGroup 的混音容器。它适合做分组控制，例如同时降低所有音乐音量、
暂停一组环境声，或给整个 ``SFX`` 总线添加一个滤波器。

在 Godot-FmodPlayer 中，:ref:`FmodChannelGroup<class_FmodChannelGroup>` 通常由总线系统创建和管理。
普通项目优先通过 :doc:`user_guide/mixer` 中的总线接口操作；只有在需要底层控制时才直接访问 ChannelGroup。

.. _glossary-channelcontrol:

ChannelControl
--------------

ChannelControl 是 Channel 和 ChannelGroup 共享的一组控制能力。它包含音量、静音、暂停、音高、3D 属性、声像矩阵、
DSP 插入、淡变点和回调等接口。

Godot-FmodPlayer 中的 :ref:`FmodChannel<class_FmodChannel>` 与 :ref:`FmodChannelGroup<class_FmodChannelGroup>`
都继承自 :ref:`FmodChannelControl<class_FmodChannelControl>`。因此，很多播放控制方法既能用于单个声音，也能用于一整组声音。

.. _glossary-dsp:

DSP
---

DSP 是 Digital Signal Processing 的缩写，表示数字信号处理单元。混响、均衡器、滤波器、延迟、失真、压缩器、
频谱分析器等都可以作为 DSP 参与音频处理。

在 Godot-FmodPlayer 中，:ref:`FmodDSP<class_FmodDSP>` 可以添加到某个 Channel、ChannelGroup 或总线相关的混音路径上。
如果多个声音需要同一种效果，通常把 DSP 放在对应总线上更容易维护，也比给每个声音单独创建效果更省资源。

.. _glossary-dsp-chain:

DSP 链
------

DSP 链是多个 DSP 按顺序连接形成的处理路径。声音进入链后，会依次经过这些处理单元。
不同顺序会产生不同结果，例如先失真再混响，和先混响再失真，听感通常不同。

.. image:: _static/dsp_chain.png

在 Godot-FmodPlayer 中，可以通过 :ref:`FmodChannelControl.add_dsp()<class_FmodChannelControl_method_add_dsp>`、
:ref:`FmodChannelControl.remove_dsp()<class_FmodChannelControl_method_remove_dsp>` 和
:ref:`FmodChannelControl.set_dsp_index()<class_FmodChannelControl_method_set_dsp_index>` 调整 DSP 链。

.. _glossary-dsp-clock:

DSP Clock
---------

DSP Clock 是 FMOD 混音器使用的样本级时间计数。它常用于精确调度播放、延迟启动、淡入淡出或和其他声音对齐。

在 Godot-FmodPlayer 中，:ref:`FmodChannelControl.get_dsp_clock()<class_FmodChannelControl_method_get_dsp_clock>`、
:ref:`FmodChannelControl.set_delay()<class_FmodChannelControl_method_set_delay>` 和淡变点接口可以用于需要样本级同步的场景。
普通按钮音效和环境声通常不需要直接处理 DSP Clock。

.. _glossary-listener:

Listener
--------

Listener 即监听器，表示玩家“听见世界”的位置和朝向。3D 声音会根据监听器与声源之间的距离、方向和相对速度计算结果。

当前插件在游戏中读取视口的 Camera3D 或 Camera2D 作为监听来源，3D 编辑器试听使用编辑器相机。原生 ``AudioListener3D`` 不会自动接管 FMOD 监听器。使用 :ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>` 时，检查活动相机、声源变换和距离设置。

.. _glossary-sound:

Sound
-----

Sound 是 FMOD 对音频数据的运行时表示。它通常由文件、内存数据或流式数据创建，然后通过 System 播放为 Channel。

在 Godot-FmodPlayer 中，:ref:`FmodAudioStream<class_FmodAudioStream>` 会在需要时创建底层 :ref:`FmodSound<class_FmodSound>`。
这让资源可以先作为 Godot 资源存在，真正播放或查询底层对象时再交给 FMOD 创建声音。

.. _glossary-stream-sample:

Stream 与 Sample
----------------

Stream 表示边读取边解码的播放方式，适合音乐、长旁白、长环境声等体积较大的音频。
Sample 表示把音频数据加载到内存后播放，适合短音效、频繁触发的 UI 声和需要低延迟响应的声音。

在 Godot-FmodPlayer 中，可以通过 :ref:`FmodAudioStream<class_FmodAudioStream>` 的创建模式选择更适合的加载方式。
一般来说，长音频优先使用流式播放，短音效优先使用样本加载。

.. _glossary-virtual-channel:

Virtual Channel
---------------

Virtual Channel 即虚拟通道。当同时播放的声音很多时，FMOD 可以让听不见或优先级较低的声音进入虚拟状态。
虚拟通道仍然保留播放时间和状态，但不一定消耗完整的混音资源。

在 Godot-FmodPlayer 中，可以通过 :ref:`FmodChannel.is_virtual()<class_FmodChannel_method_is_virtual>` 查询某个通道是否处于虚拟状态。
这对调试大量环境声、粒子音效或开放世界场景中的声音预算很有帮助。

.. _glossary-rolloff:

Rolloff
-------

Rolloff 表示 3D 声音随距离变远而衰减的曲线。不同曲线会影响声音从近处到远处的听感变化。

3D 播放节点通过 ``unit_size`` 缩放距离，``max_distance`` 是其倍数，并非通用的硬截止距离；衰减曲线由 ``attenuation_model`` 选择。低层 :ref:`FmodChannelControl<class_FmodChannelControl>` 则提供 ``set_3d_min_max_distance()`` 和自定义衰减曲线接口。先确认所用层级及其距离单位，再调整衰减行为。

.. _glossary-doppler:

Doppler
-------

Doppler 即多普勒效果。当声源和监听器之间存在相对速度时，音高会发生变化。
快速掠过的车辆、飞行物或高速移动的物体可以使用该效果增强速度感。

在 Godot-FmodPlayer 中，:ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>` 会同步位置和速度相关信息。
如果效果过强或不符合游戏风格，可以通过多普勒相关设置降低影响。

.. _glossary-occlusion:

Occlusion
---------

Occlusion 即遮挡。它描述墙体、地形或其他几何体阻挡声音传播后，音量和高频内容被削弱的效果。

Godot-FmodPlayer 提供 :ref:`FmodGeometryInstance3D<class_FmodGeometryInstance3D>`，可以把场景几何体注册到 FMOD Geometry 系统。
适合需要门后声音、墙后声音、房间隔音等空间表现的项目。

.. _glossary-pan-mix-matrix:

Pan 与 Mix Matrix
-----------------

Pan 即声像，通常用于控制声音在左右声道或环绕声场中的位置。Mix Matrix 则是更底层的输入到输出声道矩阵，
可以精确控制每个输入声道如何分配到输出声道。

在 Godot-FmodPlayer 中，简单左右声像可以使用 :ref:`FmodChannelControl.set_pan()<class_FmodChannelControl_method_set_pan>`。
如果需要多声道或特殊路由，可以使用 :ref:`FmodChannelControl.set_mix_matrix()<class_FmodChannelControl_method_set_mix_matrix>`。

.. _glossary-mix-matrix:

Mix Matrix
----------

Mix Matrix 即混音矩阵，用来控制 **输入声道** 如何分配到 **输出声道**。
可以把它理解成一张权重表：每一列是一个输入声道，每一行是一个输出声道，表格中的数值表示
“这个输入声道有多少信号送到这个输出声道”。

以一个立体声输入原样送到立体声输出为例：

.. figure:: _static/mix_matrix/stereo_identity.svg
   :alt: 立体声输入原样输出到立体声输出的混音矩阵
   :align: center
   :width: 100%

这个矩阵表示左声道只进左扬声器，右声道只进右扬声器。用更直观的形式写就是：

.. code-block:: text

    输出 L = 输入 L * 1.0 + 输入 R * 0.0
    输出 R = 输入 L * 0.0 + 输入 R * 1.0

在 Godot-FmodPlayer 中，:ref:`FmodChannelControl.set_mix_matrix()<class_FmodChannelControl_method_set_mix_matrix>` 接收一个
``PackedFloat32Array``，并指定输出声道数、输入声道数和输入声道步长。
矩阵按“输出行优先”的方式书写：先写输出 0 接收各输入的权重，再写输出 1，以此类推。

下面示例把立体声左右声道对调：

.. code-block:: gdscript

    func swap_stereo(channel: FmodChannel) -> void:
        var matrix := PackedFloat32Array([
            0.0, 1.0, # Out L = In R
            1.0, 0.0, # Out R = In L
        ])

        channel.set_mix_matrix(matrix, 2, 2)

如果只是想调整单个播放实例的左右位置，优先使用
:ref:`FmodChannelControl.set_pan()<class_FmodChannelControl_method_set_pan>`。
Mix Matrix 更适合处理多声道格式转换、特殊声道路由、左右声道互换、单声道偏置和调试音频资产等场景。

.. _glossary-upmix:

Upmix
-----

Upmix 即上混，是把较少的输入声道分配到更多输出声道。例如把单声道音效送到立体声输出，
或者把立体声音乐送到 5.1 输出。

最常见的单声道到立体声上混，是把同一份单声道信号同时送到左右声道。听感上它会位于正中间。
如果希望这个单声道声音偏左，可以降低右声道电平：

.. figure:: _static/mix_matrix/mono_upmix_left_bias.svg
   :alt: 单声道上混到偏左立体声输出的混音矩阵
   :align: center
   :width: 80%

对应代码可以写成：

.. code-block:: gdscript

    func mono_to_left_biased_stereo(channel: FmodChannel) -> void:
        var matrix := PackedFloat32Array([
            1.0,  # Out L = Mono * 1.0
            0.35, # Out R = Mono * 0.35
        ])

        channel.set_mix_matrix(matrix, 2, 1)

在 Godot-FmodPlayer 中，简单左右声像通常直接用
:ref:`FmodChannelControl.set_pan()<class_FmodChannelControl_method_set_pan>` 更方便。
只有在需要精确控制多声道分配时，才需要手动设置混音矩阵。

.. _glossary-downmix:

Downmix
-------

Downmix 即下混，是把较多的输入声道折叠到较少输出声道。例如把立体声转为单声道，
或者把 5.1 输出到立体声设备。

一个常见的立体声到单声道下混矩阵如下：

.. figure:: _static/mix_matrix/stereo_downmix_mono.svg
   :alt: 立体声下混到单声道的混音矩阵
   :align: center
   :width: 80%

这表示左右声道各取一半相加：

.. code-block:: text

    输出 Mono = 输入 L * 0.5 + 输入 R * 0.5

不要简单使用 ``1.0 + 1.0`` 做下混。两个满电平信号直接相加可能让输出超过正常范围，
造成削波或听感上的突然变大。实际项目里可以从 ``0.5``、``0.707`` 或更保守的值开始，
再根据素材响度和目标平台调整。

代码示例：

.. code-block:: gdscript

    func stereo_to_mono(channel: FmodChannel) -> void:
        var matrix := PackedFloat32Array([
            0.5, 0.5, # Out Mono = In L * 0.5 + In R * 0.5
        ])

        channel.set_mix_matrix(matrix, 1, 2)

5.1 到立体声的简化示例
~~~~~~~~~~~~~~~~~~~~~~

5.1 声道通常可以按以下顺序理解：

.. code-block:: text

    Front Left, Front Right, Center, LFE, Surround Left, Surround Right

一个简化的 5.1 到立体声下混矩阵可以写成：

.. figure:: _static/mix_matrix/surround_downmix_stereo.svg
   :alt: 5.1 声道下混到立体声的混音矩阵
   :align: center
   :width: 100%

这里的思路是：

- 左前和右前分别进入对应的左右输出。
- 中置声道同时进入左右输出，并降低到 ``0.707``，避免居中内容过响。
- 左环绕进入左输出，右环绕进入右输出，也适当降低。
- LFE 是低频效果声道，不一定适合直接混入普通立体声输出，是否加入要看项目需求。

.. warning::

   多声道下混没有唯一正确答案。不同平台、设备、耳机虚拟环绕、影院标准和游戏风格可能需要不同矩阵。
   对关键内容做下混时，必须用实际目标设备听测。

.. _glossary-callback:

Callback
--------

Callback 即回调。FMOD 会在特定事件发生时通知用户代码，例如声音结束、通道状态变化或某些底层系统事件。

在 Godot-FmodPlayer 中，ChannelControl 级别回调会通过 ``callback_received`` 信号转发到 Godot。
每个 System、ChannelControl 或 DSP 通常只维护一个回调入口，因此注册回调时应根据回调类型区分处理逻辑。

.. _glossary-system:

System
------

System 是 FMOD Core API 的核心对象，负责初始化音频设备、创建 Sound、播放声音、管理 Channel、更新混音系统、
获取性能数据和处理录音等底层功能。

在 Godot-FmodPlayer 中，通常不需要手动创建 System。插件会通过 :ref:`FmodServer<class_FmodServer>` 初始化并维护主系统。
高级用法可以从 :ref:`FmodServer.get_main_system()<class_FmodServer_method_get_main_system>` 获取 :ref:`FmodSystem<class_FmodSystem>`。

.. _glossary-bank-event:

Bank 与 Event
-------------

Bank 和 Event 常见于 FMOD 的 Studio 工作流。Godot-FmodPlayer 主要面向 **FMOD Core API**，
重点是音频文件播放、通道控制、DSP 效果、混音总线、3D 音频和性能监控。

因此，在本插件文档中看到 ``Bank`` 或 ``Event`` 时，通常只是为了帮助理解 FMOD 生态中的相关概念。
如果项目需要完整的 FMOD Studio Event、Bank 构建、参数自动化和音频设计师工作流，
应选择专门的 FMOD Studio 集成方案，而不是把 Godot-FmodPlayer 当作完整 Studio 集成使用。

.. _glossary-fsb:

FSB
---

FSB 是 FMOD Sample Bank 的缩写，是一种打包采样数据的格式。它和 Studio 工作流中的 Bank 不是同一个概念。

Godot-FmodPlayer 面向常规音频文件和 FMOD Core API 用法时，通常不需要直接处理 FSB。
如果项目依赖特殊打包格式，应先确认当前目标平台、FMOD Engine 版本和插件导入流程是否支持。

.. _glossary-profiler:

Profiler
--------

Profiler 是用于观察音频系统运行状态的工具。它可以帮助定位 CPU 占用、流式读取、通道数量、DSP 开销和混音问题。

Godot-FmodPlayer 会把部分 FMOD 性能数据注册到 Godot 的性能监视器中，例如 ``FmodCPUUsage/DSP``、
``FmodCPUUsage/Stream`` 和 ``FmodFileUsage/StreamBytesRead``。调试卡顿、爆音或加载异常时，建议同时查看 Godot 输出面板和性能监视器。

.. _glossary-runtime:

运行库
------

运行库指 FMOD Engine 在目标平台上的二进制文件，例如 Windows 上的 ``fmod.dll``，Android 上的 ``libfmod.so`` 和相关 Java 文件。

Godot-FmodPlayer 插件本身不分发 FMOD 运行库。你需要根据目标平台从 FMOD 官方渠道获取，并按 :doc:`export`
或 :doc:`getting_started/installation` 的说明放到项目中。发布游戏时还需要遵守 FMOD 的许可和署名要求。
