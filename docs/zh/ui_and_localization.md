# 🖥️ 桌面图形界面与动态国际化 (i18n) 架构

本文档介绍 **SYNTHETIC** 基于 CustomTkinter 与 TkinterMapView 构建的桌面客户端架构，以及运行时多语言动态切换技术。

⬅️ [文档中心](README.md) | 🏛️ [系统架构规范](architecture.md) | 🗺️ [空间拓扑](spatial_and_environment.md) | ⚡ [API 参考](api_reference.md)

---

## 1. 模块化前端架构

基于 **CustomTkinter** 现代化 UI 框架：
* 高度解耦的组件设计：地图输入区、传感器数据源复选、参数调节、传感器破坏率设置及语言切换。
* 后台异步线程：计算流水线运行于独立工作线程，通过 `root.after(0, ...)` 向主线程推送遥测进度，绝不导致前端界面假死。

---

## 2. 交互式地图布点窗口 (`ui/map_selector.py`)

* **自动视野居中：** 自动适配 `.osm` 文件的地理边界。
* **交互式选点：** 红色图钉代表 LPR 视觉电警抓拍机，蓝色图钉代表埋入式地感线圈。
* **配额动态提示：** 实时提示用户待布设的线圈与相机数量。

---

## 3. 动态国际化引擎 (i18n)

实现**应用无需重启、瞬时动态切换全套 UI 语言**：
* **单例 `Translator` (`ui/translator.py`)：** 自动读取 `ui/locale/` 字典（包含 `en`、`pt-br`、`es`、`fr`、`ru`、`zh-cn`）。
* 下拉菜单触发 `SyntheticApp.update_ui_texts()`，瞬时覆写全局各组件标题、按钮及弹窗文本。

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>
