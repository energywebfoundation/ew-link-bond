import inspect
import datetime


class JSONAble(object):
    def __iter__(self):
        for attr, value in self.__dict__.items():
            if isinstance(value, datetime.datetime):
                iso = value.isoformat()
                yield attr, iso
            elif hasattr(value, '__iter__'):
                if hasattr(value, 'pop'):
                    a = []
                    for item in value:
                        if hasattr(item, '__iter__'):
                            a.append(dict(item))
                        else:
                            a.append(item)
                    yield attr, a
                else:
                    yield attr, dict(value)
            else:
                yield attr, value

    def to_dict(self):
        result = {}
        init = getattr(self, '__init__')
        for parameter in inspect.signature(init).parameters:
            att = getattr(self, parameter)
            if isinstance(att, list) or isinstance(att, set):
                att = [self.to_dict_or_self(o) for o in att]
            if isinstance(att, (datetime.datetime, datetime.date)):
                att = att.isoformat()
            result[parameter] = self.to_dict_or_self(att)
        return result

    @staticmethod
    def to_dict_or_self(obj):
        to_dict = getattr(obj, 'to_dict', None)
        if to_dict:
            return to_dict()
        else:
            return obj


class LocalFileData(JSONAble):
    pass


class ChainData(JSONAble):
    pass
