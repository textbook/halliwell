"""Functionality for handling IMDb people."""


class Person:
    """Represents a person on IMDb.

    Arguments:
      id_ (:py:class:`str`): The IMDb ID of the person.
      name (:py:class:`str`): The name of the person.

    """

    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
