# Limited standalone Game content

The SDV Lab feasibility proof uses a cooked **Game** target and Town10HD_Opt,
not an Unreal Editor installation. Its required ego vehicle is Lincoln MKZ;
the map, referenced assets, collision/GNSS sensors and maneuver support remain
in the package. Do not delete assets merely because their filename does not
mention the selected map: references are transitive.

## Prop catalogue projection

The full source `PropParameters.json` may advertise props that a single-map
cook has not emitted. Loading this full catalogue in that smaller package
produces missing-package errors. Keep the source catalogue intact and create
an explicit **package-local** subset after cooking, before signing:

```sh
python3 Util/BuildTools/standalone_content_profile.py \
  --catalogue PATH_TO_FULL/PropParameters.json \
  --cooked-content PATH_TO_COOKED/CarlaUnreal/Content \
  --output PATH_TO_NEW_OUTPUT/PropParameters.json \
  --report PATH_TO_NEW_OUTPUT/prop-profile.json
```

Both output files must be new. The report records source/output digests and
every excluded entry. Review it against the scenario's required props before
placing the projected file in the candidate package. Never interpret exclusions
as repaired assets, silently replace the full source catalogue, or sign before
the final package bytes are assembled. An interrupted invocation can leave a
partial output; reconcile it instead of blindly repeating or overwriting it.

For the 25 September 2026 one-map proof, 34 of 82 advertised props were cooked;
48 exclusions are explicitly inventoried. The source-controlled helper
reproduces the tested candidate's catalogue byte for byte. This helper does not
claim to build, sign or install the full distribution.

## Required qualification

- Verify the Game and matching Python API source pins and retained corrections.
- Launch outside the build/source tree with the original sandbox protections.
- Test the real Gateway/control path, physics, telemetry, manual commands,
  Autopilot, Brake/Tire maneuvers, Return to road and orderly consumer-first stop.
- Identify the start location geometrically. Editor and cooked packages can
  enumerate identical spawn points in different orders; a bare index is not a
  portable identity.
- Record first-profile and warm startup separately. Existing OS/Metal caches
  do not constitute clean-machine evidence.
- Check loaded dependencies, source-read exclusions, memory and disk bounds.
- Preserve residual map/material warnings in the report. A successful driving
  test does not qualify every static-mesh bounding box, prop or rendering mode.

The feasibility candidate is ad-hoc signed and measured on macOS 26.6.2 /
Apple Silicon. It is not a signed/notarized installer or an older-macOS support
claim. Portable Python/native helper closure and clean-host testing belong to
the subsequent distribution gates.

## Metal graphics compatibility

The original SM6-only package does not run on the qualification M1 Pro. The
pinned Unreal Metal implementation rejects SM6 on M1 and falls back to SM5;
that profile must actually be cooked into the package. The Mac target now lists
SM6 followed by SM5. Do not force SM6 past the hardware check or infer general
M1 acceptance from a successful cook.

The road master previously exceeded SM5's 16-sampler limit in the Asphalt B
and white/yellow lane-marking instances. The qualified compile proof changes
six sampler-source properties to shared wrap; it removes no texture or graph
node. `road_sampler_profile.py`, run through Unreal's Python commandlet,
reproduces/checks this content correction. It validates default and effective
instance texture addressing, filtering, group and non-virtual status before
editing. The first application saves only `M_RoadMaster`; a repeat verifies the
profile without rewriting it. A partial profile or incompatible texture fails
closed. Preserve the versioned content asset as the actual cook input; this
helper does not run during demo installation or launch.

Do not treat cooker exit code zero as sufficient shader acceptance. Reject
`Failed to compile Material`, `Default Material will be used in game` and
sampler-limit diagnostics. Require both Metal global shader caches, all scenario
assets and no diagnostic proof assets in the final inventory. Native M1 visual,
driving and sensor acceptance remains separate from the five-material SM5
compile proof. Geometry, vehicle physics, lane definitions and model thresholds
are outside this graphics correction.

## Native window handoff on the measured host

For the tested 2056 × 1224-point built-in workspace, the CARLA outer frame is
914 × 614 points. Its standalone AppKit title bar measures 32 points; therefore
the tested client resolution is `-ResX=914 -ResY=582`, not the old 592-pixel
height inferred from a 22-point Editor frame. Unreal preserves client aspect
ratio during resizing, so the wrong height also produces a narrower window.
Measure the frame again on a different OS/display configuration rather than
treating 32 points as a universal constant.

Use exact owned processes and primary-window identity for placement, then
verify actual geometry and window-server order. A temporary capture indicator
is not a second simulator process. Do not discover a directly launched Game
by blindly opening an equivalent-looking application path: macOS may launch
another registered copy. The isolated feasibility test does not authorize
adopting its PIDs into an unrelated live Demo Control run. Ordinary packaged
launch ownership remains part of the host-runtime integration gate.

Run the focused source tests with:

```sh
python3 -B -m unittest discover -s Util/BuildTools/tests -v
```
