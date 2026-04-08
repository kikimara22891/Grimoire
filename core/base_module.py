class BaseModule:
    def __init__(self, module_id, name):
        self.id = module_id
        self.name = name

    def run(self):
        raise NotImplementedError("test")
