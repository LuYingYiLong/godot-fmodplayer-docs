快速开始
============

安装完成后，将音频导入为 ``FmodAudioStream``，赋给播放器节点即可播放。安装步骤见 :doc:`installation`。

导入音频
------------

#. 将音频文件放入项目，在文件系统面板选中它。
#. 在导入面板将 **导入为** 改为 **FMOD Audio**。
#. 音乐选择 **Stream (Low memory)**；短音效选择 **Sample (High quality)**；循环短音效选择 **Loop Sample**。
#. 点击 **重新导入**。

创建播放器
--------------

#. 新建场景，以 ``Node`` 为根节点，添加 ``FmodAudioStreamPlayer`` 子节点。
#. 将导入后的音频拖到播放器的 **Stream** 属性，**Bus** 保持 ``Master``。
#. 展开 Stream 资源，使用波形下方的播放按钮试听；点击波形可跳转。
#. 启用播放器的 **Auto Play**，按 F6 运行当前场景。

``FmodAudioStreamPlayer2D`` 和 ``FmodAudioStreamPlayer3D`` 分别用于 2D 和 3D 位置音频，见 :doc:`../user_guide/playback`。

用脚本控制
--------------

将以下脚本挂到根节点，保留已设置的 Stream，关闭 Auto Play：

.. code-block:: gdscript

    extends Node

    @onready var player: FmodAudioStreamPlayer = $FmodAudioStreamPlayer


    func _ready() -> void:
        player.play()


    func _unhandled_input(event: InputEvent) -> void:
        if event.is_action_pressed(&"ui_accept"):
            player.stream_paused = not player.stream_paused
        elif event.is_action_pressed(&"ui_cancel"):
            player.stop()
        elif event.is_action_pressed(&"ui_up"):
            player.volume_db = minf(player.volume_db + 3.0, 0.0)
        elif event.is_action_pressed(&"ui_down"):
            player.volume_db = maxf(player.volume_db - 3.0, -60.0)

Enter 或空格切换暂停，Esc 停止，上下方向键调整音量。再次播放调用 ``play()``。暂停保留位置，停止后再播放从头开始。

.. list-table::
   :header-rows: 1

   * - 属性
     - 作用
   * - ``stream``
     - 要播放的音频资源
   * - ``volume_db``
     - 分贝音量，``0.0`` 为单位增益
   * - ``pitch_scale``
     - 音高与速度倍率，``1.0`` 为原速
   * - ``stream_paused``
     - 暂停或恢复当前播放
   * - ``bus``
     - 目标总线名称，默认为 ``Master``

试听与总线面板
------------------

项目默认同步 Godot 音频总线。同步开启时，在原生 Audio 面板管理总线；FMOD Audio 面板显示同步提示。需要独立布局与编辑器内 FMOD 电平时，关闭 ``audio/fmod/sync_godot_audio_buses`` 并重新加载项目，详见 :doc:`../user_guide/mixer`。

继续阅读
------------

- :doc:`../user_guide/audio_resources`：加载模式、预加载和资源复用
- :doc:`../user_guide/playback`：重叠播放、跳转、循环和空间音频
- :doc:`../user_guide/mixer`：布局、路由和音量控制
- :doc:`../user_guide/dsp_effects`：效果器、捕获、频谱和录音
- :doc:`../user_guide/faq`：加载、无声和导出问题
