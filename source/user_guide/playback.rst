.. _playback:

播放控制
============

播放器节点管理音频资源和播放通道。低层 ``FmodChannel`` 接口可控制某一次播放的位置、循环和空间属性。

选择播放节点
----------------

.. list-table::
   :header-rows: 1

   * - 节点
     - 用途
   * - :ref:`FmodAudioStreamPlayer<class_FmodAudioStreamPlayer>`
     - 音乐、UI 和其他非空间音频
   * - :ref:`FmodAudioStreamPlayer2D<class_FmodAudioStreamPlayer2D>`
     - 相对 2D 监听器计算距离衰减和左右声像
   * - :ref:`FmodAudioStreamPlayer3D<class_FmodAudioStreamPlayer3D>`
     - 3D 场景中的位置、方向和距离衰减

将 Stream 赋给节点后调用 ``play()``，或启用 ``auto_play`` 在游戏场景就绪后自动播放。编辑器试听使用 Stream 子检查器中的播放按钮。

播放、暂停与跳转
--------------------

.. code-block:: gdscript

    @onready var player: FmodAudioStreamPlayer = $FmodAudioStreamPlayer


    func play_from(seconds: float) -> void:
        player.play(seconds)


    func pause_audio(paused: bool) -> void:
        player.stream_paused = paused


    func seek_audio(seconds: float) -> void:
        player.seek(seconds)


    func stop_audio() -> void:
        player.stop()

节点的 ``play()``、``seek()`` 和 ``get_playback_position()`` 使用秒。暂停期间 ``is_playing()`` 仍可返回 ``true``；暂停状态通过 ``stream_paused`` 判断。

音量、音高与淡变
--------------------

节点使用 ``volume_db`` 调整分贝音量，使用 ``pitch_scale`` 调整音高和速度。``0.0`` dB 和 ``1.0`` 倍分别表示单位增益和原速。

.. code-block:: gdscript

    func fade_player(player: FmodAudioStreamPlayer, target_db: float, duration: float) -> void:
        var tween: Tween = create_tween()
        tween.tween_property(player, "volume_db", target_db, duration)

循环与重叠播放
------------------

循环在资源的 ``mode_flags`` 中配置，见 :doc:`audio_resources`。对同一个节点再次调用 ``play()`` 会重新开始当前播放；同时发出多个声音时，使用多个节点或独立通道。

.. code-block:: gdscript

    func play_one_shot(audio: FmodAudioStream) -> void:
        if audio == null:
            return
        var player: FmodAudioStreamPlayer = FmodAudioStreamPlayer.new()
        player.stream = audio
        player.finished.connect(player.queue_free, CONNECT_ONE_SHOT)
        add_child(player)
        player.play()

此示例使用非循环音频，自然结束时释放临时节点。主动调用 ``stop()`` 不会触发 ``finished``，主动停止时也要安排节点回收。高频音效可复用播放器池。

2D 与 3D 位置音频
----------------------------

将空间播放器放在声源节点下，使其随角色、车辆或环境物件移动。服务器在游戏中读取当前视口相机作为监听器；编辑器试听使用编辑器相机。

2D 调整 ``max_distance``、``attenuation`` 和 ``panning_strength``；3D 调整距离与衰减模型，并确认当前 Camera3D 已激活。检查声源和监听器的世界坐标及方向。

低层通道播放
----------------

``FmodSystem.play_sound()`` 返回本次播放的 ``FmodChannel``。以下函数接收由调用方保留的 ``FmodSound``，先暂停创建通道，设置参数后恢复播放：

.. code-block:: gdscript

    func play_sound(sound: FmodSound, bus_name: StringName = &"Master") -> FmodChannel:
        var bus: FmodAudioBus = FmodServer.get_audio_bus(bus_name)
        var group: FmodChannelGroup = bus.get_bus() if bus != null else FmodServer.get_master_channel_group()
        var channel: FmodChannel = FmodServer.get_main_system().play_sound(sound, group, true)
        if channel == null:
            return null
        channel.volume_db = -6.0
        channel.pitch = 1.0
        channel.set_paused(false)
        return channel

低层通道使用 ``pitch``；播放器节点使用 ``pitch_scale``。通道位置默认以毫秒表示，也可通过 ``FmodSystem.FmodTimeUnit`` 指定其他单位：

.. code-block:: gdscript

    func seek_channel(channel: FmodChannel, seconds: float) -> void:
        channel.set_position(int(seconds * 1000.0), FmodSystem.FMOD_TIME_UNIT_MS)

运行时总线和效果配置见 :doc:`mixer`、:doc:`dsp_effects`。无声、首次播放延迟及资源清理问题见 :doc:`faq`。
