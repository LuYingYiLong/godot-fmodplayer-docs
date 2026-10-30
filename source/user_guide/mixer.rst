.. _mixer:

混音系统
============

:ref:`FmodAudioBusLayout<class_FmodAudioBusLayout>` 保存配置，:ref:`FmodServer<class_FmodServer>` 管理运行时总线和 DSP。将声音送到 ``Music``、``SFX`` 或 ``Voice`` 后，可按类别调整音量、静音和效果。

同步模式与独立模式
----------------------

.. list-table::
   :header-rows: 1

   * - 项目设置
     - 默认值
     - 作用
   * - ``audio/fmod/sync_godot_audio_buses``
     - ``true``
     - 从 Godot AudioServer 同步总线与支持的效果器
   * - ``audio/fmod/default_bus_layout``
     - ``res://default_fmod_bus_layout.tres``
     - 独立模式的启动布局

修改同步开关后重新加载项目。同步模式通过原生 Audio 面板编辑，FMOD Audio 面板显示提示和原生面板入口。独立模式通过 FMOD Audio 面板或布局 API 编辑，下文代码使用独立模式。

编辑器面板与保存
--------------------

FMOD Audio 默认位于编辑器底栏，可浮动并恢复布局。音量推子、效果器勾选、拖放、右键菜单和撤销重做沿用原生 Audio 的操作；按住 Ctrl 拖动音量使用整数分贝步进。

- **Add Bus** 添加总线；**Create** 创建并保存新布局。
- **Load** 打开布局，**Save As** 另存，**Load Default** 加载项目默认布局。
- **FMOD > Set as Default** 将当前布局设为项目默认值。
- **FMOD > Create FMOD Layout from Godot** 转换并保存独立布局，同时列出跳过的效果器。

编辑器修改在 0.8 秒后合并保存，失败时保留未保存状态。打开其他布局不会更换项目默认值。默认引用保存为 UID，导出插件会包含默认布局及其依赖。默认文件缺失时先使用内存 Master，首次编辑保存时创建文件；损坏文件会显示错误并阻止自动覆盖。

总线 ID 与发送路由
--------------------------

Master 的稳定 ID 为 ``0``，始终位于首项。其他名称必须唯一、非空且不含逗号。ID 与显示索引分别管理，排序和改名会保留运行实例。

.. code-block:: gdscript

    func create_sfx_route() -> void:
        var layout: FmodAudioBusLayout = FmodServer.get_audio_bus_layout()
        var sfx_id: int = layout.find_bus_id(&"SFX")
        if sfx_id == -1:
            sfx_id = layout.add_bus(&"SFX")
        if layout.find_bus_id(&"Footsteps") == -1:
            layout.add_bus(&"Footsteps", sfx_id)
        layout.set_bus_volume_db(sfx_id, -6.0)

``set_bus_send()`` 可发送到任意无环目标，拒绝自身发送；``move_bus()`` 只改变显示顺序。删除总线时，进入该总线的其他总线和播放通道转接到原发送目标。

播放器的 ``bus`` 属性保存名称，选项来自当前布局。重命名总线后需同步更新播放器；未知名称在下次播放时回退到 Master，修改属性不会重新路由已有通道。

音量、Mute 与 Solo
--------------------------------

通过 ``set_bus_volume_db()``、``set_bus_mute()`` 和 ``set_bus_solo()`` 修改配置。音量使用分贝，``0.0`` 为单位增益。Solo 保留选中总线及其到 Master 的发送路径可听；退出 Solo 后恢复应用保存的 Mute 标记。

效果器槽位
--------------

``add_bus_effect()`` 返回稳定槽位 ID。共享配置的槽位各有独立运行实例，参数修改更新现有 DSP，排序和跨总线移动保留其状态。``set_bus_effect_enabled()`` 控制单个槽位，``set_bus_bypass()`` 控制整条总线的受管效果。

``get_bus_effect()`` 返回配置资源。Capture、SpectrumAnalyzer 和 Record 的实时数据通过 ``FmodServer.get_bus_effect_instance()`` 读取，示例见 :doc:`dsp_effects`。

切换布局与运行时对象
------------------------

.. code-block:: gdscript

    func activate_layout(path: String) -> Error:
        var layout: FmodAudioBusLayout = load(path) as FmodAudioBusLayout
        if layout == null:
            return ERR_INVALID_DATA
        return FmodServer.set_audio_bus_layout(layout)

``set_audio_bus_layout()`` 先验证并创建新实例，成功后替换当前布局；失败时保留原布局，同步模式返回 ``ERR_BUSY``。播放通道移到同名总线，找不到时移到 Master。运行时修改写入文件需单独调用 ``ResourceSaver.save()``。

布局修改在下一次服务器更新时应用，``flush_bus_updates()`` 可立即应用。通过 ``get_audio_bus()`` 或 ``get_audio_bus_by_id()`` 获取运行时总线。直接修改运行对象不会写回配置；服务器管理其释放。

编辑器电平
--------------

独立模式下，面板显示检查器试听与编辑器内播放的电平，沿用编辑器 Audio Buses 的颜色和 tint。峰值保持 1.5 秒后以每秒 60 像素回落，电平条以每秒 60 dB 回落。界面最多 30 Hz 刷新，隐藏后停止轮询。独立游戏进程的电平暂未接入。
