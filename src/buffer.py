import time
import typing


class Buffer:

    def __init__(self, type: typing.Type, max_size: int, *args) -> None:
        self.buffer_type = type
        self.max_size = int(max_size)
        self.creation_time = time.time()
        self.last_append_time = self.creation_time
        self.buffer_items = []
        for item in args:
            if isinstance(item, self.buffer_type):
                self.buffer_items.append(item)
            else:
                raise TypeError(f"Item {item} is not of the type "
                                f"{self.buffer_type}")
            if len(self.buffer_items) >= self.max_size:
                raise OverflowError("A buffer may not be initialized with more "
                                    "items in the buffer than max size set.")

    def append(self):
        ...

    def flush(self):
        ...

    def __iter__(self):
        ...

    def __next__(self):
        ...

    def __len__(self):
        ...

    def __str__(self):
        ...
