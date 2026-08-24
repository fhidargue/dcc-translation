def safe_xform(self, node: str, attr: str) -> list | None:
    """
    Safely query for the transform attribute of a node, returning None if it fails

    Args:
        node (str): The name of the node to query
        attr (str): The transform attribute to query (e.g. "translate", "rotate", "scale")
    """

    try:
        return self.cmds.xform(
            node,
            query=True,
            objectSpace=True,
            **{attr: True},
        )
    except Exception:
        return None


def extract_rotate_order(self, transform: str) -> str:
    """
    Extract the rotation order of a transform node, returning "xyz" if it fails

    Args:
        transform (str): The name of the transform node to query
    """

    try:
        idx = self.cmds.getAttr(f"{transform}.rotateOrder")
    except Exception:
        idx = 0

    return ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"][idx]


def extract_visibility(self, transform: str) -> bool:
    """
    Extract the visibility of a transform node, returning True if it fails

    Args:
        transform (str): The name of the transform node to query
    """

    try:
        visibility = self.cmds.getAttr(f"{transform}.visibility")
    except Exception:
        return True

    try:
        if self.cmds.getAttr(f"{transform}.overrideEnabled"):
            visibility = self.cmds.getAttr(f"{transform}.overrideVisibility")
    except Exception:
        pass

    return visibility


def split_namespace(transform: str) -> tuple[str | None, str]:
    """
    Correctly split the namespace from a transform name

    Args:
        transform (str): The name of the transform node to split
    """

    short = transform.split("|")[-1]

    if ":" not in short:
        return None, short

    parts = short.split(":")
    return ":".join(parts[:-1]), parts[-1]


def detect_instance(self, transform: str, mesh_path: str) -> str | None:
    """
    Detect whether a mesh shape is instanced by tracking mesh UUIDs

    Args:
        transform (str): The name of the transform node to query
        mesh_path (str): The path of the mesh to check
    """

    if not mesh_path:
        return None

    try:
        uuid = self.cmds.ls(mesh_path, uuid=True)[0]
    except Exception:
        uuid = mesh_path

    if uuid not in self._mesh_registry:
        self._mesh_registry[uuid] = transform
        return None

    return self._mesh_registry[uuid]


def extract_points(self, mesh: str) -> list | None:
    """
    Extract vertex positions from a mesh shape, returning None if it fails

    Args:
        mesh (str): The name of the mesh shape to extract from
    """

    if self.om:
        try:
            sel = self.om.MSelectionList()
            sel.add(mesh)

            dag = sel.getDagPath(0)
            fn = self.om.MFnMesh(dag)

            return [(p.x, p.y, p.z) for p in fn.getPoints(self.om.MSpace.kObject)]
        except Exception:
            pass

    try:
        count = self.cmds.polyEvaluate(mesh, vertex=True)
        return [
            self.cmds.pointPosition(f"{mesh}.vtx[{i}]", local=True)
            for i in range(count)
        ]
    except Exception:
        return None


def extract_topology(self, mesh: str) -> tuple[list | None, list | None]:
    """
    Extract topology information from a mesh shape, returning None if it fails

    Args:
        mesh (str): The name of the mesh shape to extract from
    """

    try:
        counts = []
        indices = []

        for face in self.cmds.polyInfo(mesh, faceToVertex=True) or []:
            ids = face.split(":")[1].split()
            counts.append(len(ids))
            indices.extend(map(int, ids))

        return counts, indices
    except Exception:
        return None, None


def extract_normals(self, mesh: str) -> list | None:
    """
    Extract vertex normals from a mesh shape, returning None if it fails

    Args:
        mesh (str): The name of the mesh shape to extract from
    """

    if not self.om:
        return None

    try:
        sel = self.om.MSelectionList()
        sel.add(mesh)

        dag = sel.getDagPath(0)
        fn = self.om.MFnMesh(dag)

        return [
            (n.x, n.y, n.z) for n in fn.getVertexNormals(False, self.om.MSpace.kObject)
        ]
    except Exception:
        return None


def extract_uv_sets(self, mesh: str) -> dict[str, list]:
    """
    Extract UV set data from a mesh shape, returning an empty dict if it fails

    Args:
        mesh (str): The name of the mesh shape to extract from
    """

    uv_sets = {}

    try:
        for uv in self.cmds.polyUVSet(mesh, q=True, allUVSets=True) or []:
            self.cmds.polyUVSet(mesh, currentUVSet=True, uvSet=uv)

            count = self.cmds.polyEvaluate(mesh, uv=True)

            uv_sets[uv] = [
                self.cmds.polyEditUV(f"{mesh}.map[{i}]", q=True) for i in range(count)
            ]
    except Exception:
        pass

    return uv_sets


def extract_material_data(self, mesh: str) -> tuple[str | None, dict]:
    """
    Extract material data from a mesh shape, returning None if it fails

    Args:
        mesh (str): The name of the mesh shape to extract from
    """

    if not mesh:
        return None, {}

    try:
        sgs = self.cmds.listConnections(mesh, type="shadingEngine") or []
        mats = self.cmds.ls(self.cmds.listConnections(sgs), materials=True)
    except Exception:
        return None, {}

    if not mats:
        return None, {}

    material = mats[0]
    textures = {}

    try:
        files = self.cmds.listConnections(material, type="file") or []

        for node in files:
            path = self.cmds.getAttr(f"{node}.fileTextureName")

            if path:
                textures.setdefault("diffuseColor", path)
    except Exception:
        pass

    try:
        color = self.cmds.getAttr(f"{material}.color")[0]
        textures["diffuseColorValue"] = color
    except Exception:
        pass

    return material, textures
