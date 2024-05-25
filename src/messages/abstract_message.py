from abc import ABC, abstractmethod
class AbstractMessage(ABC):

    @property
    @abstractmethod
    def is_written(self):
        ...

    @is_written.setter
    @abstractmethod
    def is_written(self, value):
        ...
