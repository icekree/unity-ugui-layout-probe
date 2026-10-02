# From a private layout investigation to a bounded reference

This case documents a workflow, not a publicly reproducible game analysis. The public experiment contains original rectangles only. The source extraction is pinned to author-owned private snapshot `fe1264b2115f6e96cbe35d401bd9877a0ba92004`; no private Git history, archives, assets, signing details or installation logs are distributed.

## Engineering question

During a private iOS game investigation, the author needed to separate static RectTransform overflow candidates from hidden screens, expected movement and runtime layout uncertainty. Resource parsing alone did not settle the geometry or establish what a player would actually see. The reusable part was small: compute a hierarchy, preserve unknown results and verify the scope of changes.

Existing parsers such as [UnityPy](https://github.com/K0lb3/UnityPy) already address resource decoding. This reference deliberately accepts explicit JSON and does not compete as a new archive parser. Standard TRS matrices, Unity layout specifications and convex polygon clipping supply the mathematical ingredients; the engineering contribution is composing them with a visible failure contract and reviewable evidence.

## Three levels of evidence

1. **Version identity:** Record input archive/content hashes and the exact implementation revision before inspecting or changing anything. A filename or claimed game version is insufficient. Preserve a recovery artifact separately; this repository contains none.
2. **Object difference:** Compare decoded objects by stable identity and enumerate every field change. Geometry candidates alone do not authorize modifying a resource. Confirm expected fields changed and unrelated objects did not.
3. **ZIP difference:** Compare entry names, uncompressed entry hashes and archive structure. ZIP bytes can differ because of compression or metadata even when entry contents match. Separately identify payload, signature and packaging changes; do not mistake a repackaged archive for a narrowly scoped semantic change.

These checks bound what changed. They do not prove runtime correctness, native-layout equivalence, installation success or an absence of defects.

## Private observations — author records only

The historical private report enumerated 7,431 RectTransforms, with an old handled count of 2,884 and unresolved count of 4,547. Its grouped window candidates were A=0, B=34 and C=6. The old implementation marked a node handled before calculation succeeded, so 2,884 must not be presented as successful geometry. The 34 B windows were uncertain candidates, not 34 confirmed bugs, users or fixes.

The author recorded local tests and repeated report generation on a retained private input. The game archive, decoded objects and runtime captures are not published. Readers cannot reproduce those private observations from this repository, and they are not evidence of demand, revenue or native Unity parity.

## Publicly reproducible result

The public extraction keeps the geometry core and adds finite-value checks, explicit JSON inputs, Pillow rendering and original fixtures. Successful calculation and unknowns are counted separately. Entirely clipped valid geometry is distinguished from invalid geometry. The default fixture's 15-pixel overflow and 0.75 outside ratio can be checked by hand; tests also exercise rotation, mirroring, clipping, tolerance and failed-parent propagation.

Linux Python 3.12 CI runs these public tests and the demo. Two runs in one environment must yield identical JSON/PNG bytes without changing input bytes. This establishes repeatability and agreement with selected analytical expectations. A systematic native Unity comparison remains undone, so the project is an experimental reference, not a certified validator.

## Value and stopping rule

The evidence supports a finite technical portfolio artifact: another developer can inspect, reproduce, challenge or borrow a small implementation. There is no verified buyer, revenue or adoption evidence for this project. Commercial neighboring tools do not establish willingness to pay for this code.

Useful recognition means a concrete reproduction, analytical counterexample, code reuse or citation. Stars and traffic are secondary signals. This frozen snapshot promises no game update support, general importer, paid product or continued development. Feedback may be recorded without reopening the project.
