from base import GMLRangeBase, GMLBase


class GMLLowerCorner(GMLRangeBase):
    TAG = "lowerCorner"

    def __init__(self, limits, **attributes):
        """ It defines a GMLLowerCorner node based in WCS 2.0 """
        super(GMLLowerCorner, self).__init__(limits, **attributes)


class GMLUpperCorner(GMLRangeBase):
    TAG = "upperCorner"

    def __init__(self, limits, **attributes):
        """ It defines a GMLUpperCorner node based in WCS 2.0 """
        super(GMLUpperCorner, self).__init__(limits, **attributes)


class GMLLow(GMLRangeBase):
    TAG = "low"

    def __init__(self, limits, **attributes):
        """ It defines a GMLLow node based in WCS 2.0 """
        super(GMLLow, self).__init__(limits, **attributes)


class GMLHigh(GMLRangeBase):
    TAG = "high"

    def __init__(self, limits, **attributes):
        """ It defines a GMLHigh node based in WCS 2.0 """
        super(GMLHigh, self).__init__(limits, **attributes)



class GMLEnvelope(GMLBase):
    TAG = "Envelope"

    def __init__(self, data, **attributes):
        super(GMLEnvelope, self).__init__(**attributes)
        self.data = data
        self._init_limits()
        nodes = [self.lower, self.upper]
        self.extend(nodes)

    def _init_limits(self):
        self.lower = GMLLowerCorner(self.data.get('min'))
        self.upper = GMLLowerCorner(self.data.get('max'))


class GMLGrid(GMLBase):
    def __init__(self, data, **attributes):
        super(GMLGrid, self).__init__(**attributes)
        self.node_name = "Grid"


class GMLGridEnvelope(GMLEnvelope):
    TAG = "GridEnvelope"

    def _init_limits(self):
        self.lower = GMLLow(self.data.get('min'))
        self.upper = GMLHigh(self.data.get('max'))


class GMLDomainSet(GMLBase):
    TAG = "domainSet"

    def __init__(self, data, **attributes):
        super(GMLDomainSet, self).__init__(**attributes)


class GMLBoundedBy(GMLBase):
    envelope = None
    TAG = "boundedBy"

    def __init__(self, data, **attributes):
        envelope = GMLEnvelope(data)
        super(GMLBoundedBy, self).__init__((envelope, ), **attributes)