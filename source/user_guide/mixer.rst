.. _mixer:

混音系统
========

:ref:`FmodAudioBusLayout<class_FmodAudioBusLayout>` 保存总线和效果器配置，:ref:`FmodServer<class_FmodServer>` 创建对应的运行时总线和 DSP。将音乐、音效和对白分别送到 ``Music``、``SFX``、``Voice``，即可按类别调整音量和效果。

选择布局来源
------------

项目设置中的 ``audio/fmod`` 提供两个选项：

.. list-table::
   :header-rows: 1

   * - 设置
     - 默认值
     - 用途
   * - ``sync_godot_audio_buses``
     - ``true``
     - 使用 Godot Audio 面板中的总线配置，支持的效果器自动转换为 FMOD 效果
   * - ``default_bus_layout``
     - ``res://default_fmod_bus_layout.tres``
     - 独立模式启动时加载的 FMOD 布局资源

修改同步开关后重新加载项目。开启同步时，在原生 Audio 面板或通过 `AudioServer`_ 修改配置；FMOD Audio 面板显示同步提示和打开原生面板的入口。

关闭同步后，使用 FMOD Audio 面板编辑独立布局。默认文件不存在时，使用内存中的 ``Master``，首次编辑保存时创建文件。加载失败会报告错误并回退到 ``Master``；编辑器会保留错误状态，避免自动覆盖损坏的默认文件。

下文修改布局的代码示例使用独立模式。运行时修改配置会更新当前声音；写入文件需要调用 ``ResourceSaver.save()``。

FMOD Audio 面板
---------------

面板默认停靠在编辑器底栏，与 Audio 面板并列，可浮动并恢复保存的布局。音量推子、效果器勾选、右键菜单、拖放和撤销重做沿用原生 Audio 面板的操作方式。拖动音量时按住 Ctrl 可使用整数分贝步进。

顶部操作包括：

- **Add Bus**：添加总线
- **Load**：打开布局，保留项目默认布局设置
- **Save As**：另存当前布局
- **Load Default**：加载项目默认布局
- **Create**：创建并保存新布局
- **FMOD > Set as Default**：将当前布局设为项目默认值
- **FMOD > Create FMOD Layout from Godot**：转换 Godot 总线，保存为独立资源，并列出跳过的效果器

编辑器配置修改会在 0.8 秒后合并保存。保存失败时保留未保存状态。默认布局引用在保存后改用 UID，导出插件会包含默认布局及其依赖资源。

独立模式下，电平表显示检查器试听和编辑器内播放的 FMOD 音频，使用编辑器 Audio Buses 的渐变颜色和 tint 设置。峰值保持 1.5 秒，然后以每秒 60 像素回落；电平条以每秒 60 dB 回落。界面最多以 30 Hz 刷新，隐藏时停止轮询。独立游戏进程的电平暂未接入面板。

稳定 ID 与路由
--------------

``Master`` 的 ID 固定为 ``0``，始终位于首项。其他总线名称唯一，不能留空或包含逗号。总线 ID 和效果器槽位 ID 都不等于显示索引。

.. code-block:: gdscript

    func configure_buses() -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var sfx_id: int = layout.find_bus_id(&"SFX")
        if sfx_id == -1:
            sfx_id = layout.add_bus(&"SFX")
        if layout.find_bus_id(&"Footsteps") == -1:
            layout.add_bus(&"Footsteps", sfx_id)
        layout.set_bus_volume_db(sfx_id, -6.0)

发送目标可以位于列表中的任意位置。``set_bus_send()`` 拒绝发送给自身和产生环路的连接；``move_bus()`` 只调整显示顺序。删除总线时，发送到它的其他总线和正在播放的通道会转接到它原来的发送目标。

播放器的 ``bus`` 属性保存名称，检查器选项来自当前 FMOD 布局。未知名称在下次播放时回退到 ``Master``。重命名总线后，应同步修改播放器保存的名称；总线内部 ID 和已绑定的运行实例保持不变。

.. code-block:: gdscript

    @onready var music: FmodAudioStreamPlayer = $MusicPlayer


    func _ready() -> void:
        music.bus = &"Music"
        music.play()

音量、静音与独奏
----------------

``0.0`` dB 为单位增益，负值衰减，正值放大。通过布局修改这些参数会更新绑定的运行实例。

.. code-block:: gdscript

    func mute_music(muted: bool) -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var music_id: int = layout.find_bus_id(&"Music")
        if music_id != -1:
            layout.set_bus_mute(music_id, muted)


    func solo_voice(enabled: bool) -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var voice_id: int = layout.find_bus_id(&"Voice")
        if voice_id != -1:
            layout.set_bus_solo(voice_id, enabled)

有总线处于 Solo 状态时，该总线及其通向 ``Master`` 的路径保持可听，其他总线静音。布局保留各总线原有的 Mute 标记，退出 Solo 后恢复应用。

效果器配置与运行实例
--------------------

``add_bus_effect()`` 接收总线 ID，并返回稳定槽位 ID。同一个效果配置可以用于多个槽位，每个槽位拥有独立 DSP、Capture 缓冲、频谱和录音状态。修改配置参数会更新对应实例；调整顺序和移动槽位保留 DSP 状态及延迟、混响尾音。

.. code-block:: gdscript

    var capture: FmodAudioEffectCapture


    func _ready() -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var slot_id: int = layout.add_bus_effect(0, FmodAudioEffectCapture.new())
        FmodServer.flush_bus_updates()
        capture = FmodServer.get_bus_effect_instance(0, slot_id) as FmodAudioEffectCapture


    func _process(_delta: float) -> void:
        if capture != null and capture.can_get_buffer(256):
            var frames: PackedVector2Array = capture.get_buffer(256)
            print(frames[0])

使用 :ref:`FmodServer.get_bus_effect_instance()<class_FmodServer_method_get_bus_effect_instance>` 读取实时数据。``get_bus_effect()`` 返回布局中的配置资源。新增槽位后调用 ``flush_bus_updates()``，即可在同一帧读取运行实例。

``set_bus_effect_enabled()`` 控制单个槽位，``set_bus_bypass()`` 控制整条总线的受管效果。总线旁路和槽位禁用任一成立时，实例进入旁路。关闭临时效果时可保留槽位，避免重新分配 DSP。

切换与保存布局
--------------

.. code-block:: gdscript

    func activate_layout(path: String) -> Error:
        var layout: FmodAudioBusLayout = load(path) as FmodAudioBusLayout
        if layout == null:
            return ERR_INVALID_DATA
        return FmodServer.set_audio_bus_layout(layout)

``set_audio_bus_layout()`` 先验证配置、创建新实例，再替换当前布局。失败时保留当前布局；成功时将播放通道转移到同名总线，找不到时转到 ``Master``。同步模式返回 ``ERR_BUSY``。

切换布局与保存文件分别执行。保存时使用 ``ResourceSaver.save(layout, path)``；将布局设为项目默认值可通过 FMOD Audio 面板完成。资源仅保存配置，运行时总线、DSP 和实时音频数据由服务器管理。

直接控制运行时对象
------------------

``FmodServer.get_audio_bus(name)`` 和 ``get_audio_bus_by_id(id)`` 返回 :ref:`FmodAudioBus<class_FmodAudioBus>`。可用 ``get_bus()`` 取得底层 :ref:`FmodChannelGroup<class_FmodChannelGroup>`，用于低层播放和混音控制。

.. code-block:: gdscript

    func play_on_bus(sound: FmodSound, bus_name: StringName) -> FmodChannel:
        var bus: FmodAudioBus = FmodServer.get_audio_bus(bus_name)
        var group: FmodChannelGroup = bus.get_bus() if bus != null else FmodServer.get_master_channel_group()
        return FmodServer.get_main_system().play_sound(sound, group, false)

运行时对象的直接修改不会写回布局文件。总线 Solo、槽位开关和整条总线旁路应通过布局接口调整，以保持路由及各槽位状态一致。服务器管理的总线由服务器释放。

API 参考
--------

- :ref:`FmodAudioBusLayout<class_FmodAudioBusLayout>`：配置、路由与效果器槽位
- :ref:`FmodAudioBus<class_FmodAudioBus>`：运行时总线
- :ref:`FmodServer<class_FmodServer>`：布局切换和运行实例访问
- :doc:`dsp_effects`：效果配置、频谱和录音示例
