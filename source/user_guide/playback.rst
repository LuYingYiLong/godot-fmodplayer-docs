.. _playback:

播放控制
========

本章讲“怎样把声音播出来，以及播出来以后怎样控制它”。

刚开始使用时，优先用播放节点。只有当你需要更细的控制，例如一次性创建 :ref:`Sound<glossary-sound>`、拿到 :ref:`Channel<glossary-channel>`、手动设置循环点或 3D 属性时，再使用代码播放。

先选哪种播放方式
----------------

.. list-table::
  :header-rows: 1

  * - 需求
    - 推荐方式
  * - 背景音乐、长音频、场景里的固定播放器
    - :ref:`FmodAudioStreamPlayer<class_FmodAudioStreamPlayer>`
  * - 2D 场景里的音效
    - :ref:`FmodAudioStreamPlayer2D<class_FmodAudioStreamPlayer2D>`
  * - 3D 世界里的声源
    - :ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>`
  * - 同一个短音效频繁触发
    - 预加载 :ref:`音频资产<glossary-audio-asset>`，或复用 :ref:`Sound<glossary-sound>`
  * - 播放后还要精细控制
    - 取得 :ref:`Channel<glossary-channel>`

如果你不确定，先用节点。节点能处理大多数播放、停止、音量、音高和总线路由需求。

用节点播放
----------

最常见的写法是给节点设置 ``stream``，然后调用 ``play()``。

.. code-block:: gdscript

    extends Node

    @onready var music := $FmodAudioStreamPlayer

    func _ready():
        var stream := FmodAudioStream.new()
        stream.file_path = "res://music/bgm.mp3"

        music.stream = stream
        music.bus = "Music"

    func play_music():
        music.play()

    func stop_music():
        music.stop()

这里的 ``stream`` 是 Godot-FmodPlayer 的音频资源。底层真正交给 FMOD 播放时，会创建 :ref:`Sound<glossary-sound>`，播放出来的一次声音会对应一个 :ref:`Channel<glossary-channel>`。

常用节点属性
~~~~~~~~~~~~

.. list-table::
  :header-rows: 1

  * - 属性
    - 用途
  * - ``stream``
    - 要播放的音频资源
  * - ``volume_db``
    - 音量，单位为分贝；``0.0`` 是原始音量
  * - ``pitch``
    - 音高和速度倍率；``1.0`` 是正常
  * - ``autoplay``
    - 场景开始时自动播放
  * - ``bus``
    - 输出到哪个 :ref:`Bus<glossary-bus>`
  * - ``playing``
    - 当前是否正在播放

淡入淡出
~~~~~~~~

节点是 Godot 节点，可以直接用 Tween：

.. code-block:: gdscript

    @onready var music: FmodAudioStreamPlayer = $FmodAudioStreamPlayer


    func fade_music(target_db: float, duration: float) -> void:
        var tween: Tween = create_tween()
        tween.tween_property(music, "volume_db", target_db, duration)

播放一次短音效
--------------

如果只是“按按钮、开枪、拾取物品”这种一次性短音效，可以放一个播放器节点，然后反复调用 ``play()``：

.. code-block:: gdscript

    extends Node

    @onready var hit := $HitPlayer

    func _ready():
        var stream := FmodAudioStream.new()
        stream.file_path = "res://sfx/hit.wav"
        hit.stream = stream
        hit.bus = "SFX"

    func play_hit():
        hit.play()

如果同一个声音可能重叠播放很多次，例如一秒内触发多发子弹，建议考虑代码播放或对象池，避免一个节点来不及处理所有重叠声音。

用代码播放
----------

代码播放会更接近 FMOD 的工作方式：

1. 用 :ref:`System<glossary-system>` 创建 :ref:`Sound<glossary-sound>`。
2. 选择输出到哪个 :ref:`Bus<glossary-bus>` / :ref:`ChannelGroup<glossary-channelgroup>`。
3. 调用 ``play_sound()``，得到这次播放的 :ref:`Channel<glossary-channel>`。

.. code-block:: gdscript

    func play_sound(path: String, bus_name: String = "SFX") -> FmodChannel:
        var system := FmodServer.get_main_system()

        var sound := system.create_sound_from_file(path)
        var runtime_bus: FmodAudioBus = FmodServer.get_audio_bus(StringName(bus_name))
        var bus: FmodChannelGroup = runtime_bus.get_bus() if runtime_bus != null else FmodServer.get_master_channel_group()
        var channel := system.play_sound(sound, bus, false)

        return channel

返回的 ``channel`` 只代表“这一次播放”。同一个 ``sound`` 播放三次，就会有三个不同的 :ref:`Channel<glossary-channel>`。

先暂停再配置
~~~~~~~~~~~~

有时你希望声音开始前先设置音量、音高或 3D 位置。可以让它以暂停状态创建，配置完成后再恢复：

.. code-block:: gdscript

    func play_configured(path: String) -> FmodChannel:
        var system := FmodServer.get_main_system()
        var sound := system.create_sound_from_file(path)
        var runtime_bus: FmodAudioBus = FmodServer.get_audio_bus(&"SFX")
        var sfx_bus: FmodChannelGroup = runtime_bus.get_bus() if runtime_bus != null else FmodServer.get_master_channel_group()

        var channel := system.play_sound(sound, sfx_bus, true)
        channel.volume_db = -6.0
        channel.pitch = 1.2
        channel.set_paused(false)

        return channel

控制一次播放
------------

:ref:`Channel<glossary-channel>` 是“一次正在播放的声音”。它可以暂停、停止、调音量、调音高、跳转位置，也可以设置 3D 属性。

暂停、恢复和停止
~~~~~~~~~~~~~~~~

.. code-block:: gdscript

    func pause_channel(channel: FmodChannel, paused: bool):
        if channel != null:
            channel.set_paused(paused)

    func stop_channel(channel: FmodChannel):
        if channel != null:
            channel.stop()

    func is_still_playing(channel: FmodChannel) -> bool:
        return channel != null and channel.is_playing()

音量、音高和声像
~~~~~~~~~~~~~~~~

.. code-block:: gdscript

    func adjust_channel(channel: FmodChannel):
        channel.volume_db = -10.0
        channel.pitch = 1.0

        # -1.0 在左边，0.0 在中间，1.0 在右边。
        channel.set_pan(0.25)

``pitch`` 会同时影响音高和播放速度。``0.5`` 听起来更低也更慢，``2.0`` 听起来更高也更快。

播放位置
~~~~~~~~

位置通常用毫秒控制。适合音乐跳转、从某个时间点继续播放，或做简单的预览工具。

.. code-block:: gdscript

    func jump_to_30_seconds(channel: FmodChannel):
        channel.set_position(30000, FmodSystem.FMOD_TIME_UNIT_MS)

    func print_position(channel: FmodChannel):
        var position_ms := channel.get_position(FmodSystem.FMOD_TIME_UNIT_MS)
        print("position: ", position_ms, " ms")

循环
~~~~

.. code-block:: gdscript

    func loop_forever(channel: FmodChannel):
        channel.loop_count = -1

    func loop_three_times(channel: FmodChannel):
        channel.loop_count = 3

    func disable_loop(channel: FmodChannel):
        channel.loop_count = 0

循环是否生效还和创建声音时使用的播放模式有关。常规节点播放通常更适合简单循环；需要精确控制循环点时，再直接控制 :ref:`Channel<glossary-channel>` 和 :ref:`Sound<glossary-sound>`。

2D 与 3D 播放
-------------

2D 声音不跟随世界位置变化，适合 UI、音乐、旁白。3D 声音会根据 :ref:`Listener<glossary-listener>` 和声源的位置计算距离、方向和衰减。

优先使用 3D 播放节点
~~~~~~~~~~~~~~~~~~~~

在 3D 场景里，最简单的方式是使用 :ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>`。它会把节点位置同步给 FMOD。

.. code-block:: gdscript

    extends Node3D

    @onready var emitter := $FmodAudioStreamPlayer3D

    func play_at_current_position():
        emitter.bus = "SFX"
        emitter.play()

如果声音应该跟随敌人、车辆、门、机关或环境物件，就把播放器作为这些节点的子节点。

代码方式设置 3D 位置
~~~~~~~~~~~~~~~~~~~~

只有在你直接代码播放时，才需要手动设置 3D 属性：

.. code-block:: gdscript

    func play_3d_sound(path: String, position: Vector3):
        var system := FmodServer.get_main_system()
        var sound := system.create_sound_from_file(path, FmodSystem.FMOD_MODE_3D)
        var runtime_bus: FmodAudioBus = FmodServer.get_audio_bus(&"SFX")
        var bus: FmodChannelGroup = runtime_bus.get_bus() if runtime_bus != null else FmodServer.get_master_channel_group()

        var channel := system.play_sound(sound, bus, true)
        channel.set_3d_attributes(position, Vector3.ZERO)
        channel.set_3d_min_max_distance(1.0, 30.0)
        channel.set_paused(false)

        return channel

这里的 ``FMOD_MODE_3D`` 很重要。没有用 3D 模式创建的声音，即使设置了位置，也不会按 3D 声源来计算。

监听器
~~~~~~

:ref:`Listener<glossary-listener>` 表示玩家“从哪里听”。通常它跟随玩家角色或主摄像机。

.. code-block:: gdscript

    extends CharacterBody3D

    func _physics_process(_delta):
        var system := FmodServer.get_main_system()
        system.set_3d_listener_attributes(
            0,
            global_position,
            velocity,
            -global_transform.basis.z,
            global_transform.basis.y
        )

如果 3D 声音听起来方向不对、距离不对，先检查监听器位置和朝向。

常见问题
--------

声音没有播放
~~~~~~~~~~~~

按顺序检查：

- 音频路径是否正确。
- 播放节点是否有 ``stream``。
- 目标 :ref:`Bus<glossary-bus>` 是否存在，是否被静音。
- 音量是否太低。
- 3D 声音是否离 :ref:`Listener<glossary-listener>` 太远。

声音只能播放一次
~~~~~~~~~~~~~~~~

如果同一个节点还在播放，再调用 ``play()`` 可能会重启这一次播放，而不是创建新的重叠声音。需要重叠播放时，可以创建多个播放器、使用对象池，或直接用 ``play_sound()`` 获取多个 :ref:`Channel<glossary-channel>`。

大量声音时卡顿
~~~~~~~~~~~~~~

短音效可以优先用 Sample 方式或预加载；长音乐优先用 Stream 方式。两者的区别见 :ref:`Stream 与 Sample<glossary-stream-sample>`。

同时播放很多声音时，也可以关注 :ref:`Virtual Channel<glossary-virtual-channel>`。FMOD 可能会让听不见或优先级低的声音进入虚拟状态，以减少混音开销。

建议
----

- 入门先用播放节点，不要一开始就直接操作底层对象。
- 需要控制“这一次播放”时，再拿 :ref:`Channel<glossary-channel>`。
- 长音乐走 ``Music`` 总线，短音效走 ``SFX`` 总线。
- 3D 声音优先用 :ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>`。
- 代码播放时，如果要先配置参数，就用暂停状态创建，再恢复播放。
