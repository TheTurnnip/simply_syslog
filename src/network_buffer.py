import time
import typing


class NetworkBuffer:
    """
    Represents a buffer to store network messages.

    Attributes:
        buffer_type (typing.Type): The type of values that the buffer stores.
        max_size (int): The max size of the buffer.
        creation_time (float): The time that the buffer was created at.
        last_append_time (float): The time that last buffer append was made at.
        buffer_items (list): The items in the buffer.
    """

    def __init__(self, buffer_type: typing.Type, max_size: int, *args) -> None:
        """
        Initializes an instance of the NetworkBuffer class.

        Args:
            buffer_type (typing.Type): A reference to the type of data being
            \tstored in the buffer.
            max_size (int): The max length of the buffer.
            *args (Any): Items to store in the buffer.

        Raises:
            TypeError: Raised when the buffer is initialized with a value that
            does not match the buffer type.
            OverflowError: Raised when the buffer is initialized with more
            items than the max size.

        Returns:
            None

        Notes:
            This class is intended for use with a class that derives from the
            src.messages.AbstractMessage class, and thus the buffer_type
            attribute should be derived from the same AbstractMessage class.

        Examples:
            empty_buffer = NetworkBuffer(NetworkMessage, 15)
            OR
            created_with_items = NetworkBuffer(NetworkMessage, 15,
            NetworkMessage())
        """
        self.buffer_type = buffer_type
        self.max_size = int(max_size)
        self.creation_time = time.time()
        self.last_append_time = self.creation_time
        self.buffer_items = []
        for item in args:
            self._add_validated_item(item)

    def append(self, value) -> None:
        """
        Add an item to the end of the buffer.

        Args:
            value (Any): The item to append to the end of the buffer.

        Returns:
            None

        Raises:
            TypeError: Raised when the type being appended does not match the
            type set for the buffer.
            OverflowError: Raised when an item is attempted to be added that
            will exceed the set size for the buffer.
        """
        self._add_validated_item(value)

    def flush(self):
        """
        Flushes the buffer of written items.

        Returns:
            None

        Notes:
            This method relies on the type of the buffer being derived from
            src.messages.AbstractMessage.
        """
        buffer_item_index = len(self.buffer_items)
        while buffer_item_index:
            buffer_item_index -= 1
            is_written = self.buffer_items[buffer_item_index].is_written
            if is_written is True:
                del self.buffer_items[buffer_item_index]

    def _add_validated_item(self, item) -> None:
        """
        Validates an item before appending it to the buffer.

        Args:
            item (Any): The item to append to the buffer.

        Returns:
            None
        """
        if not isinstance(item, self.buffer_type):
            raise TypeError(f"Item {item} is not of the type "
                            f"{self.buffer_type}")
        if len(self.buffer_items) > self.max_size:
            raise OverflowError(f"The max size of the buffer "
                                f"({self.max_size}), the buffer was exceeded "
                                f"by {len(self) - self.max_size}")
        self.buffer_items.append(item)
        self.last_append_time = time.time()

    def __iter__(self):
        """
        Creates the pointer for iterating over the buffer_items.

        Returns:
            None
        """
        self.pointer = 0
        return self

    def __next__(self):
        """
        Increments the pointer to the number of items in the buffer.

        Returns:
            None

        Raises:
            StopIteration: Raised to tell a loop to stop iterating at the end
            of the buffer_items.
        """
        if self.pointer < len(self.buffer_items):
            current_pointer = self.pointer
            self.pointer += 1
            return self.buffer_items[current_pointer]
        else:
            raise StopIteration

    def __str__(self) -> str:
        """
        Gets the string representation of the buffer.

        Returns:
            str: The string representation of the buffer.
        """
        return str(self.buffer_items)

    def __len__(self) -> int:
        """
        Gets the current length of the buffer.

        Returns:
            int: The current length of the buffer.
        """

        return len(self.buffer_items)
