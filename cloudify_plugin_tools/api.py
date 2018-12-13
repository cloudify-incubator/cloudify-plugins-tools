class ApiContext(object):

    def __init__(self, client, credentials):
        self.client = client
        self.credentials = credentials


class ApiContextProvider(object):

    def __init__(self, logger):
        self.logger = logger

    def get_api_ctx(self, input_parameters):
        raise NotImplementedError
