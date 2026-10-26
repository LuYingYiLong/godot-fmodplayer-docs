音频资源
========

本章讲“音频文件怎样变成可以播放的资源”。

在 Godot-FmodPlayer 里，常用资源是 :ref:`FmodAudioStream<class_FmodAudioStream>`。你可以把它理解成 Godot 侧保存音频数据和播放设置的对象。真正播放时，它会在底层创建 :ref:`Sound<glossary-sound>`，再由播放器或系统播放成一次 :ref:`Channel<glossary-channel>`。

先选加载方式
------------

最重要的选择只有一个：长音频用 Stream，短音效用 Sample。

.. list-table::
  :header-rows: 1

  * - 声音类型
    - 推荐模式
    - 原因
  * - 背景音乐
    - ``MODE_STREAM``
    - 文件通常较大，边读边播更省内存
  * - 长旁白、长环境声
    - ``MODE_STREAM``
    - 播放时间长，不适合全部放进内存
  * - UI 声、按钮声
    - ``MODE_SAMPLE``
    - 文件短，追求快速响应
  * - 武器、脚步、拾取音效
    - ``MODE_SAMPLE``
    - 可能频繁触发，低延迟更重要
  * - 很短但只播放一次的声音
    - 两者都可以
    - 优先按项目内存和延迟需求决定

这两个概念也可以看 :ref:`Stream 与 Sample<glossary-stream-sample>`。

FmodAudioStream
---------------

**FmodAudioStream** 是最常用的音频资源类。它保存音频数据和创建模式，例如是否流式播放、是否作为样本加载、是否循环。

常用创建模式
~~~~~~~~~~~~

.. list-table::
  :header-rows: 1

  * - 标志
    - 说明
  * - ``MODE_STREAM``
    - 流式播放，适合音乐和长音频
  * - ``MODE_SAMPLE``
    - 样本播放，适合短音效和低延迟播放
  * - ``MODE_LOOP``
    - 循环播放
  * - ``MODE_LOOP_BIDI``
    - 双向循环，类似来回播放

这些标志可以用 ``|`` 组合：

.. code-block:: gdscript

    var flags := FmodAudioStream.MODE_STREAM | FmodAudioStream.MODE_LOOP

从文件加载
----------

推荐优先使用 ``res://`` 路径，这样导出项目时更容易保持一致。

.. code-block:: gdscript

    var music := FmodAudioStream.load_from_file(
        "res://music/bgm.ogg",
        FmodAudioStream.MODE_STREAM | FmodAudioStream.MODE_LOOP
    )

    var hit := FmodAudioStream.load_from_file(
        "res://sfx/hit.wav",
        FmodAudioStream.MODE_SAMPLE
    )

加载后可以直接交给播放器：

.. code-block:: gdscript

    @onready var music_player := $FmodAudioStreamPlayer

    func _ready():
        music_player.stream = music
        music_player.bus = "Music"
        music_player.play()

从内存加载
----------

如果音频来自加密包、网络、存档或你自己的加载流程，可以把二进制数据放进 ``audio_data``。

.. code-block:: gdscript

    func load_from_bytes(data: PackedByteArray) -> FmodAudioStream:
        var stream := FmodAudioStream.new()
        stream.audio_data = data
        stream.mode_flags = FmodAudioStream.MODE_SAMPLE
        return stream

这种方式要注意：播放期间资源对象必须还活着。不要在声音还没播放完时把保存数据的对象释放掉。

预加载常用音效
--------------

短音效经常会反复播放。可以在场景开始时先加载好，之后直接复用。

.. code-block:: gdscript

    extends Node

    var sfx := {}

    func _ready():
        sfx["hit"] = FmodAudioStream.load_from_file(
            "res://sfx/hit.wav",
            FmodAudioStream.MODE_SAMPLE
        )
        sfx["pickup"] = FmodAudioStream.load_from_file(
            "res://sfx/pickup.wav",
            FmodAudioStream.MODE_SAMPLE
        )

    func play_sfx(name: String):
        if not sfx.has(name):
            push_error("SFX not found: " + name)
            return

        var player := FmodAudioStreamPlayer.new()
        add_child(player)
        player.stream = sfx[name]
        player.bus = "SFX"
        player.play()

        await get_tree().create_timer(3.0).timeout
        player.queue_free()

如果你的项目会大量重叠播放短音效，可以进一步做播放器对象池。入门阶段先用上面的方式更容易理解。

背景音乐播放列表
----------------

音乐通常用 ``MODE_STREAM``，需要循环时再加 ``MODE_LOOP``。

.. code-block:: gdscript

    extends Node

    @onready var player := $FmodAudioStreamPlayer
    var tracks: Array[FmodAudioStream] = []
    var current_index := 0

    func _ready():
        tracks.append(FmodAudioStream.load_from_file(
            "res://music/track_0.ogg",
            FmodAudioStream.MODE_STREAM
        ))
        tracks.append(FmodAudioStream.load_from_file(
            "res://music/track_1.ogg",
            FmodAudioStream.MODE_STREAM
        ))

        play_track(0)

    func play_track(index: int):
        current_index = index
        player.stream = tracks[index]
        player.bus = "Music"
        player.play()

查询音频信息
------------

``FmodAudioStream`` 可以查询长度，也可以取得底层 :ref:`Sound<glossary-sound>`。

.. code-block:: gdscript

    func print_stream_info(stream: FmodAudioStream):
        print("loaded: ", stream.is_data_loaded())
        print("length: ", stream.get_length())

        var sound := stream.get_sound()
        if sound:
            print("sound length: ", sound.get_length())

普通播放通常不需要直接操作 ``FmodSound``。只有在你需要更底层的信息、回调或特殊播放控制时，才去拿它。

支持格式
--------

常见格式包括 ``.wav``、``.ogg``、``.mp3``、``.flac``、``.aiff``，以及部分模块音乐格式如 ``.mod``、``.xm``、``.s3m``、``.it``。

实用建议：

- 音乐优先考虑 ``ogg`` 或 ``mp3``。
- 短音效优先考虑 ``wav``。
- 需要无缝循环时，优先测试 ``ogg`` 或 ``wav`` 的循环点表现。
- 特殊格式在导出前一定要在目标平台测试。

常见问题
--------

音效第一次播放有延迟
~~~~~~~~~~~~~~~~~~~~

把短音效用 ``MODE_SAMPLE`` 加载，并在进入场景前预加载。

音乐占用内存太高
~~~~~~~~~~~~~~~~

检查是否把音乐用了 ``MODE_SAMPLE``。长音乐一般应该使用 ``MODE_STREAM``。

循环不生效
~~~~~~~~~~

确认创建模式里包含 ``MODE_LOOP``：

.. code-block:: gdscript

    stream.mode_flags = FmodAudioStream.MODE_STREAM | FmodAudioStream.MODE_LOOP

打包后找不到文件
~~~~~~~~~~~~~~~~

优先使用 ``res://`` 路径，并确认音频文件被包含在 Godot 导出规则中。

建议
----

- 长音乐、长环境声：``MODE_STREAM``。
- 短音效、UI 声、频繁触发的声音：``MODE_SAMPLE``。
- 常用短音效提前加载，避免第一次播放卡顿。
- 能用播放节点时先用播放节点，需要底层控制时再碰 :ref:`Sound<glossary-sound>` 和 :ref:`Channel<glossary-channel>`。
