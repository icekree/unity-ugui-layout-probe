# Attribution and provenance

- `geometry.py` is extracted from the author's private `tools/hornyvilla_ui_geometry.py` at snapshot `fe1264b2115f6e96cbe35d401bd9877a0ba92004`, with input validation added. The public repository starts new history and distributes no game-owned content.
- `demo.py`, tests, JSON fixtures, generated overview and documentation are original project work. Code, fixtures and documentation use the MIT license in `LICENSE`.
- Layout behavior is informed by Unity's [Basic Layout specification](https://docs.unity3d.com/Packages/com.unity.ugui@2.0/manual/UIBasicLayout.html) and [Canvas Scaler documentation](https://docs.unity3d.com/Packages/com.unity.ugui@2.0/manual/script-CanvasScaler.html). For formula comparison, see [Unity uGUI CanvasScaler.cs at a fixed revision](https://github.com/Unity-Technologies/uGUI/blob/9b8c5df053bf9a235c673b9bf4a549e573f2a279/com.unity.ugui/Runtime/UGUI/UI/Core/Layout/CanvasScaler.cs). These are specification/source references, not bundled Unity code. This implementation is not affiliated with or endorsed by Unity.
- TRS/quaternion mathematics and Sutherland–Hodgman convex clipping are standard algorithms. No new algorithm or ownership of those mathematical ideas is claimed.
- [Pillow 12.3.0](https://pillow.readthedocs.io/en/stable/about.html) is the demo's separately installed dependency, licensed under MIT-CMU. Its bundled default font is used through `ImageFont.load_default`; no host font or game font is copied into the repository. Pillow and its bundled components retain their upstream attribution and licenses.
- [UnityPy](https://github.com/K0lb3/UnityPy) is mentioned as an existing parser; no UnityPy code is included or required.

The MIT grant applies to this project's own material, not to Unity trademarks, third-party software or any private game resources.
