class ivec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def __repr__(self):
        return f"ivec3({self.x},{self.y},{self.z})"
