class GenericSeq():
    def __init__(self):
        self.events = []
        self.type = 'seq'
        self.numbering = 0

    def __str__(self):
        s = self.type + str(self.numbering)
        s += " Events:\n" if self.type != 'D' else "\n"
        for i in self.events:
            s += str(i)
            s += "\n"
        return s

    def make_attrib(self):
        """
        Returns a dict object that contains all the relevant member variables.

        Returns
        -------
        attrib : dict
            Contains all relevant member variables.
        """
        attrib = {}
        members = dir(self)
        for x in members:
            if not x.startswith("__") and not callable(getattr(self, x)):
                attrib[x] = getattr(self, x)

        attrib.pop('type') if 'type' in attrib else None
        attrib.pop('events') if 'events' in attrib else None
        attrib.pop('numbering') if 'numbering' in attrib else None
        return attrib
