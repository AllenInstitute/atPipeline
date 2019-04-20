import copy

class RenderStack:

    def __init__(self, owner = None, project_name = None, stack_name = None):
        self.owner          = owner
        self.project_name   = project_name
        self.stack_name     = stack_name

    @classmethod
    def copyfrom(cls, stack):
        "Initialize using stack object"
        return cls(stack.owner, stack.project_name, stack.stack_name)

class RenderStackBounds:
    def __init__(self, bounds:list):
        self.minX = bounds[0]
        self.maxX = bounds[1]
        self.minY = bounds[2]
        self.maxY = bounds[3]
        self.minZ = bounds[4]
        self.maxZ = bounds[5]