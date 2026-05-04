# DCC Translation Pipeline

![Python](https://img.shields.io/badge/python-3.13-blue)
![Maya](https://img.shields.io/badge/Maya-2024+-orange)
![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.x-orange)
![OpenUSD](https://img.shields.io/badge/OpenUSD-supported-brightgreen)
![MongoDB](https://img.shields.io/badge/MongoDB-supported-brightgreen)
![SQLite](https://img.shields.io/badge/SQLite-supported-brightgreen)

A modular validation-driven publishing framework for translating `Autodesk Maya` scenes into `OpenUSD` using a lightweight canonical `SceneGraph` representation, with automated ingestion support for `Unreal Engine` and pluggable registry backends for translation tracking.

The system performs rule-based validation prior to export, converts scene structure into a simplified SceneGraph abstraction, generates a USD stage using the `OpenUSD API`, and records translation activity through interchangeable registry backends (`SQLite` or `MongoDB`) for traceability and reproducibility.

This project demonstrates how modern animation and VFX pipelines can standardize scene exchange between DCC tools using backend-agnostic validation-driven publishing workflows.

## Overview

Different DCC tools store scene structure differently:

| DCC            | Scene Structure |
|---------------|----------------|
| Maya          | DAG hierarchy  |
| Unreal Engine | Actor hierarchy |

To improve interoperability, this project introduces a lightweight `SceneGraph` layer that normalizes essential scene information before constructing a USD stage:


## Translation Pipeline Execution

The SceneGraph intentionally stores only essential structural data required for cross-DCC translation and USD stage construction.

```
Maya Scene Extraction
    > Validation Layer (YAML Rule Profiles)
        > SceneGraph Construction
            > USD Export (Stage construction)
                > Metadata Serialization
                    > Translation Logging -Backend Registry (SQLite / MongoDB)
                        > Unreal Import
```

Execution workflow:

1. Extract hierarchy, transforms, mesh references, pivots, visibility state, namespaces, and instancing data from `Maya` using `maya.cmds` and `OpenMaya`.
2. Select and load a target-specific `YAML` validation profile.
3. Convert extracted nodes into a lightweight canonical SceneGraph representation.
4. Construct a USD stage using the `OpenUSD (pxr) API`.
5. Generate structured publish metadata (`scene.metadata.json`).
6. Record validation results and export metadata using a registry backend.
7. Import `USD` automatically into `Unreal Engine`.

The architecture supports future adapters for additional DCC tools such as `Houdini`. Adapters follow a modular translation interface and reuse the same validation, SceneGraph, metadata, and export pipeline without modifying core logic.

## User Guide

Please refer to the [USERGIDE.md](./USERGUIDE.md) file for installation and tool usage.

## Features

### Table of Contents

1. [Scene Validation](#1-scene-validation)
2. [SceneGraph Intermediate Representation](#2-scenegraph-intermediate-representation)
3. [USD Export](#3-usd-export)
4. [Metadata Serialization](#4-metadata-serialization)
5. [Translation Registry Backends](#5-translation-registry-backends)
6. [Command Line Interface](#6-command-line-interface)
7. [Unreal Engine Import Demonstration](#7-unreal-engine-import-demonstration)
8. [Maya Publish Tool Integration](#8-maya-publish-tool-integration)
9. [Testing](#9-testing)

### 1. Scene Validation

Validation runs prior to SceneGraph construction using configurable YAML rule profiles to ensure compatibility with downstream tools and publishing standards.

Typical validation checks include:

- Transform normalization
- Unsupported node detection
- Unit consistency verification
- Geometry presence validation
- Naming convention enforcement
- Namespace filtering
- Visibility filtering
- Intermediate shape exclusion

Example rule execution driven by YAML validation profiles:

```python
if rules["require_frozen_transforms"]["enabled"]:
    scale = cmds.getAttr(f"{node}.scale")[0]

    if scale != (1.0, 1.0, 1.0):
        report.error(
            f"Non-frozen scale detected on {node}"
        )
```

Validation results are written to `scene.metadata.json` and recorded in the publish registry backend.

### YAML Validation Profiles

Validation rules are externally defined:

```
validation_profiles/
    maya_to_usd.yml
    maya_to_unreal.yml
```

```yaml
pipeline_target: unreal

require_frozen_transforms:
  enabled: true
  severity: error

allowed_node_types:
  - transform
  - mesh

forbidden_node_types:
  - constraint
  - locator

unit_scale: cm

require_geometry:
  enabled: true
  severity: error
```

Profiles enable consistent validation across multiple pipeline targets without modifying validator source code.

### 2. SceneGraph Intermediate Representation

Scenes are converted into a lightweight canonical structure before USD export:

```
Maya 
    > SceneGraph 
        > USD Stage
```

SceneGraph stores:

- Hierarchy
- Transforms
- Mesh references
- Visibility state
- Pivot offsets
- Metadata attributes
- Instancing information

Example structure:

```python
class SceneNode:
    def __init__(
        self,
        name,
        node_type,
        transform,
        mesh_path=None,
        metadata=None
    ):
        self.name = name
        self.node_type = node_type
        self.transform = transform
        self.mesh_path = mesh_path
        self.metadata = metadata or {}
        self.children = []
```

The SceneGraph acts as a canonical publish representation rather than a full scene description system.

### 3. USD Export

SceneGraph nodes are converted into USD primitives using the OpenUSD Python API:

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateNew("scene.usd")

UsdGeom.Xform.Define(stage, "/Root/MyAsset")

stage.GetRootLayer().Save()
```

Export preserves:

- Hierarchy
- Transforms
- Visibility
- Pivots
- Namespaces
- Instancing relationships

USD acts as the canonical interchange layer between validation and downstream consumption stages.

### 4. Metadata Serialization

Each publish operation generates structured metadata describing the translation process: 

```
scene.metadata.json
```

Metadata includes:

- Sene name
- Source DCC
- Target DCC
- Export format
- Validation profile
- Validation status
- Timestamp
- Exported assets
- Registry backend used

This enables reproducible publishing workflows and automated auditing.

### 5. Translation Registry Backends

Translation metadata is recorded through a pluggable backend interface.

Supported backends:

- SQLite
- MongoDB

Example SQLite entry:

```sql
scene: robot_scene
source: maya
target: unreal
format: usd
validation_profile: unreal_rules.yml
validation: success
import: success
timestamp: 2026-04-13
```

Example MongoDB document:

```json
{
  "scene": "robot_scene",
  "source": "maya",
  "target": "unreal",
  "format": "usd",
  "validation": "success",
  "import": "success"
}
```

Backends implement a shared registry interface:

```
RegistryBackend
    - SQLiteBackend
    - MongoBackend
```

This enables pipeline deployments to switch storage systems without modifying publishing logic.

### 6. Command Line Interface

The framework includes a CLI publishing entry point:

```bash
python -m dcc_translation.cli publish \
    --scene robot_scene.ma \
    --target unreal \
    --profile maya_to_unreal.yml
```

CLI features:

- Validation execution
- SceneGraph construction
- USD export
- Metadata generation
- Backend registry logging

This supports batch publishing workflows and automation pipelines.

### 7. Unreal Engine Import Demonstration

Exported USD stages can be automatically imported into Unreal Engine:

```python
import unreal

task = unreal.AssetImportTask()
task.filename = "scene.usd"
task.destination_path = "/Game/PipelineImports"
task.automated = True

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
```

This demonstrates USD as a transport layer between offline DCC environments and realtime engines.

### 8. Maya Publish Tool Integration

The framework includes a Maya-side publishing entry point:

```
dcc_translation/maya_plugin/publish_tool.py
```

This enables validation and export directly from within Maya as part of a structured artist publishing workflow.

### 9. Testing

The project uses pytest with nox sessions to separate standard Python tests from Maya standalone tests.

Three testing entry points are available:

**9.1 Run Local Tests (No Maya Required)**

Runs all validation, SceneGraph, USD export, registry, CLI, and pipeline tests:

```bash
uv run nox -s local
```

These tests execute inside a standard Python environment and do not require Autodesk Maya.

**9.2 Run Maya Standalone Tests**

Runs adapter integration tests using `mayapy`:

```bash
uv run nox -s maya
```

By default, Nox searches for:

```bash
/Applications/Autodesk/maya2025/Maya.app/Contents/bin/mayapy
```

You can override this path:

```bash
export MAYAPY_EXECUTABLE=/path/to/mayapy
uv run nox -s maya
```

If Maya standalone is unavailable, the session is skipped automatically.

**9.3 Run All Tests**

Runs both local and Maya standalone test suites:

```bash
uv run nox -s all
```

## Project Architecture

```
dcc_translation/

core/
    scene_graph.py
    validator.py
    translator.py
    metadata.py

adapters/
    base_adapter.py
    maya_adapter.py
    unreal_adapter.py
    mock_adapter.py

formats/
    usd_adapter.py

database/
    translation_registry.py

database/backend/
    registry_backend.py
    sqlite_backend.py
    mongo_backend.py

config/
    env.py

validation_profiles/
    maya_to_usd.yml
    maya_to_unreal.yml

maya_plugin/
    publish_tool.py

cli.py
```

## Workflow

### Export from Maya

- Validate scene
- Construct SceneGraph
- Generate USD stage
- Generate Metadata
- Log translation via Registry Backend

### Import into Unreal Engine

- Load USD stage
- Reconstruct hierarchy
- Restore transforms
- Register imported assets

## Technology Stack

### Core Language

- Python

### APIs and Libraries

- maya.cmds
- maya.api.OpenMaya
- OpenUSD (pxr)
- Unreal Python API
- sqlite3
- pymongo
- PyYAML
- pytest

### Outputs

Pipeline execution produces:

```
scene.usd
scene.metadata.json
translations.db (SQLite backend)
or
MongoDB translation collection
```

## Goal

The goal of this project is to develop a production-oriented publishing pipeline that improves interoperability between Autodesk Maya and Unreal Engine through automated validation, canonical scene normalization, backend-agnostic translation tracking, and OpenUSD-based scene transport.

Modern animation and VFX pipelines rely on multiple specialized DCC applications, yet scene exchange between them is often manual, inconsistent, and difficult to reproduce.

This project addresses that problem by implementing:

- A Maya validation and publishing plugin.
- A lightweight SceneGraph canonical representation.
- OpenUSD stage construction as a transport backbone.
- Automated Unreal Engine USD ingestion.
- Interchangeable registry backends (SQLite / MongoDB).
- CLI publishing automation.
- Structured metadata generation.

The resulting system demonstrates how structured scene publishing workflows can improve reliability, automation, and interoperability across heterogeneous DCC environments.

## Future Extensions (Optional)

- Houdini SceneGraph adapter.
- REST publishing service.
- Batch scene processing.
- Asset version tracking.
- Dependency graph validation.
- Cloud registry backends.