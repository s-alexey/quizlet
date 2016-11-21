import requests
import tortilla
from . import entities

BASE_URL = 'https://api.quizlet.com/2.0/'

__all__ = ['QuizletAPI', 'QuizletError', 'BASE_URL', 'QuizletClient']


class QuizletClient:
    """ A main class that holds a QuizletAPI and some managers. """

    def __init__(self, client_id=None, token=None, login=None):
        self.api = QuizletAPI(client_id=client_id, token=token, login=login)
        self.sets = SetManager(self.api)
        self.classes = ClassManager(self.api)

    def user(self, username):
        return entities.User(username, self.api)


class QuizletError(requests.HTTPError):
    """ Custom HTTP exception. """

    def __str__(self):
        try:
            # Adds json with a description of an error.
            return "{}\n{}".format(super().__str__(), self.response.json())
        except ValueError:
            return super().__str__()


class QuizletAPI(tortilla.Wrap):
    """ A client for Quizlet API. """

    def __init__(self, client_id=None, token=None, login=None, **kwargs):
        kwargs.setdefault('part', BASE_URL)
        if client_id:
            kwargs['params'] = {'client_id': client_id}
        if token:
            kwargs['headers'] = {'Authorization': 'Bearer {}'.format(token)}
        super(QuizletAPI, self).__init__(**kwargs)
        self.login = login

    def __getattr__(self, part):
        try:
            return self.__dict__[part]
        except KeyError:
            return self._chain(part)

    def _chain(self, part):
        """ Semi-public interface to create sub wrapper.
        Allows chainable requests with not valid python identifiers.
        """
        return self.__class__(part=part, parent=self,
                              debug=self.config.get('debug'))

    def request(self, method, *parts, **options):
        """ Makes request.

        Raises:
             QuizletError: If there in case there is a mistake in submitted data.
             HTTPError: If some error occurs in network or on the server.
        """
        try:
            return super(QuizletAPI, self).request(method, *parts, **options)
        except requests.HTTPError as e:
            if 400 <= e.response.status_code < 500:
                # Do not raise new exception.
                e.__class__ = QuizletError
            raise e

    def __call__(self, *args, **kwargs):
        """ Replaces result or super class' method with an QuizletAPI analogue."""
        result = super(QuizletAPI, self).__call__(*args, **kwargs)
        result.__class__ = QuizletAPI
        return result

    def items(self, max_items=None, params=None):
        """ Iterates over items related to this endpoint. """
        data = self.get(params=params)
        if isinstance(data, list):
            return data

        for item in data[self._part]:
            yield item

        params = params or {}
        for page_id in range(2, data['total_pages'] + 1):
            item_count = 0
            items = self.get(params={'page': page_id, **params})[self._part]
            for item in items:
                yield item
                item_count += 1

                if max_items is not None and item_count > max_items:
                    return

    @property
    def user_url(self):
        """ User profile endpoint. """
        return self.users(self.login)


class EntityManager:
    _name = NotImplemented
    _entity = NotImplemented

    @property
    def _plural(self):
        return self._name + 's'

    @property
    def endpoint(self):
        return getattr(self.api, self._plural)

    def __init__(self, api):
        self.api = api

    def new_entity(self, data):
        """ Creates a new entity from the retrieved data. """
        return self._entity(data, endpoint=self.endpoint(data['id']))

    def __call__(self, id=None, ids=None, **kwargs):
        """ Returns either user's entities or specified by id(s).

        Arguments:
            id(:obj:`str`): An entity's id.
            ids(:obj:`list` of :obj:`str`): An entities' ids.
        """
        if ids is not None:
            return self.endpoint.get(params={self._name + '_ids': ids})
        elif id is not None:
            return self.new_entity(self.endpoint(id).get())

        return getattr(self.api.user_url, self._plural).get(params=kwargs)

    def create(self, **kwargs):
        """ Creates a new entity. """
        return self.new_entity(self.endpoint.post(data=kwargs))

    def search(self, query, max_items=None, **params):
        """ Searches for the public item. """
        endpoint = getattr(self.api.search, self._plural)
        return [self.new_entity(item) for item in
                endpoint(params=dict(q=query, **params)).items(max_items=max_items)]

    def __iter__(self):
        return self.endpoint.items()


class SetManager(EntityManager):
    _name = 'set'
    _entity = entities.Set

    def create(self, title, terms, lang_terms, definitions, lang_definitions):
        # Gets the idea of what must be present here.
        return super(SetManager, self).create(title=title, terms=terms, lang_terms=lang_terms,
                                              definitions=definitions, lang_definitions=lang_definitions)


class ClassManager(EntityManager):
    _name = 'class'
    _plural = 'classes'
    _entity = entities.Class
