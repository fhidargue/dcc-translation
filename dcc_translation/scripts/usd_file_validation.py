import os

usd_path = "/Users/fhidalgo/Documents/BU/pipelineproject-fhidargue/kitchen_export.usda"

if not os.path.exists(usd_path):
    print("USD file not found:", usd_path)
else:
    text = open(usd_path).read()

    checks = {
        "Mesh prims": "def Mesh",
        "Vertex positions (points)": "point3f[] points",
        "Normals": "normal3f[]",
        "UV coordinates": "texCoord2f[]",
        "PreviewSurface shader": "UsdPreviewSurface",
        "Texture nodes": "UsdUVTexture",
        "Instancing enabled": "instanceable = true",
        "Pivot transforms": "xformOp:translate:pivot",
        "Scene root": 'def "SceneRoot"',
        "Material scope": "/Materials/",
    }

    print("\nUSD EXPORT VALIDATION REPORT\n")

    for label, token in checks.items():
        if token in text:
            print(f"YES - {label}")
        else:
            print(f"NO - {label}")

    print("\nDETAIL COUNTS\n")

    print("Mesh prim count:", text.count("def Mesh"))
    print("Material count:", text.count("def Material"))
    print("Texture shader count:", text.count("UsdUVTexture"))
    print("Instance prim count:", text.count("instanceable = true"))
    print("Pivot op count:", text.count("xformOp:translate:pivot"))

    print("\nDone")
