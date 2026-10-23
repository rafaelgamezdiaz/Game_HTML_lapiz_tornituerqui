---
name: blueprint-to-3d-model
description: Generates accurate 3D assets in Blender (blend and glb) autonomously from multi-view orthographic reference blueprints or model sheets without requiring manual modeling prompts.
---

# Blueprint to 3D Model Automation Protocol

When the user provides a reference sheet or blueprint image displaying multiple orthographic views (Front, Side, Back, Top, Bottom, Isometric) of an object:

## 1. Automated Blueprint Ingestion & Extraction
1. **Locate Reference Image**: Detect the uploaded image path in `.user_uploaded` or `assets/` and copy it to `assets/<asset_name>_reference.jpg`.
2. **Dimension & Crop Analysis**:
   - Extract bounding dimensions (e.g., width, length, height callouts in inches or units).
   - Automatically crop individual projections (Front, Side, Back, Top, Bottom, Iso) for inspection if necessary.
   - Sample base color hex codes and material properties (metals, dielectric, glass, emissive).

## 2. Automated Blender Script Generation (`tools/build_<asset_name>.py`)
Generate a self-contained Blender Python script that:
1. **Calibrates Reference Empties**:
   - Spawns background reference image empties aligned to standard orthographic view axes:
     - Front Ortho: `(0, Y_dist, Z_mid)`, Rot: `(90, 0, 180)`
     - Side Ortho: `(X_dist, 0, Z_mid)`, Rot: `(90, 0, -90)`
     - Back Ortho: `(0, -Y_dist, Z_mid)`, Rot: `(90, 0, 0)`
     - Top Ortho: `(0, 0, Z_dist)`, Rot: `(0, 0, -90)`
     - Bottom Ortho: `(0, 0, -Z_dist)`, Rot: `(180, 0, -90)`
2. **Geometry Construction**:
   - Uses BMesh and modifiers (Mirror on X where symmetric, Bevel, Subsurf, Boolean) prioritizing clean quads.
   - Positions origin `(0, 0, 0)` at the central waterline/ground base and longitudinal centerline.
   - Implements decals/graphics via generated procedural textures or PIL texture files.
3. **PBR Materials**:
   - Creates Principled BSDF nodes with exact base colors, roughness, metallic, and transmission.
4. **Hierarchy & Naming**:
   - Organizes all parts into a clean 5-8 node object hierarchy.
5. **Export**:
   - Saves source `.blend` to `assets/models/<asset_name>.blend`.
   - Exports runtime `.glb` to `assets/models/<asset_name>.glb`.

## 3. Automated Verification & Previews (`tools/render_<asset_name>_preview.py`)
1. Executes headless Blender render script with 3-point studio lighting.
2. Produces multi-angle render previews (`preview_<asset_name>_iso.png`, `side.png`, `front.png`, `top.png`).
3. Evaluates silhouette against the blueprint reference.
