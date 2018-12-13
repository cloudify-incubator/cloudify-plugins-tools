import unittest
from mock import Mock, patch

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

from cloudify_sdk_tools.exceptions import TemplateNotFoundError
from cloudify_sdk_tools.rest import RestSDKClient


class TestRestSDKClient(unittest.TestCase):

    TEST_PROJECT_UUID = "ac90331c-a57c-4a08-862c-cd32b0a1366c"

    GET_PROJECT_RESPONSE = {
        "project": {
            "display_name": "default",
            "uuid": "ac90331c-a57c-4a08-862c-cd32b0a1366c",
            "application_policy_set_refs": [{
                "to": [
                    "default-domain",
                    "default",
                    "default-application-policy-set"
                ],
                "href": "http://192.168.14.238:8082/"
                        "application-policy-set/"
                        "a42b0bb5-97b0-41b9-83e0-f2f8231d5ebe",
                "attr": None,
                "uuid": "a42b0bb5-97b0-41b9-83e0-f2f8231d5ebe"
            }],
            "parent_uuid": "790fa6b0-8b58-4665-91be-989375b0870a",
            "parent_href": "http://192.168.14.238:8082/domain/"
                           "790fa6b0-8b58-4665-91be-989375b0870a",
            "parent_type": "domain",
            "perms2": {
                "owner": "None",
                "owner_access": 7,
                "global_access": 0,
                "share": []
            },
            "tag_refs": [{
                "to": ["application=k8s"],
                "href": "http://192.168.14.238:8082/tag/"
                        "2cda4acb-5a7d-4166-b9fb-1ae40d2efa5f",
                "attr": None,
                "uuid": "2cda4acb-5a7d-4166-b9fb-1ae40d2efa5f"
            }],
            "href": "http://192.168.14.238:8082/project/"
                    "ac90331c-a57c-4a08-862c-cd32b0a1366c",
            "id_perms": {
                "enable": True,
                "uuid": {
                    "uuid_mslong": 12434494769298426376,
                    "uuid_lslong": 9668328117653026412
                },
                "created": "2018-06-13T21:18:56.491217",
                "description": None,
                "creator": None,
                "user_visible": True,
                "last_modified": "2018-10-29T08:28:44.760560",
                "permissions": {
                    "owner": "cloud-admin",
                    "owner_access": 7,
                    "other_access": 7,
                    "group": "cloud-admin-group",
                    "group_access": 7
                }
            },
            "fq_name": [
                "default-domain",
                "default"
            ],
            "name": "default"
        }
    }

    EXPECTED_TEMPLATE = "# Input parameters:\n# - uuid\n\n" \
                        "rest_calls:\n" \
                        "  - path: '/project/{{ uuid }}" \
                        "?exclude_back_refs=True&exclude_children=True'\n" \
                        "    method: 'GET'\n" \
                        "    headers:\n" \
                        "      Content-type: 'application/json'\n" \
                        "    response_format: json\n" \
                        "    response_translation:\n" \
                        "      project: [data]"

    def setUp(self):
        _ctx = MockCloudifyContext(
            'node_name',
            properties={},
            runtime_properties={}
        )

        _ctx._execution_id = "execution_id"
        _ctx.instance.host_ip = None

        current_ctx.set(_ctx)
        return _ctx

    def tearDown(self):
        current_ctx.clear()
        super(TestRestSDKClient, self).tearDown()

    def _test_call(self,
                   directory='project',
                   file='get',
                   parameters={'uuid': TEST_PROJECT_UUID},
                   expected_params={'uuid': TEST_PROJECT_UUID},
                   respond_with=GET_PROJECT_RESPONSE,
                   expected_result=GET_PROJECT_RESPONSE,
                   expected_ssl=False,
                   expected_verify=False,
                   **client_parameters):
        # given
        send_rest_request = Mock(return_value={
            'result_properties': respond_with
        })

        with patch(
            'cloudify_sdk_tools.rest.send_rest_request',
            send_rest_request
        ):
            # when
            response = RestSDKClient(**client_parameters).call(
                directory,
                file,
                parameters
            )

            # then
            self.assertEqual(response, expected_result)

            send_rest_request.assert_called_with(
                params=expected_params,
                request_props={
                    'ssl': expected_ssl,
                    'verify': expected_verify,
                    'port': client_parameters.get('port', 80),
                    'hosts': [client_parameters.get('ip')]
                },
                template=self.EXPECTED_TEMPLATE
            )

    def test_call(self):
        self._test_call(
            logger=Mock(),
            module_name='cloudify_sdk_tools.tests',
            ip='host'
        )

    def test_call_ssl(self):
        self._test_call(
            logger=Mock(),
            module_name='cloudify_sdk_tools.tests',
            ip='host',
            ssl=True,
            expected_ssl=True
        )

    def test_call_ssl_str(self):
        self._test_call(
            logger=Mock(),
            module_name='cloudify_sdk_tools.tests',
            ip='host',
            ssl='true',
            expected_ssl=True
        )

    def test_call_ssl_wrong_input(self):
        self._test_call(
            logger=Mock(),
            module_name='cloudify_sdk_tools.tests',
            ip='host',
            ssl=2121221214,
            expected_ssl=False
        )

    def test_call_str(self):
        self._test_call(
            logger=Mock(),
            module_name='cloudify_sdk_tools.tests',
            ip='host',
            ssl=None,
            expected_ssl=False
        )

    def test_call_template_not_found(self):
        with self.assertRaises(TemplateNotFoundError):
            self._test_call(
                directory='not_supported_resource',
                logger=Mock(),
                module_name='cloudify_sdk_tools.tests',
                ip='host'
            )

    def test_call_common_parameters(self):
        expected_params = {'a': 1, 'uuid': self.TEST_PROJECT_UUID}

        self._test_call(
            logger=Mock(),
            module_name='cloudify_sdk_tools.tests',
            ip='host',
            expected_params=expected_params,
            common_parameters={'a': 1}
        )
