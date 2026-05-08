import os

from pxr import Usd, UsdGeom, Sdf, Gf, Vt, UsdShade
from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.utils.utils import sanitize_usd_name


class USDExporter:
    def __init__(self, output_path: str, target="unreal"):
        self.output_path = output_path
        self.target = target
        self._prototype_registry = {}

        existing_layer = Sdf.Layer.Find(output_path)

        if existing_layer:
            existing_layer.Clear()

        if os.path.exists(output_path):
            os.remove(output_path)

        self.stage = Usd.Stage.CreateNew(output_path)

        # Set Y as up axis for Unreal
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.y)
        UsdGeom.SetStageMetersPerUnit(self.stage, 0.01)

    def export(self, scene_nodes: list) -> None:
        """
        Export SceneGraph nodes to USD

        Args:
            scene_nodes (list): List of SceneGraphNode to export
        """

        root = self.stage.DefinePrim("/SceneRoot")
        UsdGeom.Scope.Define(self.stage, "/Materials")

        # Set default prim
        self.stage.SetDefaultPrim(root)

        for node in scene_nodes:
            self._export_node(node)

        self.stage.GetRootLayer().Save()

    def _export_node(self, node: SceneNode, parent_path: str = "/SceneRoot") -> None:
        """
        Export a single node to USD

        Args:
            node (SceneGraphNode): The node to export
            parent_path (str): The path of the parent node
        """

        short_name = sanitize_usd_name(
            node.metadata.get("maya", {}).get("shortName", node.name)
        )
        node_path = f"{parent_path}/{short_name}"

        if node.node_type == "mesh":
            instance_of = node.metadata.get("maya", {}).get("instanceOf")

            if instance_of:
                prim = UsdGeom.Xform.Define(self.stage, node_path)
                usd_prim = prim.GetPrim()
                usd_prim.SetInstanceable(True)

                prototype_path = self._prototype_registry.get(instance_of)

                if prototype_path:
                    usd_prim.GetReferences().AddInternalReference(prototype_path)
            else:
                prim = UsdGeom.Mesh.Define(self.stage, node_path)

                # Register prototype location
                maya_path = node.metadata.get("maya", {}).get("instanceOf") or node.name
                self._prototype_registry[maya_path] = node_path

                self._apply_mesh_geometry(prim, node)
        else:
            prim = UsdGeom.Xform.Define(self.stage, node_path)

        usd_prim = prim.GetPrim()

        self._apply_transform(usd_prim, node)
        self._apply_metadata(usd_prim, node)
        self._apply_material_binding(usd_prim, node)

        for child in node.children:
            self._export_node(child, node_path)

    def _apply_transform(self, usd_prim: Usd.Prim, node: SceneNode) -> None:
        """
        Apply transformation data from the node to the USD prim

        Args:
            usd_prim (Usd.Prim): The USD prim to apply the transform to
            node (SceneGraphNode): The source node containing transformation data
        """
        if node.transform is None:
            return

        xform = UsdGeom.Xformable(usd_prim)
        # xform.SetResetXformStack(True) # Resets the prim xform to prevent double transforms

        maya_meta = node.metadata.get("maya", {})

        rotate_pivot = maya_meta.get("rotatePivot")
        scale_pivot = maya_meta.get("scalePivot")

        existing_ops = {op.GetOpName(): op for op in xform.GetOrderedXformOps()}

        if self.target != "unreal":
            if rotate_pivot and "xformOp:translate:pivot" not in existing_ops:
                xform.AddTranslateOp(opSuffix="pivot").Set(Gf.Vec3d(*rotate_pivot))

            if scale_pivot and "xformOp:translate:scalePivot" not in existing_ops:
                xform.AddTranslateOp(opSuffix="scalePivot").Set(Gf.Vec3d(*scale_pivot))

        matrix = node.get_matrix(as_usd=True)

        if matrix:
            if "xformOp:transform" in existing_ops:
                existing_ops["xformOp:transform"].Set(matrix)
            else:
                xform.AddTransformOp().Set(Gf.Matrix4d(matrix))

        rotate_order = maya_meta.get("rotateOrder")

        if rotate_order is not None:
            usd_prim.SetCustomDataByKey("maya_rotateOrder", rotate_order)

    def _apply_metadata(self, usd_prim: Usd.Prim, node: SceneNode) -> None:
        """
        Apply metadata from the node to the USD prim

        Args:
            usd_prim (Usd.Prim): The USD prim to apply the metadata to
            node (SceneGraphNode): The source node containing metadata
        """

        usd_prim.SetCustomDataByKey(
            "scenegraph_uuid",
            node.uuid,
        )

        if hasattr(node, "publish_id"):
            usd_prim.SetCustomDataByKey(
                "publish_id",
                node.publish_id,
            )

        maya_meta = node.metadata.get("maya", {})

        if maya_meta.get("visibility") is False:
            usd_prim.CreateAttribute("visibility", Sdf.ValueTypeNames.Token).Set(
                "invisible"
            )

    def _apply_mesh_geometry(self, mesh_prim: UsdGeom.Mesh, node: SceneNode) -> None:
        """
        Write polygon topology into USD Mesh prim

        Args:
            mesh_prim (UsdGeom.Mesh): The USD Mesh prim to write geometry to
            node (SceneGraphNode): The source node containing geometry data
        """

        if node.points is None:
            return

        # USD expects a tuple of point, not arrays
        mesh_prim.CreatePointsAttr(Vt.Vec3fArray([tuple(p) for p in node.points]))

        if node.face_counts:
            mesh_prim.CreateFaceVertexCountsAttr(Vt.IntArray(node.face_counts))

        if node.face_indices:
            mesh_prim.CreateFaceVertexIndicesAttr(Vt.IntArray(node.face_indices))

        if node.normals:
            mesh_prim.CreateNormalsAttr(Vt.Vec3fArray([tuple(n) for n in node.normals]))
            mesh_prim.SetNormalsInterpolation(UsdGeom.Tokens.vertex)

        if node.uv_sets:
            primvars = UsdGeom.PrimvarsAPI(mesh_prim)

            for uv_name, coords in node.uv_sets.items():
                primvar_name = "st" if uv_name == "map1" else sanitize_usd_name(uv_name)

                primvars.CreatePrimvar(
                    primvar_name,
                    Sdf.ValueTypeNames.TexCoord2fArray,
                    UsdGeom.Tokens.vertex,
                ).Set([tuple(c) for c in coords])

    def _apply_material_binding(self, usd_prim: Usd.Prim, node: SceneNode) -> None:
        """
        Apply material binding to the USD prim based on the node's metadata

        Args:
            usd_prim (Usd.Prim): The USD prim to apply the material binding to
            node (SceneGraphNode): The source node containing material metadata
        """
        maya_data = node.metadata.get("maya", {})
        material_name = maya_data.get("material")

        if not material_name:
            return

        material_name = sanitize_usd_name(material_name)

        material_path = f"/Materials/{material_name}"
        material = UsdShade.Material.Define(self.stage, material_path)

        shader = UsdShade.Shader.Define(self.stage, f"{material_path}/PreviewSurface")
        shader.CreateIdAttr("UsdPreviewSurface")

        # Adds a default diffuse grey color
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            (0.8, 0.8, 0.8)
        )

        textures = maya_data.get("textures", {})

        def create_texture_output(
            texture_label, texture_path, output_type="rgb"
        ) -> UsdShade.Output:
            """
            Helper function to create a UsdUVTexture shader for a given texture path and connect it to the material

            Args:
                texture_label (str): A label for the texture (e.g. "DiffuseTexture")
                texture_path (str): The file path to the texture image
                output_type (str): The type of output to connect ("rgb" or "r")
            """

            texture_shader = UsdShade.Shader.Define(
                self.stage,
                f"{material_path}/{texture_label}",
            )

            texture_shader.CreateIdAttr("UsdUVTexture")
            texture_shader.CreateInput(
                "file",
                Sdf.ValueTypeNames.Asset,
            ).Set(texture_path)

            # Required for validators to recognize as texture node
            texture_shader.CreateInput(
                "st",
                Sdf.ValueTypeNames.TexCoord2f,
            )

            return texture_shader.CreateOutput(
                output_type,
                Sdf.ValueTypeNames.Float3
                if output_type == "rgb"
                else Sdf.ValueTypeNames.Float,
            )

        # Diffuse color from texture
        if "diffuseColor" in textures:
            rgb_output = create_texture_output(
                "DiffuseTexture", textures["diffuseColor"], "rgb"
            )

            shader.CreateInput(
                "diffuseColor",
                Sdf.ValueTypeNames.Color3f,
            ).ConnectToSource(rgb_output)

        # Normal from texture
        if "normal" in textures:
            normal_output = create_texture_output(
                "NormalTexture", textures["normal"], "rgb"
            )

            shader.CreateInput(
                "normal",
                Sdf.ValueTypeNames.Normal3f,
            ).ConnectToSource(normal_output)

        # Roughness from texture
        if "roughness" in textures:
            rough_output = create_texture_output(
                "RoughnessTexture", textures["roughness"], "r"
            )

            shader.CreateInput(
                "roughness",
                Sdf.ValueTypeNames.Float,
            ).ConnectToSource(rough_output)

        # Mettalic from texture
        if "metallic" in textures:
            metal_output = create_texture_output(
                "MetallicTexture", textures["metallic"], "r"
            )

            shader.CreateInput(
                "metallic",
                Sdf.ValueTypeNames.Float,
            ).ConnectToSource(metal_output)

        # Connect shader to material output
        material.CreateSurfaceOutput().ConnectToSource(
            shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        )

        # Bind the material to the USD prim
        UsdShade.MaterialBindingAPI(usd_prim).Bind(material)
