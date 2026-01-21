from dataclasses import dataclass


@dataclass
class Block:
    # lightweight shim for unpickling; MGAIA pickles may set arbitrary attributes
    namespacedName: str = ""

    def __repr__(self):
        return f"Block({self.namespacedName})"


class Transform:
    def __init__(self, translation=None, rotation=0):
        self.translation = translation
        self.rotation = rotation


class Editor:
    def __init__(self, buffering=False):
        pass

    def pushTransform(self, t: Transform):
        # context manager shim
        class Ctx:
            def __enter__(self_inner):
                return None

            def __exit__(self_inner, exc_type, exc, tb):
                return False

        return Ctx()

    def placeBlock(self, vec, block):
        # shim: do nothing
        return
