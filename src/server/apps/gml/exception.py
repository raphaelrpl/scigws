class GMLException(Exception):
    def __init__(self, msg):
        super(GMLException, self).__init__(msg)
        self.msg = msg