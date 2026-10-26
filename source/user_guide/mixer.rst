.. _mixer:

混音系统
========

本章讲的是“声音最后从哪里出来、怎样一起调音量、怎样一起加效果”。

如果你刚开始使用 Godot-FmodPlayer，可以先把 :ref:`Bus<glossary-bus>` 理解成 Godot 的音频总线：音乐走 ``Music``，音效走 ``SFX``，对白走 ``Voice``。把声音分到不同总线后，就可以一次性控制一整类声音。

什么时候需要混音系统
--------------------

常见需求可以这样对应：

.. list-table::
  :header-rows: 1

  * - 你想做的事
    - 推荐做法
  * - 调低所有音乐
    - 把音乐播放到 ``Music`` 总线，然后调这个总线的 ``volume_db``
  * - 暂停时让音效静音
    - 静音 ``SFX`` 总线
  * - 对所有脚步声加滤波
    - 建一个 ``Footsteps`` 总线，并把效果加到这个总线上
  * - 对单个正在播放的声音微调
    - 取得 :ref:`Channel<glossary-channel>`，只控制这一次播放
  * - 对一组声音统一控制
    - 使用 :ref:`Bus<glossary-bus>` 或它底层的 :ref:`ChannelGroup<glossary-channelgroup>`

核心概念
--------

Bus
~~~

:ref:`Bus<glossary-bus>` 是一条混音路径。你可以把它想成一条“声音分类管道”。

例如：

.. code-block:: text

    Master
    ├── Music
    ├── SFX
    ├── Voice
    └── Ambient

所有声音最后都会汇入 ``Master``。如果把背景音乐送到 ``Music``，把按钮音效送到 ``SFX``，以后就可以分别控制它们。

ChannelGroup
~~~~~~~~~~~~

:ref:`ChannelGroup<glossary-channelgroup>` 是 FMOD 底层用于混合一组 :ref:`Channel<glossary-channel>` 的对象。普通使用时优先操作 :ref:`FmodAudioBus<class_FmodAudioBus>` 或总线布局；只有需要更底层的播放控制时，才直接拿 :ref:`FmodChannelGroup<class_FmodChannelGroup>`。

DSP
~~~

:ref:`DSP<glossary-dsp>` 是音频效果处理单元。混响、滤波、延迟、压缩、频谱分析都属于 DSP。多个声音要共享同一个效果时，通常把效果加到总线上，而不是给每个声音单独加。

把声音送到总线
--------------

最简单的方式是设置播放节点的 ``bus``：

.. code-block:: gdscript

    extends Node

    @onready var music := $MusicPlayer
    @onready var hit_sfx := $HitPlayer

    func _ready():
        music.bus = "Music"
        hit_sfx.bus = "SFX"

    func play_music():
        music.play()

    func play_hit():
        hit_sfx.play()

如果你直接用代码播放 :ref:`Sound<glossary-sound>`，就把目标 :ref:`ChannelGroup<glossary-channelgroup>` 传给 ``play_sound()``：

.. code-block:: gdscript

    func play_ui_sound(path: String):
        var system := FmodServer.main_system
        var ui_bus := system.get_channel_group_by_name("UI")
        var sound := system.create_sound_from_file(path)
        return system.play_sound(sound, ui_bus, false)

控制总线音量、静音和独奏
------------------------

音量通常用分贝（dB）表示：

- ``0.0`` 表示原始音量。
- 负数表示变小，例如 ``-6.0``。
- 正数表示变大，但要小心失真。

.. code-block:: gdscript

    func set_music_quiet():
        var system := FmodServer.main_system
        var music := system.get_channel_group_by_name("Music")

        music.volume_db = -12.0

    func mute_sfx(muted: bool):
        var system := FmodServer.main_system
        var sfx := system.get_channel_group_by_name("SFX")

        sfx.mute = muted

    func solo_voice(enabled: bool):
        var system := FmodServer.main_system
        var voice := system.get_channel_group_by_name("Voice")

        voice.solo = enabled

``mute`` 是让这条总线静音。``solo`` 是只听这条总线，常用于调试对白、环境声或音乐。

和 Godot 音频总线同步
---------------------

Godot-FmodPlayer 的 FMOD 总线布局会和 Godot 的 `AudioServer`_ 总线布局同步。也就是说，你在 Godot 的音频总线面板里创建的 ``Music``、``SFX``、``Voice`` 等总线，也可以被映射到 FMOD 侧使用。

通常情况下，你只需要通过 :ref:`FmodServer.get_audio_bus_layout()<class_FmodServer_method_get_audio_bus_layout>` 取得当前布局：

.. code-block:: gdscript

    func get_layout():
        var layout := FmodServer.get_audio_bus_layout()
        return layout

如果你在运行时修改了 Godot 的音频总线结构，可以让 FMOD 侧按需同步：

.. code-block:: gdscript

    func sync_buses_from_godot():
        var layout := FmodServer.get_audio_bus_layout()
        layout.sync_from_audio_server_if_changed()

同步会保留或创建 ``Master`` 总线，并根据 Godot 当前的总线结构更新 FMOD 侧的总线、父子关系、音量、静音、独奏、旁路状态和支持的音频效果。

.. note::

   如果项目的总线结构主要在 Godot 编辑器里维护，推荐优先通过 Godot 音频总线面板创建总线，再让 FMOD 布局同步。只有运行时需要临时总线，或者你明确希望由代码管理总线结构时，再手动调用 ``create_audio_bus()``。

创建自己的总线
--------------

默认总线不够用时，可以通过 Godot 音频总线面板新增总线，然后同步到 FMOD。也可以直接通过 :ref:`FmodAudioBusLayout<class_FmodAudioBusLayout>` 在代码中创建新总线：

.. code-block:: gdscript

    func setup_extra_buses():
        var layout := FmodServer.get_audio_bus_layout()

        layout.create_audio_bus("UI", "Master")
        layout.create_audio_bus("Weapons", "SFX")
        layout.create_audio_bus("Footsteps", "SFX")

建议总线层级先保持简单：

.. code-block:: text

    Master
    ├── Music
    ├── SFX
    │   ├── Weapons
    │   └── Footsteps
    ├── Voice
    └── UI

如果不确定是否要新建总线，先问自己一句：以后是否要单独调它的音量、静音或效果？如果答案是“是”，就适合拆成总线。

给总线添加效果
--------------

总线效果适合处理“一整类声音”。例如所有室内脚步声都变闷，或者暂停菜单打开时让音乐带一点低通。

.. code-block:: gdscript

    func add_pause_filter():
        var layout := FmodServer.get_audio_bus_layout()

        var filter := FmodAudioEffectFilter.new()
        filter.cutoff_hz = 1200.0
        filter.resonance = 0.2

        layout.add_bus_effect("Music", filter)

这里的滤波器就是一个 :ref:`DSP<glossary-dsp>`。如果只想影响某一次播放，不要加到总线上；去控制那一次播放返回的 :ref:`Channel<glossary-channel>` 会更合适。

淡入淡出
--------

总线对象不是 Godot 节点，不能直接用 ``tween_property()`` 绑属性动画。可以用一个循环逐帧插值：

.. code-block:: gdscript

    func fade_bus(bus_name: String, target_db: float, duration: float):
        var system := FmodServer.main_system
        var bus := system.get_channel_group_by_name(bus_name)
        if bus == null:
            return

        var start_db := bus.get_volume_db()
        var elapsed := 0.0

        while elapsed < duration:
            await get_tree().process_frame
            elapsed += get_process_delta_time()

            var t := clampf(elapsed / duration, 0.0, 1.0)
            bus.set_volume_db(lerpf(start_db, target_db, t))

        bus.set_volume_db(target_db)

常见用法是暂停时压低音乐：

.. code-block:: gdscript

    func on_pause_changed(paused: bool):
        if paused:
            fade_bus("Music", -10.0, 0.25)
        else:
            fade_bus("Music", 0.0, 0.25)

降低音乐给对白让位
------------------

这个效果常被叫作 ducking，意思是对白播放时先把音乐压低，播放结束后再恢复。

.. code-block:: gdscript

    var normal_music_db := 0.0
    var ducked_music_db := -12.0

    func play_voice_line(path: String):
        await fade_bus("Music", ducked_music_db, 0.2)

        var system := FmodServer.main_system
        var voice_bus := system.get_channel_group_by_name("Voice")
        var sound := system.create_sound_from_file(path)
        var channel := system.play_sound(sound, voice_bus, false)

        while channel != null and channel.is_playing():
            await get_tree().process_frame

        await fade_bus("Music", normal_music_db, 0.3)

这不是必须使用压缩器才能完成。对多数游戏来说，直接调低音乐总线已经足够清楚，也更容易理解和调试。

高级：混音矩阵什么时候需要看
----------------------------

:ref:`Mix Matrix<glossary-mix-matrix>` 可以精确控制“哪个输入声道送到哪个输出声道”。如果你只是想让声音偏左或偏右，优先用 :ref:`FmodChannelControl.set_pan()<class_FmodChannelControl_method_set_pan>`。

只有在这些情况下，才建议继续研究 :ref:`FmodChannelControl.set_mix_matrix()<class_FmodChannelControl_method_set_mix_matrix>`：

- 要把单声道手动分配到多声道输出，也就是 :ref:`Upmix<glossary-upmix>`。
- 要把 5.1 等多声道内容折叠成立体声，也就是 :ref:`Downmix<glossary-downmix>`。
- 要交换左右声道或做特殊声道路由。
- 要调试某个音频资产的声道顺序。

一个最小示例：把立体声左右声道对调。

.. code-block:: gdscript

    func swap_stereo(channel: FmodChannel):
        var matrix := PackedFloat32Array([
            0.0, 1.0,
            1.0, 0.0,
        ])

        channel.set_mix_matrix(matrix, 2, 2)

性能与排查
----------

混音相关问题可以从三处开始看：

- 声音是否被送到了正确的 :ref:`Bus<glossary-bus>`。
- 目标总线是否被静音、独奏或音量过低。
- 是否有过多 :ref:`DSP<glossary-dsp>` 同时启用。

可以在 Godot 性能监视器中查看 FMOD 注册的性能项：

.. code-block:: gdscript

    func _process(_delta):
        var dsp_usage = Performance.get_monitor("FmodCPUUsage/DSP")
        var stream_usage = Performance.get_monitor("FmodCPUUsage/Stream")
        var channels = FmodServer.main_system.get_channels_playing()

        print("DSP: %.2f%% | Stream: %.2f%% | Real: %d | Virtual: %d" % [
            dsp_usage,
            stream_usage,
            channels["real"],
            channels["virtual"],
        ])

这里的 ``Virtual`` 指 :ref:`Virtual Channel<glossary-virtual-channel>`。它不一定是错误，很多时候只是 FMOD 在帮你节省混音资源。

建议
----

- 先用 ``Master``、``Music``、``SFX``、``Voice``、``UI`` 这样的简单结构。
- 只有需要单独控制时才继续拆分总线。
- 多个声音共享效果时，把 :ref:`DSP<glossary-dsp>` 加到总线上。
- 单个声音的临时控制，优先使用播放返回的 :ref:`Channel<glossary-channel>`。
- 不要一开始就设计很深的总线树；能听清、能维护，比“看起来专业”更重要。
