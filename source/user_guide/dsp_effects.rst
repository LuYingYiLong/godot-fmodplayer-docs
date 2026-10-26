DSP 效果器
==========

本章讲“怎样给声音加效果”。

:ref:`DSP<glossary-dsp>` 是音频效果处理单元。混响、滤波、延迟、压缩、频谱分析都可以看成 DSP。刚开始使用时，建议优先用 ``FmodAudioEffect*`` 这些资源类，把效果加到 :ref:`Bus<glossary-bus>` 上；只有需要非常底层的控制时，再直接操作 :ref:`FmodDSP<class_FmodDSP>`。

先决定加在哪里
--------------

.. list-table::
  :header-rows: 1

  * - 需求
    - 推荐做法
  * - 所有音乐一起加滤波
    - 把效果加到 ``Music`` 总线
  * - 所有环境声一起加混响
    - 把效果加到 ``Ambient`` 总线
  * - 只影响一次播放
    - 拿到这次播放的 :ref:`Channel<glossary-channel>` 后添加 DSP
  * - 只是调整左右位置
    - 优先用 :ref:`FmodChannelControl.set_pan()<class_FmodChannelControl_method_set_pan>`，不需要单独加效果
  * - 做频谱 UI
    - 使用 ``FmodAudioEffectSpectrumAnalyzer``

对多数项目来说，“效果加到总线”最容易维护。比如暂停菜单打开时，只要给 ``Music`` 总线加低通或降低音量，所有音乐都会一起变化。

常用效果怎么选
--------------

.. list-table::
  :header-rows: 1

  * - 效果
    - 类
    - 常见用途
  * - 增益
    - :ref:`FmodAudioEffectAmplify<class_FmodAudioEffectAmplify>`
    - 放大或衰减声音
  * - 滤波器
    - :ref:`FmodAudioEffectFilter<class_FmodAudioEffectFilter>`
    - 水下、墙后、暂停菜单变闷
  * - 均衡器
    - :ref:`FmodAudioEffectEQ<class_FmodAudioEffectEQ>`
    - 调整低频、中频、高频
  * - 混响
    - :ref:`FmodAudioEffectReverb<class_FmodAudioEffectReverb>`
    - 房间、洞穴、走廊空间感
  * - 延迟
    - :ref:`FmodAudioEffectDelay<class_FmodAudioEffectDelay>`
    - 回声、节奏延迟
  * - 压缩器
    - :ref:`FmodAudioEffectCompressor<class_FmodAudioEffectCompressor>`
    - 控制动态范围，让声音更稳定
  * - 频谱分析器
    - :ref:`FmodAudioEffectSpectrumAnalyzer<class_FmodAudioEffectSpectrumAnalyzer>`
    - 音乐可视化、频段检测
  * - 录音
    - :ref:`FmodAudioEffectRecord<class_FmodAudioEffectRecord>`
    - 录制经过某条总线的声音

给总线添加效果
--------------

下面示例给 ``Music`` 总线加一个低通滤波器。它会让音乐听起来更闷，适合暂停菜单、角色潜水、隔墙听声等场景。

.. code-block:: gdscript

    func add_pause_filter():
        var layout := FmodServer.get_audio_bus_layout()

        var filter := FmodAudioEffectFilter.new()
        filter.cutoff_hz = 1200.0
        filter.resonance = 0.2

        layout.add_bus_effect("Music", filter)

效果加到总线后，经过这条 :ref:`Bus<glossary-bus>` 的声音都会受影响。

旁路效果
--------

如果只是临时关闭效果，优先用旁路，而不是反复创建和删除。

.. code-block:: gdscript

    func set_music_effects_enabled(enabled: bool):
        var layout := FmodServer.get_audio_bus_layout()
        layout.set_bus_bypass("Music", not enabled)

旁路的意思是：信号仍然通过，但跳过这条总线上的效果处理。

常用效果示例
------------

暂停菜单：音乐变闷
~~~~~~~~~~~~~~~~~~

.. code-block:: gdscript

    var pause_filter := FmodAudioEffectFilter.new()

    func _ready():
        pause_filter.cutoff_hz = 1000.0
        pause_filter.resonance = 0.1
        FmodServer.get_audio_bus_layout().add_bus_effect("Music", pause_filter)
        FmodServer.get_audio_bus_layout().set_bus_bypass("Music", true)

    func set_paused_audio(paused: bool):
        FmodServer.get_audio_bus_layout().set_bus_bypass("Music", not paused)

房间混响：给环境声加空间感
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: gdscript

    func setup_room_reverb():
        var reverb := FmodAudioEffectReverb.new()
        reverb.room_size = 0.7
        reverb.damping = 0.45
        reverb.wet = 0.35
        reverb.dry = 1.0

        FmodServer.get_audio_bus_layout().add_bus_effect("Ambient", reverb)

均衡器：削弱刺耳频段
~~~~~~~~~~~~~~~~~~~~

.. code-block:: gdscript

    func soften_sfx():
        var eq := FmodAudioEffectEQ10.new()

        # 降低较高频段，让音效不那么刺耳。
        eq.set_band_gain_db(7, -3.0)
        eq.set_band_gain_db(8, -4.0)

        FmodServer.get_audio_bus_layout().add_bus_effect("SFX", eq)

延迟：给特殊音效加回声
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: gdscript

    func add_echo_to_voice_bus():
        var delay := FmodAudioEffectDelay.new()
        delay.tap1_delay_ms = 180.0
        delay.tap1_level_db = -8.0
        delay.tap2_active = false
        delay.feedback_active = true
        delay.feedback_delay_ms = 260.0
        delay.feedback_level_db = -12.0

        FmodServer.get_audio_bus_layout().add_bus_effect("Voice", delay)

频谱分析：读取音乐能量
~~~~~~~~~~~~~~~~~~~~~~

``FmodAudioEffectSpectrumAnalyzer`` 不改变声音，它只是读取频谱数据。适合音乐可视化、根据低频驱动画面等。

.. code-block:: gdscript

    var analyzer := FmodAudioEffectSpectrumAnalyzer.new()

    func _ready():
        analyzer.fft_size = FmodAudioEffectSpectrumAnalyzer.FFT_SIZE_2048
        FmodServer.get_audio_bus_layout().add_bus_effect("Music", analyzer)

    func _process(_delta):
        analyzer.update_spectrum()

        var bass := analyzer.get_magnitude_for_frequency_range(
            20.0,
            250.0,
            FmodAudioEffectSpectrumAnalyzer.MAGNITUDE_AVERAGE
        )

        print("bass energy: ", bass.length())

录音：录下某条总线
~~~~~~~~~~~~~~~~~~

``FmodAudioEffectRecord`` 会让声音原样通过，同时在录制开启时缓存经过总线的音频。

.. code-block:: gdscript

    var recorder := FmodAudioEffectRecord.new()

    func _ready():
        recorder.format = FmodAudioEffectRecord.FORMAT_16_BITS
        FmodServer.get_audio_bus_layout().add_bus_effect("Master", recorder)

    func start_recording():
        recorder.recording_active = true

    func stop_recording() -> AudioStreamWAV:
        recorder.recording_active = false
        return recorder.get_recording()

效果顺序
--------

多个 :ref:`DSP<glossary-dsp>` 会组成 :ref:`DSP 链<glossary-dsp-chain>`。声音会按顺序经过它们，所以顺序会影响听感。

一个容易理解的默认顺序是：

.. code-block:: text

    均衡器 / 滤波器 -> 压缩器 -> 失真 -> 延迟 / 混响 -> 分析器 / 录音

这不是硬规则。比如先失真再混响，和先混响再失真，听起来会很不一样。调效果时建议一次只改一个变量，边听边调。

什么时候直接用 FmodDSP
----------------------

``FmodAudioEffect*`` 更适合用户指南里的常规用法；``FmodDSP`` 更接近底层 FMOD。

只有在这些情况才建议直接用 :ref:`FmodDSP<class_FmodDSP>`：

- 需要访问 FMOD 内置 DSP 的原始参数索引。
- 需要手动插入某个 :ref:`Channel<glossary-channel>` 的 DSP 链。
- 需要自定义 DSP 回调或做实验性处理。
- 你已经知道对应 DSP 的参数含义和范围。

一个最小示例：

.. code-block:: gdscript

    func add_low_level_reverb():
        var system := FmodServer.main_system
        var reverb := system.create_dsp_by_type(FmodDSP.DSP_TYPE_SFXREVERB)
        var master := system.get_master_channel_group()

        master.add_dsp(0, reverb)

低层 DSP 参数通常是数字索引，不如 ``FmodAudioEffectReverb.room_size`` 这类属性直观。普通项目优先使用效果资源类。

性能建议
--------

- 每个启用的 :ref:`DSP<glossary-dsp>` 都会增加 CPU 开销。
- 多个声音共享同一种效果时，放到总线上通常更省。
- 临时关闭效果时，用旁路比反复添加、移除更稳定。
- 频谱分析和音高变换这类 FFT 效果更容易吃 CPU。
- 不要每帧大幅跳变参数；需要变化时用插值或 Tween。

排查清单
--------

效果没有声音变化时，先检查：

- 声音是否真的输出到这条 :ref:`Bus<glossary-bus>`。
- 总线是否被旁路。
- 效果参数是否太轻，听不出来。
- 效果是否加到了错误的总线。
- 多个效果顺序是否和预期一致。
