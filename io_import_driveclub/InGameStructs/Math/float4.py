class float4:
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.X = x
        self.Y = y
        self.Z = z
        self.W = w

    def __repr__(self):
        return f"float4({self.X:.6f}, {self.Y:.6f}, {self.Z:.6f}, {self.W:.6f})"

    def __iter__(self):
        return iter((self.X, self.Y, self.Z, self.W))

