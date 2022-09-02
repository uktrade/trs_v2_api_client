class TrackedChangedDict(dict):
    def __setitem__(self, key, value):
        print("asd")
