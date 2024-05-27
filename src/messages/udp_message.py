from src.messages.abstract_message import AbstractMessage


class UDPMessage(AbstractMessage):
    """
    Represents a UPD message from a python socket.

    Attributes:
        _address (str): The address that the message was received from.
        _message (bytes): The message in the form of bytes.
        _is_written (bool): If False when the message has not been
                            written to the disk.
    """

    def __init__(self, address: str, message: bytes) -> None:
        """
        Initializes an instance of the UDPMessage class.

        Args:
            address (str): The address that tht message was received from.
            message (bytes): The message in the form of bytes.

        Returns:
            None
        """
        self._address = address
        self._message = message
        self._is_written = False

    @property
    def address(self) -> str:
        """
        Gets the address the message was received from.
        """
        return self._address

    @property
    def message(self) -> bytes:
        """
        Gets the reqeust message.
        """
        return self._message

    @property
    def is_written(self) -> bool:
        """
        Gets the is_written value for the message.
        """
        return self._is_written

    @is_written.setter
    def is_written(self, value: bool) -> None:
        """
        Sets the _is_written attribute.

        Args:
            value (bool): If the message has been writen to the disk or not.

        Returns:
            None
        """
        if not isinstance(value, bool):
            raise TypeError(
                "The buffer_type of the is_written property must be bool.")
        self._is_written = value

    def __str__(self) -> str:
        """
        Gets the string representation of the class data.

        Returns:
            str: The string representation of the class data.
        """
        return (f"Written: {self._is_written} | {self._address}:"
                f" {self._message}")
