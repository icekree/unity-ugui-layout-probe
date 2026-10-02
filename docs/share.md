# Prepared sharing copy and portfolio text

These materials are prepared for sharing; they have not been posted to a community. Use the exact revision being discussed. Code release: [v0.1.1](https://github.com/icekree/unity-ugui-layout-probe/releases/tag/v0.1.1); later tutorial and presentation additions are on `main`.

## English short post

How would you verify a Unity RectTransform overflow measurement without opening Unity?

I published Unity uGUI Layout Probe: a frozen experimental Python geometry reference with seven original JSON/PNG scenes. One 20-pixel box spans x=95..115 in a 100-pixel viewport: right overflow is 15 pixels and outside area ratio is 0.75, checkable by hand. The tutorial includes a runnable standard-library reuse example. Invalid geometry and unresolved parents stay UNKNOWN. A post-publication review led to three reproduced input/output fixes and 25 passing regression/analytical tests.

Native Unity parity remains unverified; static overflow is not a runtime defect. Concrete synthetic counterexamples, reuse and citations are welcome.

Code and tutorial: https://github.com/icekree/unity-ugui-layout-probe

## 中文短帖

Unity RectTransform 的越界距离，怎样不用打开 Unity 就能手算并核对？

我整理了一个冻结的实验性 Python 几何参考实现：七种原创 JSON/PNG 场景，无需游戏或 Unity。20 像素宽的矩形横跨 x=95..115，视口宽 100，因此右侧越界 15 像素、屏幕外面积比例 0.75。教程给出完整输入和仅用标准库的复用示例；无效几何、无法解析的父级保留 UNKNOWN。发布复核发现的三个输入／输出问题已复现修复，25 项测试通过。

尚未系统对照 Unity 原生结果，静态越界不等于运行时缺陷。欢迎原创反例、具体复用和引用。

代码与教程：https://github.com/icekree/unity-ugui-layout-probe

## Portfolio description

**Unity uGUI Layout Probe — icekree.** Extracted a small Python geometry core from a private layout investigation and turned it into a publicly reproducible MIT reference. It combines CanvasScaler formulas, hierarchy transforms, rotated/mirrored polygons and ancestor clipping with explicit unknown results. Original fixtures include a hand-checkable 15-pixel / 0.75 overflow example. A bounded case separates version identity, object changes and ZIP differences. Post-publication review issues were independently reproduced and fixed, with 25 tests and Linux CI. Added a reuse tutorial and versioned citation metadata. Scope remains explicit JSON and experimental geometry; no native Unity parity, buyer or adoption claim is made.

**作品集介绍：**将一次私有布局调查中可复用的几何核心，整理成可公开运行、审查和借用的 MIT 参考实现。包含 CanvasScaler、父子变换、旋转／镜像、祖先裁剪与显式 UNKNOWN；原创场景提供 15 像素、0.75 面积比例的手算验证。工程案例区分版本、对象及 ZIP 差异证据。发布复核中的三个问题经独立复现后修复，25 项测试和 Linux CI 通过，并补充复用教程及版本引用。作者 icekree；范围限定为明确 JSON 上的实验性几何，不宣称 Unity 原生一致性或商业采用。

## Reproducible preview

The [social preview](social-preview.png) is an original schematic, not a Unity capture. Its inset scales a 100×100 viewport and the x=95..115 rectangle by three; numeric labels refer to the original scene's pixels. Rebuild it from the repository root:

```sh
uv run --with-requirements requirements.txt python tools/render_social_preview.py
```

The renderer uses Pillow's bundled default font and no external artwork. The checked-in image is 1280×640 PNG, under 1 MB.
