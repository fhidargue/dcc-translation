# DCC Translation Pipeline - Complete User Guide

This guide explains everything required to install, configure, and run the DCC Translation Pipeline across CLI, Maya, registry backends, and plugin UI integration.

## Table of Contents

1. [Requirements](#1-requirements)
2. [System Dependencies](#2-system-dependencies)
3. [Maya 2025 Setup](#3-maya-2025-setup)
4. [Unreal Engine 5 Setup](#4-unreal-engine-5-setup)
5. [Development Environment Setup](#5-development-environment-setup)
6. [Registry Backends](#6-registry-backends)
7. [Testing](#7-testing)
8. [CLI Usage](#8-cli-usage)
9. [Maya Plugin Installation](#9-maya-plugin-installation)
10. [Enable Plugin Inside Maya](#10-enable-plugin-inside-maya)
11. [Shelf Button Usage](#11-shelf-button-usage)
12. [Export From Script Editor](#12-export-from-script-editor)
13. [Metadata Output](#13-metadata-output)
14. [Summary](#14-summary)

## 1. Requirements

Minimum supported environment:

| Software      | Version                      |
| ------------- | ---------------------------- |
| Python        | >=3.11                       |
| Maya          | 2025                         |
| Unreal Engine | 5.x                          |
| NumPy         | required                     |
| PyYAML        | required                     |
| PyMongo       | optional                     |
| dotenv        | optional                     |
| pytest        | development only             |
| uv            | optional package manager     |
| Podman        | optional container workflows |

Operating systems supported:

* macOS
* Linux
* Windows

# 2. System Dependencies

Install locally:

```
Git
Python >=3.11
uv package manager
Autodesk Maya 2025
Unreal Engine 5
```

Optional:

```
Podman
MongoDB
```

# 3. Maya 2025 Setup

The pipeline requires several Python packages to be installed inside Maya's
embedded Python interpreter (`mayapy`).

Install all dependencies with a single command or separately:

```bash
/Applications/Autodesk/maya2025/Maya.app/Contents/bin/mayapy -m pip install \
numpy pyyaml pytest pymongo python-dotenv
```

This installs:

* NumPy
* PyYAML
* PyTest
* PyMongo
* Dotenv

After installation:

**Restart Maya**

# 4. Unreal Engine 5 Setup

Install:

```
Unreal Engine 5.x
USD importer plugin enabled
```

Inside Unreal:

```
Edit > Plugins > USD Importer > Enable
```

**Restart Unreal Engine**

# 5. Development Environment Setup

Clone the repository:

```bash
git clone <repository_url>
cd pipelineproject-fhidargue
```

Initialize the Podman virtual machine:

```bash
podman machine start
```

Launch Services with `podman-compose`:

```bash
podman-compose up -d
```

This launches:

* MongoDB registry backend
* Any additional services defined in podman-compose.yml

Install dependencies using uv:

```bash
uv sync
```

This creates a managed virtual environment and installs:

* Project dependencies
* CLI entrypoint
* Validation system
* USD exporter
* Registry backends

Verify the CLI is available:

```bash
uv run dcc-translate --help
```

# 6. Registry Backends

Supported:

| Backend | Description      |
| ------- | ---------------- |
| SQLite  | default fallback |
| MongoDB | production-ready |

Automatic detection:

```
Mongo running > Mongo used
Mongo offline > SQLite fallback
```

# 7. Testing

The project uses pytest with nox sessions to separate standard Python tests from Maya standalone tests.

Three testing entry points are available:

**Run Local Tests (No Maya Required)**

Runs all validation, SceneGraph, USD export, registry, CLI, and pipeline tests:

```bash
uv run nox -s local
```

These tests execute inside a standard Python environment and do not require Autodesk Maya.

**Run Maya Standalone Tests**

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

**Run All Tests**

Runs both local and Maya standalone test suites:

```bash
uv run nox -s all
```

# 8. CLI Usage

Available commands:

* dcc-translate validate
* dcc-translate publish
* dcc-translate inspect

## Validation Workflow

Run validation:

```bash
uv run dcc-translate validate --dcc mock --target unreal
```

Checks include:

* Frozen transforms
* Geometry presence
* Naming conventions
* Supported node types
* Hierarchy structure

Output example:

```
Validation completed
Scene passed validation
```

## Publish Workflow

Publish USD:

```bash
uv run dcc-translate publish --dcc mock --target unreal --backend mongo --out kitchen.usda
```

``bash
uv run dcc-translate publish --dcc mock --target unreal --backend sqlite --out kitchen.usda
```

Pipeline performs:

1. Scene extraction
2. Validation
3. USD export
4. Metadata creation
5. Registry logging

Outputs:

```
kitchen.usda
kitchen.metadata.json
kitchen.db (SQLite)
```

## Inspect Workflow

View publish history stored in the registry:

```bash
uv run dcc-translate inspect --backend mongo
```

```bash
uv run dcc-translate inspect --backend sqlite
```

# 9. Maya Plugin Installation

Install module:

```bash
uv run pipelineproject-fhidargue/maya_module/installModule.py
```

Creates:

```
~/Library/Preferences/Autodesk/maya/2025/modules/dcc_translation.mod
```

**Restart Maya if you had it open**

# 10. Enable Plugin Inside Maya

Open Maya 2025:

```
Windows > Settings/Preferences > Plug-in Manager
```

Enable the plug-in from the module:

```
../pipelineproject-fhidargue/maya_module/plug-ins/DCCExportUSD.py
```

Check:

```
Loaded
Auto Load
```

# 11. Shelf Button Usage

Shelf appears on the top right of the Maya 2025 UI:

```
DCCTranslation
```

Button:

```
Export USD to Unreal
```

Clicking button executes:

```
cmds.DCCExportUSD()
```

Select the file name and location when you want to save the `USD` file. After this step, wait for the pipeline to run automatically.

# 12. Export From Script Editor

Alternative manual execution inside the Maya 2025 script editor:

```python
from dcc_translation.scripts.maya_export import publish_usd

publish_usd("/path/to/output.usda")
```

# 13. Metadata Output

Each export generates:

```
scene.metadata.json
```

Contains:

```json
{
    "publish_id": "c56c3314-8978-4e57-8ed8-956351fcXXXX",
    "scene": "kitchen_set.ma",
    "source_dcc": "maya",
    "target_dcc": "unreal",
    "validation_profile": "../pipelineproject-fhidargue/dcc_translation/validation_profiles/maya_to_unreal.yml",
    "validation_profile_hash": "436e7e58b87eacfd5fa881f38be1f05e21a1XXXX",
    "validation_status": "success",
    "errors": [],
    "warnings": [],
    "exported_nodes": 1,
    "output_path": "../pipelineproject-fhidargue/test.usd",
    "machine": "User's machine",
    "timestamp": "2026-05-01T21:59:49.176064"
}
```

# 14. Summary

Pipeline supports:

* Maya scene validation
* USD export
* Unreal Engine integration
* Metadata tracking
* Registry logging
* CLI automation
* Maya shelf UI export

Designed for scalable cross-DCC production pipelines.
