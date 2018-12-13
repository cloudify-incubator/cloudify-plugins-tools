import unittest

from mock import Mock

from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

from cloudify_plugin_tools.runner import (
    TaskRunner,
    InstanceTaskRunner,
    RelationshipTaskRunner
)

from cloudify_plugin_tools.constants import SOURCES_DEFAULT_ORDER


class TestTaskRunner(unittest.TestCase):

    RUNNER_CLS = TaskRunner

    def setUp(self):
        self.runner_cls = self.RUNNER_CLS

        self.resolving_rules = []
        self.sources_order = SOURCES_DEFAULT_ORDER

        self.resolver = Mock()

        self.provider_final_input_values = {'a': 1, 'b': 2, 'c': 3}
        self.provider_get_input_arguments = Mock(
            return_value=self.provider_final_input_values
        )
        self.provider = Mock()
        self.provider.get_input_arguments = \
            self.provider_get_input_arguments

        self.api_ctx = Mock()
        self.api_ctx_provider_get_api_ctx = Mock(return_value=self.api_ctx)
        self.api_ctx_provider = Mock()
        self.api_ctx_provider.get_api_ctx = self.api_ctx_provider_get_api_ctx

        self.resolver_cls = Mock(
            return_value=self.resolver
        )
        self.provider_cls = Mock(
            return_value=self.provider
        )
        self.api_ctx_provider_cls = Mock(
            return_value=self.api_ctx_provider
        )
        self.runner_cls.RESOLVER_CLASS = self.resolver_cls
        self.runner_cls.INPUTS_PROVIDER_CLASS = self.provider_cls

        self.mocked_ctx = MockCloudifyContext(
            'node_name',
            properties={},
            runtime_properties={},
        )
        current_ctx.set(self.mocked_ctx)

    def tearDown(self):
        current_ctx.clear()
        super(TestTaskRunner, self).tearDown()

    @property
    def runner_no_api_ctx_provider(self):
        return self.runner_cls(
            self.mocked_ctx,
            self.resolving_rules,
            self.sources_order
        )

    @property
    def runner_with_api_ctx_provider(self):
        return self.runner_cls(
            self.mocked_ctx,
            self.resolving_rules,
            self.sources_order,
            self.api_ctx_provider_cls
        )

    def test_init_no_api_ctx_provider(self):
        # when
        runner = self.runner_no_api_ctx_provider

        # then
        self.assertEquals(runner.ctx, self.mocked_ctx)

        self.resolver_cls.assert_called_once_with(
            self.resolving_rules
        )
        self.assertEquals(runner.inputs_resolver, self.resolver)

        self.provider_cls.assert_called_once_with(
            self.resolver,
            self.sources_order
        )
        self.assertEquals(runner.inputs_provider, self.provider)

    def test_init_with_api_ctx_provider(self):
        # when
        runner = self.runner_with_api_ctx_provider

        # then
        self.assertEquals(runner.ctx, self.mocked_ctx)

        self.resolver_cls.assert_called_once_with(
            self.resolving_rules
        )
        self.assertEquals(runner.inputs_resolver, self.resolver)

        self.provider_cls.assert_called_once_with(
            self.resolver,
            self.sources_order
        )
        self.assertEquals(runner.inputs_provider, self.provider)

        self.api_ctx_provider_cls.assert_called_once()
        self.assertEquals(runner.api_ctx_provider, self.api_ctx_provider)

    def test_prepare_input_arguments(self):
        # given
        kwargs = {'a': 1, 'b': 2}

        # when
        result = self.runner_no_api_ctx_provider.prepare_input_arguments(
            **kwargs
        )

        # then
        self.provider_get_input_arguments.assert_called_once_with(
            self.mocked_ctx,
            **kwargs
        )
        self.assertEquals(result, self.provider_final_input_values)

    def test_prepare_prepare_api_context_with_api_ctx_provider(self):
        # given
        input_parameters = {'user': 'test', 'pass': 'test', 'host': '1.2.3.4'}

        # when
        result = self.runner_with_api_ctx_provider.prepare_api_context(
            input_parameters
        )

        # then
        self.api_ctx_provider_get_api_ctx.assert_called_once_with(
            input_parameters
        )
        self.assertEquals(result, self.api_ctx)

    def test_prepare_prepare_api_context_no_api_ctx_provider(self):
        # given
        input_parameters = {'user': 'test', 'pass': 'test', 'host': '1.2.3.4'}

        # when
        result = self.runner_no_api_ctx_provider.prepare_api_context(
            input_parameters
        )

        # then
        self.api_ctx_provider_get_api_ctx.assert_not_called()
        self.assertIsNone(result)

    def test_do_run_with_api_ctx_provider(self):
        # given
        input_arguments = {'user': 'test', 'pass': 'test', 'host': '1.2.3.4'}
        expected_result = 'some_task_result'
        task = Mock(return_value=expected_result)

        # when
        result = self.runner_with_api_ctx_provider.do_run(
            task,
            input_arguments,
            self.api_ctx
        )

        # then
        task.assert_called_once_with(
            self.mocked_ctx,
            self.api_ctx,
            **input_arguments
        )
        self.assertEquals(result, expected_result)

    def test_do_run_no_api_ctx_provider(self):
        # given
        input_arguments = {'user': 'test', 'pass': 'test', 'host': '1.2.3.4'}
        expected_result = 'some_task_result'
        task = Mock(return_value=expected_result)

        # when
        result = self.runner_with_api_ctx_provider.do_run(
            task,
            input_arguments,
            None
        )

        # then
        task.assert_called_once_with(
            self.mocked_ctx,
            **input_arguments
        )
        self.assertEquals(result, expected_result)

    def test_run_with_api_ctx_provider(self):
        # given
        args = ('fake1', 'fake2', 'fake3')
        kwargs = {'user': 'test', 'pass': 'test', 'host': '1.2.3.4'}
        expected_result = 'some_task_result'
        task = Mock(return_value=expected_result)

        # when
        result = self.runner_with_api_ctx_provider.run(task, *args, **kwargs)

        # then
        self.assertEquals(result, expected_result)

    def test_run_no_api_ctx_provider(self):
        # given
        args = ('fake1', 'fake2', 'fake3')
        kwargs = {'user': 'test', 'pass': 'test', 'host': '1.2.3.4'}
        expected_result = 'some_task_result'
        task = Mock(return_value=expected_result)

        # when
        result = self.runner_with_api_ctx_provider.run(task, *args, **kwargs)

        # then
        self.assertEquals(result, expected_result)


class TestInstanceTaskRunner(TestTaskRunner):

    RUNNER_CLS = InstanceTaskRunner


class TestRelationshipTaskRunner(TestTaskRunner):

    RUNNER_CLS = RelationshipTaskRunner
