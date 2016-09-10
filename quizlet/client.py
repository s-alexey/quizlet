import requests
import tortilla

BASE_URL = 'https://api.quizlet.com/2.0/'

__all__ = ['QuizletAPI', 'QuizletError', 'BASE_URL']


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

    def __init__(self, *, client_id=None, token=None, login=None, **kwargs):
        kwargs.setdefault('part', BASE_URL)
        if client_id:
            kwargs['params'] = {'client_id': client_id}
        if token:
            kwargs['headers'] = {'Authorization': 'Bearer {}'.format(token)}
        super().__init__(**kwargs)
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
            return super().request(method, *parts, **options)
        except requests.HTTPError as e:
            if 400 <= e.response.status_code < 500:
                # Do not raise new exception.
                e.__class__ = QuizletError
            raise e

    def __call__(self, *args, **kwargs):
        """ Replaces result or super class' method with an QuizletAPI analogue."""
        result = super().__call__(*args, **kwargs)
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
