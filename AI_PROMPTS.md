# Agent 交互日志

**团队名称：** [请填写团队名称]
**成员名单：** [请填写成员名单]
**使用的 AI Coding Agent 工具：** Claude Code (CLI)

---

## 🤖 交互记录（2026-05-10）

本次会话使用 Claude Code CLI，以下是对整个开发过程的完整交互记录。

### 1. 项目需求理解

**User Prompt:**
> 读取 README.md 理解需求，用 Python pandas 读取 API 数据，HTML 做网页

**Agent Response:**
- 读取了 README.md，确认了比赛要求：5G 信号数据可视化看板
- 检查了现有代码骨架（app.py 仅为 Streamlit 空壳）
- 确认了数据字段：Latitude, Longitude, CellID, Band, RSRP_dBm, SINR_dB, TerminalType, Download_Mbps
- 决定使用 Streamlit + pydeck + Plotly 实现

### 2. 构建核心看板

**User Prompt:**
> 主体使用 python，用 pandas 读取 API 数据，网页可以用 html

**Agent Response:**
- 使用 pandas 读取 data/signal_samples.csv
- 实现 pydeck 交互式散点地图，RSRP 信号强度颜色映射（> -90dBm 绿色，< -110dBm 红色）
- 添加 Plotly 各频段基站数量柱状图 + 终端类型分布饼图
- 侧边栏筛选器：频段多选、RSRP 范围滑块、终端类型多选
- 3D 地图模式（勾选后信号点以柱状图立起，高度对应下载速率）
- 地图 tooltip 显示详细数据
- 数据预览折叠面板，含指标卡

### 3. 单元测试

**User Prompt:**
> 自动完成 - 创建单元测试

**Agent Response:**
- 创建 test_app.py，包含 7 个测试用例：
  - test_data_loading: 验证 CSV 加载和字段完整性
  - test_rsrp_color: 验证颜色映射逻辑（强信号绿、弱信号红）
  - test_rgba_to_hex: 验证 RGBA 转十六进制颜色
  - test_approx_district: 验证行政区近似映射
  - test_filter_logic: 验证筛选逻辑正确性
  - test_band_distribution: 验证频段分布
  - test_terminal_type_distribution: 验证终端类型分布
- 将 rsrp_color 提取到 utils.py，避免测试时引入 Streamlit 依赖

### 4. 数据预览优化 + 行政区信息

**User Prompt:**
> 1. 数据预览中 color 用实际颜色显示，height 仅画图用不显示
> 2. 经纬度旁添加所属上海行政区

**Agent Response:**
- 将 color 列转为 SVG 色块（ImageColumn），替换 RGBA 数字
- 隐藏 height 列（仅 3D 地图内部使用）
- 列名汉化：纬度、经度、行政区、小区ID、频段...
- 实现行政区识别：
  - 优先加载 Nominatim API 精确缓存
  - 离线时使用最近邻中心点近似算法
- 侧边栏增加"行政区"筛选器
- 地图 tooltip 增加区信息
- 创建 precompute_districts.py 用于批量精确查询

### 5. 兼容性修复

**User Prompt:**
> 运行报错：AttributeError: module 'streamlit.column_config' has no attribute 'ColorColumn'

**Agent Response:**
- 定位问题：Streamlit 1.57.0 无 ColorColumn
- 改用 ImageColumn + Base64 SVG 色块渲染
- 创建 color_swatch() 函数

### 6. PowerShell 中文乱码修复

**User Prompt:**
> PowerShell 界面中文乱码，帮我查原因并修复

**Agent Response:**
- 诊断：编码已设为 UTF-8 (65001)，但终端字体 Lucida Console 不包含中文字形
- 将 PowerShell 控制台字体改为 Microsoft YaHei
- 修改 HKCU:\Console 注册表对应配置

### 7. 暗色/亮色主题切换

**User Prompt:**
> 给网页加上暗色和亮色两个主题颜色可以给用户选择

**Agent Response:**
- 侧边栏底部添加"🎨 主题"选择器（亮色/暗色）
- 实现暗色模式 CSS：背景 #0e1117、卡片 #1a1d24、文字 #e0e0e0
- pydeck 地图跟随切换 Carto light/dark 底图样式
- Plotly 图表跟随切换 plotly / plotly_dark 模板
- 覆盖了 metric、dataframe、expander、selectbox 等组件的暗色样式

### 8. Git 标签与推送

**User Prompt:**
> 根据 README 要求 tag 并 push 到远端（多次）

**Agent Response:**
- 首次提交 commit: 5151cc9，创建 basic-done 和 advanced-done 标签
- 第二次提交（暗色主题），更新 tags 并推送到 GitHub

---

## 📋 文件清单

| 文件 | 说明 |
|------|------|
| app.py | Streamlit 主应用（地图、图表、筛选器、预览） |
| utils.py | 工具函数（RSRP 颜色、行政区映射） |
| test_app.py | 7 个单元测试 |
| precompute_districts.py | 批量行政区精确查询脚本 |
| requirements.txt | 依赖：streamlit, pandas, pydeck, numpy, plotly, geopy |
| data/signal_samples.csv | 500 条 5G 路测数据 |

## ✅ 完成关卡

- **基础关卡**：pandas 数据加载 ✅ / 信号散点地图（RSRP 颜色） ✅ / 频段柱状图+终端饼图 ✅
- **进阶关卡**：侧边栏联动筛选 ✅ / 3D 地图（柱高度=下载速率） ✅ / 单元测试 ✅

---

*(本日志由 Claude Code CLI 会话自动生成，记录了完整的代码构建过程。)*
