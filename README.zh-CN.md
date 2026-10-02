# Unity uGUI Layout Probe

这是一个**冻结的研究快照**：用 Python 对明确输入的 Unity uGUI 布局做实验性几何计算，并输出原创 JSON/PNG 演示。陌生开发者无需游戏、IPA/APK、Unity 安装或 Unity 工程即可运行。

```sh
uv run --with-requirements requirements.txt python demo.py
uv run --with-requirements requirements.txt python -m unittest discover -s tests -v
```

使用 Python 3.12。默认读取 `examples/layouts.json`，写入 `artifacts/demo/summary.json`、编号 PNG 和总览图；支持 `--input` 和 `--output`。几何核心仅用标准库，演示固定 `Pillow==12.3.0`，使用内置字体。

七种原创场景覆盖边界内、确定越界、旋转与镜像、祖先裁剪、显式运行时不确定、默认隐藏和不支持的 Canvas 模式。默认九个节点中八个成功计算、一个 UNKNOWN。越界场景的手算结果为右侧 15 像素、面积比例 0.75。

**尚未完成与 Unity 原生运行结果的系统性对照。确定性不等于正确性，静态越界不等于运行时缺陷，UNKNOWN 不表示通过。**程序不导入 IPA/APK 或 Unity 工程，不包含游戏素材、扫描器、Atlas、游戏适配器、补丁或安装工具。

A/B/C 仅对已计算的越界节点分诊：A 为输入声明可见且没有不确定因素，B 有显式不确定因素，C 隐藏、禁用、接近透明或预期行为。C 优先于 B。无越界的节点没有标签。无效几何单列 UNKNOWN；有效且完全裁掉的矩形仍计入成功计算。运行时状态由输入声明，不从脚本推断。

[英文首页](README.md)、[格式约定](docs/format.md)、[工程案例](docs/case-study.md)和[归属说明](THIRD_PARTY.md)提供完整边界。工程案例中的私有实测只是作者记录，不是公开可复现证据。

目前没有本项目买家、收入或已验证需求的证据。有限整理的价值在于可审查的实现、手算验证、对未知结果的诚实处理，以及具体复用。欢迎提交原创最小复现、反例和引用；不承诺持续开发，不因 Stars 或收入不足追加开发。
