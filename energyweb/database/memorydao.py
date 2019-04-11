from copy import deepcopy

import tasks.database.dao as dao


class MemoryDAO(dao.DAO):
    """
    Store values in memory instead of any persistence
    Usually used in tests as a test fixture to raise coverage
    """

    def __init__(self):
        dao.DAO.register(MemoryDAO)
        self._stack = {}

    def cls(self, obj):
        return obj.__class__.__name__

    def create(self, obj):
        self._stack[obj.reg_id] = deepcopy(obj)

    def retrieve(self, reg_id):
        if reg_id not in self._stack.keys():
            raise FileNotFoundError
        obj = self._stack[reg_id]
        return deepcopy(obj)

    def retrieve_all(self):
        return [deepcopy(self._stack[i]) for i in self._stack]

    def update(self, obj):
        if obj.reg_id in self._stack.keys():
            self._stack[obj.reg_id] = deepcopy(obj)
        else:
            raise FileNotFoundError

    def delete(self, obj):
        del self._stack[obj.reg_id]

    def find_by(self, attributes: dict):
        result = []
        if len(self._stack) == 0:
            return result
        sample = list(self._stack.items())[0][1]
        intersect_keys = set(attributes).intersection(set(sample.__dict__))
        for k, reg in self._stack.items():
            for key in intersect_keys:
                stack_item = reg.__dict__
                if stack_item[key] == attributes[key]:
                    result.append(deepcopy(reg))
        if len(result) < 1:
            raise FileNotFoundError
        return result


class MemoryDAOFactory(dao.DAOFactory):

    def __init__(self):
        super().__init__()
        self.__instances = {}

    def get_instance(self, cls) -> MemoryDAO:
        if id(cls) in list(self.__instances.keys()):
            return self.__instances[id(cls)]
        self.__instances[id(cls)] = MemoryDAO()
        return self.__instances[id(cls)]
