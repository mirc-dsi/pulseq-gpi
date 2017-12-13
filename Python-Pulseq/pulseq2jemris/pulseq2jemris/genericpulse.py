class GenericPulse():
    def __init__(self):
        self.type = 'pulse'

    def __str__(self):
        members = [attr for attr in dir(self) if
                   not callable(getattr(self, attr)) and not attr.startswith("__")]
        values = [getattr(self, attr) for attr in members]
        return str(dict(zip(members, values)))

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
            if not x.startswith("__") and not callable(getattr(self, x)) and getattr(self, x) is not None:
                attrib[x] = getattr(self, x)

        attrib.pop('type') if 'type' in attrib else None
        return attrib
