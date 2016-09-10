Tutorial
========

This package wraps `Quizlet API <https://quizlet.com/api/2.0/docs>`_.

In order to use this module you should register your application on you profile's
`settings page <https://quizlet.com/settings>`_ and initialize `:class:QuizletClient` instance with your `client_id`.

 .. code-block:: python

    import quizlet
    client = quizlet.QuizletClient(client_id='my_client_id', login='me')

Or you can use Oauth 2.0 access token. This way will gives additional opportunities
depending on token's `scope <https://quizlet.com/api/2.0/docs/scopes>`_:

 .. code-block:: python

    import quizlet
    client = quizlet.QuizletClient(token='bla bla bla', login='me')

.. note::

    Argument `login` is required to make user-related requests (for instance to retrieve user's :class:`~quizlet.Set` s).


Once the client is initialized, you can use its :attr:`api` attribute to make http requests.
It's some sort of a low level of making requests.

.. code-block:: python

   client.api.search.sets.get(params={'q': 'Python'})

Here is a simplier analog:

.. code-block:: python

   client.sets.search(query='Python')


Here are some examples of this module is capable of:

.. code-block:: python

    # Get client's sets
    for set in client.sets:
        print(set.id)

    # Create a new set (if you have permissions to do it)
    s = client.sets.create(title='My first set from python',
                           terms=['Hello'], lang_terms='en',
                           definitions=['Bonjour'], lang_definitions='fr')

    # Delete the set
    s.delete()

    # Search for classes:
    for cls in client.classes.search(query='Python', max_items=30):
        # Do something
        pass

    # Join a class
    cls.join()


.. note::
   If some argument is invalid or you are not authorized to perform particular action a
   :class:`~quizlet.QuizletError` will be raised.
   Don't worry, they usually contain a good explanation of what's going wrong.