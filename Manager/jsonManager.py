import json


class JsonManager(object):
    mappings = {}

    @classmethod
    def class_mapper(cls, d):
        for keys, c in cls.mappings.items():
            if keys.issuperset(d.keys()):  # are all required arguments present?
                return c(**d)
        else:
            # Raise exception instead of silently returning None
            raise ValueError('Unable to find a matching class for object: {!s}'.format(d))

    @classmethod
    def complex_handler(cls, object_to_handle):
        if hasattr(object_to_handle, '__dict__'):
            return object_to_handle.__dict__
        else:
            raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(object_to_handle), repr(object_to_handle)))

    @classmethod
    def register(cls, class_to_register):
        cls.mappings[frozenset(tuple([attr for attr, val in class_to_register().__dict__.items()]))] = class_to_register
        return class_to_register

    @classmethod
    def to_json(cls, obj):
        return json.dumps(obj.__dict__, default=cls.complex_handler, indent=4)

    @classmethod
    def from_json(cls, json_str):
        return json.loads(json_str, object_hook=cls.class_mapper)

    @classmethod
    def to_file(cls, obj, path, file_mode="w"):
        with open(path, file_mode) as json_file:
            json_file.writelines([cls.to_json(obj)])
        return path

    @classmethod
    def from_file(cls, file_path, file_mode="r"):
        result = None
        with open(file_path, file_mode) as json_file:
            result = cls.from_json(json_file.read())
        return result
