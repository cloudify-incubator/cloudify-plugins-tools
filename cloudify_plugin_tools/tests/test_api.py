import unittest
from mock import Mock

from cloudify_plugin_tools import api


class TestApiContext(unittest.TestCase):

    def test_init(self):
        # given
        credentials = Mock()
        client = Mock()

        # when
        api_ctx = api.ApiContext(client, credentials)

        # then
        self.assertEquals(api_ctx.client, client)
        self.assertEquals(api_ctx.credentials, credentials)


class TestApiContextProvider(unittest.TestCase):

    def test_init(self):
        # given
        logger = Mock()

        # when
        api_ctx_provider = api.ApiContextProvider(logger)

        # then
        self.assertEquals(api_ctx_provider.logger, logger)

    def test_get_api_ctx(self):
        # given
        api_ctx_provider = api.ApiContextProvider(Mock())
        input_paramaters = Mock()

        # then
        with self.assertRaises(NotImplementedError):
            # when
            api_ctx_provider.get_api_ctx(input_paramaters)
