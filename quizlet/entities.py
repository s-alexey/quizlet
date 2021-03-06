from __future__ import unicode_literals, absolute_import
from tortilla.utils import Bunch

__all__ = ['Set', 'Class', 'User']


class Entity(Bunch):
    """ A base Quizlet Entity.

    Attributes:
        endpoint(:obj:`.QuizletAPI`): An api's endpoint that points to this object.
            Allows makes requests from within the class.
    """

    def __init__(self, kwargs=None, *, endpoint=None):
        super(Entity, self).__init__(kwargs)
        self.endpoint = endpoint

    def __repr__(self):
        return "{cls}({repr})".format(cls=self.__class__.__name__, repr=super().__repr__())

    def to_dict(self):
        """ Transforms an entity to a pure dict. """
        result = dict(self)
        result.pop('endpoint', None)
        return result


class Set(Entity):
    """ A wrapper for Quizlet Set.

    Attributes:
        terms(:obj:`list` of :obj:`str`): A list of terms (front desks).
        definitions(:obj:`list` of :obj:`str`): A list of definitions (back desks).
    """

    def retrieve(self):
        """ Updates current object state. """
        self.update(self.endpoint.get())
        return self

    def delete(self):
        """ Deletes current set. """
        return self.endpoint.delete()


class Class(Entity):
    """ A wrapper for Quizlet's classes. """

    @property
    def sets(self):
        return [Set(s) for s in self.endpoint.classes(self.id).sets.get()]

    def join(self):
        """ Joins the class. """
        return self.endpoint.users(self.endpoint.login).put()


class User(Entity):
    """ User endpoint wrapper.

    Attributes:
        sets: A list of user's sets.
        favorites: Favourite user's sets.
        studied: A list of user's studying sessions.
        classes: User's classes.
    """
    def __init__(self, name, api):
        super(User, self).__init__()
        self.endpoint = api.users(name)
        self.name = name

    @property
    def sets(self):
        return self.endpoint.sets().get()

    @property
    def studied(self):
        return self.endpoint.studied().get()

    @property
    def classes(self):
        return self.endpoint.classes().get()

    @property
    def favorites(self):
        return self.endpoint.favorites().get()
