# API 文档核对记录

日期：2026-10-28

## 范围与依据

核对全部 47 个已注册类的 XML 和中文类参考，对照 C++ 绑定、实现、ClassDB 快照及必要的 FMOD 2.04 官方说明。范围包括 817 个方法、421 个属性、325 个常量和 11 个信号。

修正了 37 个类中的 223 处描述，包括上一轮 `create_system()` / `init()` 的修正。中文目录新增 239 条、修正 207 条消息，清理 404 条失效消息，覆盖参数说明错位、错误单位、返回字典字段遗漏和仍为英文的访问器说明。接口签名保持不变。

`FmodAudioStreamFLAC.xml` 已删除：该类没有实现或注册，发布清单和 ClassDB 中也不存在。FLAC 文件仍由 `FmodAudioStream` 和 FMOD 导入器处理。

## 主要文档修正

- 创建实例、初始化、指针非空和可用句柄的区别
- 内存音频的持有方式、锁定数据返回副本及声音组释放行为
- DSP 输入/输出、淡化点、录音设备和版本查询的字典键及数据类型
- 几何旋转的弧度单位、混响的 Hz/百分比单位、效果器的范围和默认值
- 暂停仍属于活动播放；替换音频流会停止播放；总线变更在创建新通道时生效
- `MODE_STREAM` 从内存中的完整源数据流式解码，不直接从磁盘读取
- 自定义 DSP 的实际算法，以及仅保存设置或尚未实现的选项
- Android 导出工具的菜单名、压缩包输入和实际模板修改内容

播放器和总线行为另外用当前 Windows 插件进行了隔离运行核对。XML 通过生成器与 ClassDB 检查，中文翻译按新生成的 gettext 消息合并；中英文构建检查规范锚点和本地链接。

## 实现缺陷与待验证风险

初次核对只修改文档。随后已修复混音矩阵缓冲、独奏绑定、父级传递，以及 3D 距离滤波、关闭衰减、角度检查器单位和声音组取消限制；其余项目仍为后续实现工作。

### 已确认的绑定或行为问题

| API | 当前问题 | 实现位置 |
| --- | --- | --- |
| `FmodAudioBus.is_solo()` | **已修复**：脚本方法和 `solo` 属性均读取独奏标志，不受静音标志影响 | `src/mixer/fmod_audio_bus.cpp::_bind_methods` |
| `FmodAudioBusLayout.create_audio_bus(name, parent)` | **已修复**：提取父总线通道组后设置原生路由；未初始化或已释放的父级会在创建前被拒绝 | `src/mixer/fmod_audio_bus_layout.cpp::create_audio_bus` |
| `FmodAudioStreamPlayer3D.attenuation_filter_db` | **已修复**：使用 `1 - pow(10, db / 20)` 转换为原生滤波量；0 dB 旁路，负值增强滤波 | `src/nodes/fmod_audio_stream_player_3d.cpp::_apply_attenuation_settings` |
| `FmodAudioStreamPlayer3D.ATTENUATION_DISABLED` | **已修复**：使用恒定增益的自定义衰减曲线，保留其他 3D 设置 | 同上 |
| `FmodAudioStreamPlayer3D.emission_angle` | **已修复**：检查器直接显示度数，范围与 setter 的 0–90° 一致，场景保存值不变 | `src/nodes/fmod_audio_stream_player_3d.cpp::_bind_methods` |
| `FmodSoundGroup.set_max_audible()` | **已修复**：方法和属性接受 `-1` 取消限制，保留 `0` 的语义；小于 `-1` 的值会被拒绝且不改变当前限制 | `src/playback/fmod_sound_group.cpp::set_max_audible` |

表中六项均已在 Windows 插件中完成修复并通过回归。发声锥衰减的检查器范围也已与 setter 的 -80–0 dB 一致。

### 尚未接通或未生效的功能

- `FmodSound` 的 PCM read、PCM set-position 和 nonblock 回调 setter 只保存 Callable，当前工厂没有注册对应原生回调
- `FmodSoundLock` 返回复制后的字节数组，没有写回原始 PCM 的公开接口
- 3D rolloff 回调仅在主线程调用脚本，其他线程返回 `1.0`；回调目标还受单个静态系统指针限制
- 播放器的 `area_mask`、2D 播放器的 `max_polyphony` 没有参与当前播放逻辑
- Compressor 的 `sidechain`、Distortion 的 `oversample`、SpectrumAnalyzer 的 `buffer_length` 没有实现原文档所承诺的处理
- Record 的 `FORMAT_IMA_ADPCM` 当前导出 16-bit PCM
- Filter 目前只应用低通；18 dB 选项使用 24 dB 实现

### 混音矩阵缓冲：已修复

FMOD 的矩阵行列参数会返回实际尺寸，不能用调用方传入的尺寸限制写入容量。原分配还没有覆盖带填充的行步长。

`FmodDSPConnection.get_mix_matrix()` 现使用最大通道宽度的独立缓冲区接收数据，再复制到验证过的目标布局。返回数组包含完整行步长，填充和未使用区域为零；尺寸不足会返回空数组并报告错误。DSPConnection 和 ChannelControl 的 setter 均在计算长度前验证通道数与步长，防止短数组读取和整数乘法溢出。最后一行不强制携带无效填充。

实现位置：`src/dsp/fmod_dsp_connection.cpp`、`src/playback/fmod_channel_control.cpp`。

### 回归验证

`tests/regression/mix_matrix_test.gd` 和 `audio_bus_test.gd` 共 79 项检查，已加入 `routing`、`regression` 和 `all` 套件。覆盖大步长、32×32 矩阵、过小目标、短数组、异常大整数、独奏/静音独立性、多级父子路由与无效父级。Windows 优化 Debug/PDB 构建、编辑器导入、完整回归及 `all -Quick` 已通过。

命令：`tools/run_tests.ps1 -Suite routing`。日志及 JSON 结果位于 `tests/logs/runs/`，编译日志位于 `tests/logs/builds/`。

### 3D 空间音频：已修复

`tests/regression/spatial_audio_test.gd` 的 57 项检查已加入 `spatial`、`regression` 和 `all` 套件，覆盖播放前赋值、运行时更新、dB/频率边界、距离增益、模式切换、播放器相互独立、原生锥角、检查器范围和场景保存往返。

使用 `CHANNEL_DISTANCEFILTER` 和离线双音 PCM 测量实际输出：关闭衰减后，距离 0.5 和 1000 的 RMS 均为约 0.24998；原实现远处仅约 0.00025。滤波从 0 dB 改为 -24 dB 后，RMS 约为 0.06014，恢复 0 dB 后返回原值。原生滤波量 0 和 1 的对照输出分别约为 0.24998 和 0.05342，因此转换方向依据本机 FMOD 2.04 实际输出验证。项目需在系统初始化前启用 `audio/fmod/init_flags/channel_distance_filter` 并重新运行，手动测试项目已启用。

Windows 优化 Debug/PDB 构建、编辑器导入、完整回归、`all -Quick` 和编辑器生命周期测试已通过。命令：`tools/run_tests.ps1 -Suite spatial`。本轮日志位于 `tests/logs/runs/spatial_*`，中英文文档构建日志位于 `tests/logs/runs/spatial_docs/`。

### SoundGroup 取消限制：已修复

2026-10-29：`FmodSoundGroup.set_max_audible()` 仅拒绝小于 `-1` 的值，方法和 `max_audible` 属性均可用 `-1` 取消限制，`0` 仍表示不允许可听播放。

`tests/regression/sound_group_test.gd` 的 25 项检查已加入 `smoke`、`regression` 和 `all`。覆盖新原生组的默认值、方法与属性、无效负数保留原限制，以及实际播放从上限 1 切换到不限量后同时保留 6 个实例、从 0 恢复播放和重新设定有限上限。修复前 13 项失败；Windows 优化 Debug/PDB 构建、编辑器导入和修复后的完整回归均通过。

命令：`tools/run_tests.ps1 -Suite smoke`。结果位于 `tests/logs/runs/sound_group_*/sound_group_regression.json`，文档构建日志位于 `tests/logs/runs/sound_group_docs/`。

## 后续修复顺序

按需求补齐尚未实现的回调与 DSP 功能。

涉及运行时语义变化后，需重新导出接口快照，更新本记录中的限制，并复测对应音频场景。
