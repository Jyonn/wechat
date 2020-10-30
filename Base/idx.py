import platform


ORDERED_DICT_PYTHON_VERSION = '3.6'
ORDERED_DICT_PYTHON_IMPLEMENTATION = 'CPython'


class idx:
    class IdxKeyError:
        pass

    def __init__(self, **kwargs):
        self._dict = kwargs
        self._default_val = self.IdxKeyError

    def default(self, default_value=IdxKeyError):
        self._default_val = default_value
        return self

    def __getattr__(self, item):
        if self._default_val == self.IdxKeyError:
            return self._dict[item]
        return self._dict.get(item, self._default_val)


class tidx:
    @classmethod
    def allow_key_maps_constructor(cls):
        return platform.python_version() >= ORDERED_DICT_PYTHON_VERSION and \
               platform.python_implementation() == ORDERED_DICT_PYTHON_IMPLEMENTATION

    def __init__(self, *key_list, **key_maps):
        self._key_list = key_list or []
        self._map_func = dict()
        assert len(self._key_list) == len(set(self._key_list))

        if self.allow_key_maps_constructor():
            for key in key_maps:
                self._key_list.append(key)
                if key_maps[key]:  # Not None
                    if isinstance(key_maps[key], str):
                        key_maps[key] = [key_maps[key]]
                    assert isinstance(key_maps[key], list)
                    for func in key_maps[key]:
                        self._map_func[func] = key
        else:
            if key_maps:
                raise EnvironmentError('Only python >= 3.6 supports key maps in constructor')

    def __call__(self, *args, **kwargs):
        d = dict()
        for k, v in zip(self._key_list, args):
            d[k] = v
        d.update(kwargs)
        for func in self._map_func:
            d[func] = getattr(d[self._map_func[func]], func)
        return idx(**d)

    def map(self, **key_maps):
        for key in key_maps:
            if isinstance(key_maps[key], int):
                self._map_func[key] = self._key_list[key_maps[key]]
            else:
                if isinstance(key_maps[key], str):
                    key_maps[key] = [key_maps[key]]
                assert isinstance(key_maps[key], list)
                for func in key_maps[key]:
                    self._map_func[func] = key
        return self
