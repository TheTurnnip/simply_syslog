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
            self.add_validated_item(item)

    def append(self, value):
        self.add_validated_item(value)

    def flush(self):
        del(self.buffer_items)
        self.buffer_items = []

    def add_validated_item(self, item):
        if not isinstance(item, self.buffer_type):
            raise TypeError(f"Item {item} is not of the type "
                            f"{self.buffer_type}")
        if len(self.buffer_items) >= self.max_size:
            raise OverflowError("A buffer may not be initialized with more "
                                "items in the buffer than max size set.")
        self.buffer_items.append(item)

    def __iter__(self):
        self.pointer = 0
        return self

    def __next__(self):
        if self.pointer < len(self.buffer_items):
            current_pointer = self.pointer
            self.pointer += 1
            return self.buffer_items[current_pointer]
        else:
            raise StopIteration

    def __str__(self):
        return str(self.buffer_items)

    def __len__(self):
        return len(self.buffer_items)
