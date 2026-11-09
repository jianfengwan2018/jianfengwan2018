# 大化春秋 / 化学实验游戏

本项目继续在原 GitHub 仓库中开发。原 Godot 工程、HTML5 旧版、地图素材和提交历史均保留。

## 找版本

- [版本记录](CHANGELOG.md)：按时间查看每一版及其固定提交。
- [版本清单](releases/index.json)：版本号、归档时间、源提交、GitHub 提交与目录的对应关系。
- [版本管理规范](VERSIONING.md)：如何提交、打标签、保留同一版本的不同时间快照和恢复旧版。
- [HTML5 v12 道路试玩版](web-demo/html5-v12-roads-pass-2026-11-05/README.md)：已归档的道路、音乐、天气版本。
- [HTML5 v6 早期试玩版](web-demo/html5-v6-2026-11-05/README.md)：保留的早期版本。
- [校园地图素材归档](maps/campus-2026-11-07/README.md)：图像资料，不能当作完整游戏发布。

**截至 2026-11-09 本次核查，R25 的完整程序尚未归档到本仓库 main。** 已有托管源提交为 `c8c5dc2dfe73b4f7b0e22181519f5703275b1d42`。它与 GitHub 的提交编号不同，不能用 v12 或地图素材目录代替 R25。清单中的 `pending_archive` 表示待完成，不表示已发布。

## 运行 HTML5 旧版

无需构建或安装前端依赖。在仓库根目录运行：

```sh
python3 -m http.server 8000 --directory chemistry-lab-game/web-demo/html5-v12-roads-pass-2026-11-05/dist
```

浏览器访问 http://localhost:8000 。各版功能、测试结果及素材限制以其目录中的 README、QA 和 ATTRIBUTION 为准。

## 原 Godot 工程

使用 Godot 4 标准版（GDScript），Compatibility 渲染器。

1. 安装 [Godot 4.3 或更新的 Godot 4 稳定版](https://godotengine.org/download/)。
2. 克隆或下载本仓库。
3. 在 Godot 项目管理器中导入本目录的 `project.godot`。
4. 按 F6 运行当前场景或 F5 运行项目。

```sh
godot --path chemistry-lab-game --editor
godot --headless --path chemistry-lab-game --editor --quit
```

Godot 工程仍是初始标题场景，实验玩法尚未实现。HTML5 试玩版是独立实现，不是 Godot Web 导出。本次只整理版本管理，没有重跑 Godot 或游戏运行测试。

## 校验归档

Python 3.10+，仅用标准库。从仓库根目录运行：

```sh
python3 chemistry-lab-game/tools/check_versions.py
python3 -m unittest discover -s chemistry-lab-game/tools -p 'test_*.py'
```

第一条会逐文件检查已有归档的字节数、SHA-256 和 Git blob SHA；需要完整克隆的资源文件。检查通过只表示归档文件匹配清单，不表示游戏所有功能通过测试。
