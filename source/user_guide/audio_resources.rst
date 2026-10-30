音频资源
============

:ref:`FmodAudioStream<class_FmodAudioStream>` 保存音频字节和创建设置。播放器使用它创建、缓存 :ref:`FmodSound<class_FmodSound>`，每次播放产生一个 :ref:`FmodChannel<class_FmodChannel>`。

导入资源与运行时加载
------------------------

项目内音频按 :doc:`../getting_started/quick_start` 导入为 FMOD Audio。将资源赋给播放器的 Stream，或通过导出属性在检查器中指定：

.. code-block:: gdscript

    extends Node

    @export var audio: FmodAudioStream
    @onready var player: FmodAudioStreamPlayer = $FmodAudioStreamPlayer


    func _ready() -> void:
        if audio == null:
            return
        player.stream = audio
        player.play()

导出属性由 Godot 保存资源引用。脚本中固定引用已有资源时使用编辑器提供的 UID；外部文件路径由加载函数的参数传入。

.. code-block:: gdscript

    func load_audio(path: String) -> FmodAudioStream:
        return FmodAudioStream.load_from_file(
            path,
            FmodAudioStream.MODE_SAMPLE,
        )

``load_from_file()`` 通过 Godot FileAccess 读取原始文件，失败时返回 ``null``。从导出包动态读取原始文件时，需要将它包含在导出规则中；已导入资源使用 Godot 的资源引用加载。

Stream、Sample 与循环
--------------------------------------

.. list-table::
   :header-rows: 1

   * - 标志
     - 用途
   * - ``MODE_STREAM``
     - 逐步解码，适合音乐和长音频
   * - ``MODE_SAMPLE``
     - 解码为样本，适合频繁触发的短音效
   * - ``MODE_LOOP``
     - 正向循环，可与 Stream 或 Sample 组合
   * - ``MODE_LOOP_BIDI``
     - 双向循环，需确认格式和加载模式支持

Stream 与 Sample 选择其一，通过 ``|`` 添加循环标志。在播放前设置模式；修改模式会使缓存的 Sound 失效。

.. code-block:: gdscript

    func configure_music(audio: FmodAudioStream) -> void:
        audio.mode_flags = FmodAudioStream.MODE_STREAM | FmodAudioStream.MODE_LOOP

``FmodAudioStream`` 在两种模式下都会保存音频文件字节，``load_from_file()`` 也会先读取整个文件。Stream 减少完整解码样本的内存开销，资源中的文件数据仍占内存。需要低层文件流时，可使用 ``FmodSystem.create_sound_from_file()`` 并指定 ``FmodSystem.FMOD_MODE_CREATESTREAM``。

预加载与复用
----------------

``preload()`` 提前创建内部 Sound。可在加载界面预加载常用短音效，或启用播放器的 ``preload_on_set_stream``。多个播放器可以共享同一资源，使用各自的播放通道。

.. code-block:: gdscript

    func prepare_audio(audio: FmodAudioStream) -> bool:
        if audio == null:
            return false
        return audio.preload()

通过导出数组维护音效或播放列表，可保留编辑器资源引用，避免每次触发都重新读文件。重叠播放和临时播放器的清理见 :doc:`playback`。

从内存创建
--------------

收到完整的编码音频数据后，赋给 ``audio_data``：

.. code-block:: gdscript

    func audio_from_bytes(data: PackedByteArray) -> FmodAudioStream:
        var audio: FmodAudioStream = FmodAudioStream.new()
        audio.mode_flags = FmodAudioStream.MODE_SAMPLE
        audio.audio_data = data
        return audio

普通 WAV、OGG 等编码文件可直接传入完整字节；无文件头的原始 PCM 还需要配置采样率、声道数和格式，参见 ``FmodAudioStream`` 的 Raw PCM 属性。

长度与生命周期
------------------

.. code-block:: gdscript

    func print_audio_info(audio: FmodAudioStream) -> void:
        print("Data loaded: ", audio.is_data_loaded())
        print("Length in seconds: ", audio.get_length())
        print("Sound cached: ", audio.is_preloaded())

播放期间保留资源引用。``get_sound()`` 返回资源管理的缓存对象；低层播放时，也应保留对应资源直到通道结束。停止使用该资源的所有播放器后，可释放引用或调用 ``clear()`` 清空数据。

相关页面
------------

播放与空间音频见 :doc:`playback`，总线配置见 :doc:`mixer`，导出过滤和运行库配置见 :doc:`../export`。
