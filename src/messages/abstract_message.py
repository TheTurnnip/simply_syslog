from abc import ABC, abstractmethod


class AbstractMessage(ABC):
    """
    Abstract class that all messages that are stored in a src.NetworkBuffer
    object should derive from.
    """

    @property
    @abstractmethod
    def is_written(self) -> bool:
        """
        Gets the is_written attribute.

        Returns:
            bool: Returns the is_written attribute.
        """
        ...

    @is_written.setter
    @abstractmethod
    def is_written(self, value):
        """
        Sets the is_written value

        Args:
            value (bool): The value to the is_written value to.

        Returns:
            None
        """
        ...
