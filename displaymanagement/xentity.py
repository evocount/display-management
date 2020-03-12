from abc import abstractmethod
import json


class XEntity:
    """
    Represents and Entity in the X domain
    .......
    Methods
    -------
    get_info()
    toJSON()
    """

    def __init__(self, id):
        self._id = id

    @abstractmethod
    def get_info(self):
        """
        Returns the information represented by this Entity
        """
        pass

    def toJSON(self):
        """
        Returns the information represented by this Entity in JSON format
        """
        info = self.get_info()
        return json.dumps(info)
