from tortilla.utils import Bunch

__all__ = ['Set', 'Class']


class Entity(Bunch):
    """ A base Quizlet Entity.

    Attributes:
        endpoint(:obj:`.QuizletAPI`): An api's endpoint that points to this object.
            Allows makes requests from within the class.
    """

    def __init__(self, kwargs=None, *, endpoint=None):
        super().__init__(kwargs)
        self.endpoint = endpoint

    def __repr__(self):
        return "{cls}({repr})".format(cls=self.__class__.__name__, repr=super().__repr__())


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
