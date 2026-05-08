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
10. [Validation UI Workflow](#10-validation-ui-workflow)
11. [Enable Plugin Inside Maya](#11-enable-plugin-inside-maya)
12. [Shelf Button Usage](#12-shelf-button-usage)
13. [Live YAML Validation Editing](#13-live-yaml-validation-editing)
14. [Export From Script Editor](#14-export-from-script-editor)
15. [Metadata Output](#15-metadata-output)
16. [Summary](#16-summary)

# 1. Requirements

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
* Maya integration utilities

## Environment Configuration (.env)

Create a `.env` file in the project root:

```bash
touch .env
```

Example configuration:

```env
# MongoDB admin user
DCC_MONGO_ADMIN_USER=admin
DCC_MONGO_ADMIN_PASS=adminpass

# MongoDB pipeline registry user
DCC_MONGO_PIPELINE_USER=pipeline_user
DCC_MONGO_PIPELINE_PASS=pipeline_pass

# Mongo connection
DCC_MONGO_HOST=localhost
DCC_MONGO_PORT=27017
DCC_MONGO_DB=dcc_translation

# SQLite registry fallback
DCC_SQLITE_PATH=translations.db
```

## Environment Variable Description

| Variable | Purpose |
|---|---|
| `DCC_MONGO_ADMIN_USER` | MongoDB admin username |
| `DCC_MONGO_ADMIN_PASS` | MongoDB admin password |
| `DCC_MONGO_PIPELINE_USER` | Pipeline registry database user |
| `DCC_MONGO_PIPELINE_PASS` | Pipeline registry password |
| `DCC_MONGO_HOST` | MongoDB hostname |
| `DCC_MONGO_PORT` | MongoDB port |
| `DCC_MONGO_DB` | MongoDB database name |
| `DCC_SQLITE_PATH` | SQLite fallback database path |

## Backend Resolution

The pipeline automatically resolves the registry backend:

```text
MongoDB available  -> Mongo backend
MongoDB unavailable -> SQLite fallback
```

This allows the same publishing workflow to operate locally or in production environments without changing exporter logic.

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

```bash
uv run dcc-translate publish --dcc mock --target unreal --backend sqlite --out kitchen.usda
```

Pipeline performs:

1. Scene extraction
2. Validation
3. SceneGraph construction
4. USD stage export
5. Metadata creation
6. Registry logging
7. Unreal-compatible hierarchy export

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

The pipeline includes a drag-and-drop Maya installer.

The installer automatically:

- Installs the Maya module
- Creates the `.mod` file
- Registers environment paths
- Loads the plugin
- Enables plugin autoload
- Creates the custom shelf
- Adds the validation/publish shelf button

## Installation Steps

### Step 1 — Open Maya 2025

Launch Autodesk Maya 2025.

### Step 2 — Drag Installer Into Maya

Drag this file into the Maya viewport:

```bash
drag_to_maya.py
```

### Step 3 — Automatic Installation

The installer automatically:

- Writes dcc_translation.mod
- Refreshes Maya module paths
- Loads the plugin
- Creates the DCCTranslation shelf
- Adds the export button

Example generated module file location:

```bash
~/Library/Preferences/Autodesk/maya/2025/modules/dcc_translation.mod
```

No manual environment configuration is required.

# 10. Validation UI Workflow

The Maya plugin launches a fully dockable PySide6 validation interface.

Launch from:

```python
cmds.DCCExportUSD()
```

or from the custom Maya shelf button.

The validation UI provides:

- Live validation profile editing
- YAML-driven rule configuration
- Dynamic widget rendering
- Validation reporting
- USD publishing
- Validation state tracking

## Validation Workflow

1. Open validation UI
2. Modify validation rules if required
3. Save profile changes
4. Run validation
5. Review warnings/errors
6. Publish USD after validation passes

The `Publish USD` button remains disabled until validation succeeds.

Any profile modification automatically invalidates the current validation state.

# 11. Enable Plugin Inside Maya

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

# 12. Shelf Button Usage

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

# 13. Live YAML Validation Editing

Validation rules are externally defined using YAML profiles.

Profiles are located in:

```text
dcc_translation/validation_profiles/
```

Example:

```text
maya_to_unreal.yml
```

Example validation rules:

```yaml
require_frozen_transforms:
  enabled: true
  severity: error

allowed_node_types:
  - transform
  - mesh

require_geometry:
  enabled: true
```

The validation UI dynamically generates widgets from schema definitions:

- Checkboxes
- Combo boxes
- Editable lists
- Text fields

Profiles can be:

- Edited live inside Maya
- Saved without restarting Maya
- Reloaded dynamically
- Extended with new validation rules

Any profile modification automatically disables publishing until validation passes again.

# 14. Export From Script Editor

Alternative manual execution inside the Maya 2025 script editor:

```python
from dcc_translation.scripts.maya_export import publish_usd

publish_usd("/path/to/output.usda")
```

# 15. Metadata Output

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
    "exported_nodes": 247,
    "output_path": "../pipelineproject-fhidargue/test.usd",
    "machine": "User's machine",
    "timestamp": "2026-05-01T21:59:49.176064"
}
```

# 16. Summary

Pipeline supports:

* Maya scene validation
* Live YAML validation editing
* Dockable PySide6 validation UI
* USD export
* Unreal Engine integration
* Hierarchical mesh export
* Metadata tracking
* Registry logging
* CLI automation
* Maya shelf integration
* Drag-and-drop Maya installation
* Validation-gated publishing workflows

Designed for scalable cross-DCC production pipelines.
