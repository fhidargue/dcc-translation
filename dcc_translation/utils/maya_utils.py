def safe_xform(self, node, attr):
    try:
        return self.cmds.xform(
            node,
            query=True,
            objectSpace=True,
            **{attr: True},
        )
    except Exception:
        return None


def extract_rotate_order(self, transform):
    try:
        idx = self.cmds.getAttr(f"{transform}.rotateOrder")
    except Exception:
        idx = 0

    return ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"][idx]


def extract_visibility(self, transform):
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


def split_namespace(transform):
    short = transform.split("|")[-1]

    if ":" not in short:
        return None, short

    parts = short.split(":")
    return ":".join(parts[:-1]), parts[-1]


def detect_instance(self, transform, mesh_path):
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


def extract_points(self, mesh):
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


def extract_topology(self, mesh):
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


def extract_normals(self, mesh):
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


def extract_uv_sets(self, mesh):
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


def extract_material_data(self, mesh):
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

    return material, textures
