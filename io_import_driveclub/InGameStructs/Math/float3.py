class float3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.X = x
        self.Y = y
        self.Z = z

    def __repr__(self):
        return f"float3({self.X:.6f}, {self.Y:.6f}, {self.Z:.6f})"

    def __iter__(self):
        return iter((self.X, self.Y, self.Z))

