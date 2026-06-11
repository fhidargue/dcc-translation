# DCC Translation Pipeline

![Python](https://img.shields.io/badge/python-3.13-blue)
![Maya](https://img.shields.io/badge/Maya-2025+-orange)
![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.x-orange)
![OpenUSD](https://img.shields.io/badge/OpenUSD-supported-brightgreen)
![MongoDB](https://img.shields.io/badge/MongoDB-supported-brightgreen)
![SQLite](https://img.shields.io/badge/SQLite-supported-brightgreen)

![DCC Translation Tool](./dcc_translation/assets/dcc-translation.gif)

A production-oriented Pipeline TD project focused on validation, scene translation, and USD publishing workflows between Autodesk Maya and Unreal Engine using OpenUSD.

The system validates Maya scenes using configurable YAML rule profiles, converts scene data into a lightweight SceneGraph abstraction, exports structured USD stages, generates publish metadata, and records translation activity through interchangeable backend registries.

## Problem

Modern VFX and game pipelines transfer large amounts of scene data between different DCC applications, often leading to:

- Inconsistent assets
- Failed imports
- Manual cleanup workflows
- Non-standardized publishing pipelines

This project explores how validation-driven publishing workflows and OpenUSD can improve reliability and interoperability across production environments.

## Key Features

- Maya validation and publishing plugin
- OpenUSD export pipeline
- Lightweight SceneGraph abstraction
- YAML-driven validation profiles
- PySide6 validation UI
- Unreal Engine workflow support
- SQLite and MongoDB registry backends
- Automated testing with Nox and mayapy
- Drag-and-drop Maya installation
- CLI publishing workflows

## Pipeline Architecture

![Pipeline Architecture](./dcc_translation/assets/images/dcc-translation.png)

The DCC Translation Pipeline is built around a modular validation-driven publishing workflow designed to standardize scene translation between Autodesk Maya, OpenUSD, and Unreal Engine. The system begins with Maya scene extraction, where DAG hierarchy, transforms, geometry, and metadata are converted into a lightweight DCC-independent SceneGraph representation.

Validation is performed through configurable YAML rule profiles before the scene is translated into a USD stage using the OpenUSD API. The publishing system then generates structured metadata and records translation activity through interchangeable backend registries such as SQLite and MongoDB. Finally, exported USD stages can be imported into Unreal Engine while preserving scene hierarchy and per-object separation.

## Translation Pipeline Execution

The SceneGraph intentionally stores only essential structural data required for cross-DCC translation and USD stage construction.

```
Maya Scene Extraction
    > Validation Layer (YAML Rule Profiles)
        > SceneGraph Construction
            > USD Export (Stage construction)
                > Metadata Serialization
                    > Translation Logging - Backend Registry (SQLite / MongoDB)
                        > Unreal Engine Import
```

## Demo

<details>
<summary>Maya DCC Translation Plugin UI</summary>

![Maya DCC Translation Plugin UI](./dcc_translation/assets/images/plugin-ui.png)
</details>

<details>
<summary>YAML Validation</summary>

![Maya DCC Translation Validation](./dcc_translation/assets/images/plugin-validation.png)
</details>

<details>
<summary>YAML Validation - Error</summary>

![Maya DCC Translation Error](./dcc_translation/assets/images/plugin-error.png)
</details>

<details>
<summary>YAML Validation - Success</summary>

![Maya DCC Translation Success](./dcc_translation/assets/images/plugin-success.png)
</details>

<details>
<summary>OpenUSD Publish</summary>

![Maya DCC Translation USD Publish](./dcc_translation/assets/images/plugin-publish.png)
</details>

<details>
<summary>UE5 Import</summary>

![Maya DCC Translation UE5 Import](./dcc_translation/assets/images/unreal-import.png)
</details>

<details>
<summary>UE5 Complete</summary>

![Maya DCC Translation UE5 Complete](./dcc_translation/assets/images/unreal-complete.png)
</details>

<details>
<summary>Backend Registry - MongoDB</summary>

![Maya DCC Translation Backend Registry](./dcc_translation/assets/images/mongo.png)
</details>

<details>
<summary>CLI</summary>

![Maya DCC Translation CLI Docs](./dcc_translation/assets/images/cli-help.png)

![Maya DCC Translation CLI Commands](./dcc_translation/assets/images/cli-commands.png)
</details>

## User Guide

Please refer to the ![USERGUIDE.md](./USERGUIDE.md) documentation file for installation and usage instructions.

Project showcase and walkthrough video:

https://www.youtube.com/watch?v=HBnfSlUyQT8

## Future Extensions

- Houdini SceneGraph adapter.
- REST publishing service.
- Live changes with Websockets.
- Batch scene processing.
- Asset version tracking.
- Dependency graph validation.
- Cloud registry backends.
- Automated Unreal Engine import workflows using the Unreal Python API.
- Automated asset publishing and scene reconstruction inside Unreal Engine.
