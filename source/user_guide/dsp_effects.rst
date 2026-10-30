DSP 效果器
==================

``FmodAudioEffect*`` 资源配置总线效果，``FmodDSP`` 提供低层 DSP 接口。相同总线上的声音依次经过其效果器槽位。

选择效果器
--------------

.. list-table::
   :header-rows: 1

   * - 处理
     - 资源
   * - 增益与声像
     - ``Amplify``、``Panner``、``StereoEnhance``
   * - 滤波与均衡
     - ``Filter``、``EQ6``、``EQ10``、``EQ21``
   * - 动态与失真
     - ``Compressor``、``HardLimiter``、``Distortion``
   * - 时间与调制
     - ``Delay``、``Reverb``、``Chorus``、``Phaser``、``PitchShift``
   * - 数据采集
     - ``Capture``、``SpectrumAnalyzer``、``Record``

表中的名称都以 ``FmodAudioEffect`` 开头，完整接口见 :doc:`../api_reference/dsp`。在检查器中编辑效果资源可使用对应预览；Panner 支持拖动，EQ 支持拖动频率和增益、悬停滚轮调节 Q。

添加和旁路
--------------

以下示例使用 :doc:`mixer` 中的独立总线模式。为 Music 创建低通配置，将播放器的 Bus 设为 Music：

.. code-block:: gdscript

    func add_music_filter() -> int:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var music_id: int = layout.find_bus_id(&"Music")
        if music_id == -1:
            music_id = layout.add_bus(&"Music")
        var effect: FmodAudioEffectFilter = FmodAudioEffectFilter.new()
        effect.cutoff_hz = 1200.0
        return layout.add_bus_effect(music_id, effect)

返回值是槽位 ID。通过 ``set_bus_effect_enabled(bus_id, slot_id, enabled)`` 控制该槽位，或用 ``set_bus_bypass(bus_id, bypass)`` 旁路整条总线的受管效果。暂时关闭效果时保留槽位，可维持 DSP 状态。

配置与实时数据
------------------

布局保存配置资源，每个槽位拥有独立运行实例。修改配置会同步到实例；Capture 缓冲、频谱和录音从运行实例读取。添加槽位后调用 ``flush_bus_updates()``，即可在同一帧获取实例。

布局切换、槽位删除或效果替换后，应重新获取对应实例。共享配置不会共享各槽位的捕获和分析状态。

Capture：读取音频帧
------------------------------

.. code-block:: gdscript

    extends Node

    var capture: FmodAudioEffectCapture


    func _ready() -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var slot_id: int = layout.add_bus_effect(0, FmodAudioEffectCapture.new())
        FmodServer.flush_bus_updates()
        capture = FmodServer.get_bus_effect_instance(0, slot_id) as FmodAudioEffectCapture


    func _process(_delta: float) -> void:
        if capture == null:
            return
        var frames: PackedVector2Array = capture.get_buffer(capture.get_frames_available())
        if not frames.is_empty():
            print(frames[0])

每个 Vector2 的 x、y 分别为左、右采样。读取会消费缓冲帧；缓冲满时丢弃新帧，保留未读帧。``clear_buffer()`` 清空队列并重置计数。

SpectrumAnalyzer：读取频段
----------------------------------------------

.. code-block:: gdscript

    extends Node

    var analyzer: FmodAudioEffectSpectrumAnalyzer


    func _ready() -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var settings: FmodAudioEffectSpectrumAnalyzer = FmodAudioEffectSpectrumAnalyzer.new()
        settings.fft_size = FmodAudioEffectSpectrumAnalyzer.FFT_SIZE_2048
        var slot_id: int = layout.add_bus_effect(0, settings)
        FmodServer.flush_bus_updates()
        analyzer = FmodServer.get_bus_effect_instance(0, slot_id) as FmodAudioEffectSpectrumAnalyzer


    func _process(_delta: float) -> void:
        if analyzer == null:
            return
        var bass: Vector2 = analyzer.get_magnitude_for_frequency_range(
            20.0,
            250.0,
            FmodAudioEffectSpectrumAnalyzer.MAGNITUDE_AVERAGE,
        )
        print(bass)

频段查询返回左右声道的线性幅度。同一 DSP 时钟内复用频谱快照，新音频块到来后自动更新。增大 FFT 窗口会提高频率分辨率，并增加时间窗口和计算量。

Record：导出录音
--------------------------

.. code-block:: gdscript

    extends Node

    var recorder: FmodAudioEffectRecord


    func _ready() -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var settings: FmodAudioEffectRecord = FmodAudioEffectRecord.new()
        settings.format = FmodAudioEffectRecord.FORMAT_16_BITS
        var slot_id: int = layout.add_bus_effect(0, settings)
        FmodServer.flush_bus_updates()
        recorder = FmodServer.get_bus_effect_instance(0, slot_id) as FmodAudioEffectRecord


    func start_recording() -> void:
        if recorder != null:
            recorder.recording_active = true


    func stop_recording() -> AudioStreamWAV:
        if recorder == null:
            return null
        recorder.recording_active = false
        return recorder.get_recording()

``get_recording()`` 返回 AudioStreamWAV，可通过 ``save_to_wav(path)`` 保存。录制会持续积累音频数据；按需要限制时长并及时取出结果。

效果顺序与低层 DSP
--------------------------

槽位按布局顺序处理。可从“EQ/滤波 → 压缩 → 失真 → 延迟/混响 → 分析/录音”开始试听，再按目标音色调整；分析器和录音器的位置决定它们读取到的信号。

需要原生参数索引或给单次播放添加处理时，使用 :ref:`FmodDSP<class_FmodDSP>` 和 :ref:`FmodChannelControl.add_dsp()<class_FmodChannelControl_method_add_dsp>`。直接创建的 DSP 由调用方管理挂接、移除和释放。

频谱分析和音高变换等处理会增加 CPU 开销。运行项目后，在调试器监视器查看 ``FmodCPUUsage``；用相同音频、通道数和采样设置比较调整前后的结果。
