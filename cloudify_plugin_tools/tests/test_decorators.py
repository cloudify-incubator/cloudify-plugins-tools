import unittest
import cloudify_plugin_tools.decorators as decorators

from mock import Mock

from cloudify.exceptions import (
    NonRecoverableError,
    RecoverableError
)
from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

from cloudify_plugin_tools import InputArgumentResolvingRule
from cloudify_plugin_tools.constants import SOURCES_DEFAULT_ORDER
from cloudify_plugin_tools.decorators import run_with
from cloudify_plugin_tools.exceptions import UnreachableApiError


class TestRunWith(unittest.TestCase):

    class MockedRunner(object):

        def __init__(self,
                     ctx,
                     resolving_rules,
                     sources_order,
                     api_ctx_provider_cls=None):

            self.ctx = ctx
            self.resolving_rules = resolving_rules
            self.sources_order = sources_order
            self.api_ctx_provider_cls = api_ctx_provider_cls

        def run(self, task, *args, **kwargs):
            task(args, kwargs, **vars(self))

    class MockedTask(object):

        class Call(object):

            def __init__(self,
                         ctx,
                         resolving_rules,
                         sources_order,
                         api_ctx_provider_cls,
                         args,
                         kwargs):

                self.ctx = ctx
                self.resolving_rules = resolving_rules
                self.sources_order = sources_order
                self.api_ctx_provider_cls = api_ctx_provider_cls
                self.args = args
                self.kwargs = kwargs

        def __init__(self):
            self.calls = []

        def __call__(self, args, kwargs, **runner_properties):
            self.calls.append(
                self.Call(
                    args=args,
                    kwargs=kwargs,
                    **runner_properties
                )
            )

    def _mock_ctx(self):
        _ctx = MockCloudifyContext(
            'node_name',
            properties={},
            runtime_properties={}
        )

        return _ctx

    def setUp(self):
        self.mocked_ctx = self._mock_ctx()
        current_ctx.set(self.mocked_ctx)

        self.default_runner_class = self.MockedRunner
        self.default_input_arguments_resolve_rules = [
            InputArgumentResolvingRule(
                argument_name='some_var',
                node_type='cloudify.nodes.some_plugin.SomeType',
                runtime_properties_path=['object_reference']
            )
        ]
        self.default_input_arguments_sources_order = SOURCES_DEFAULT_ORDER
        self.default_api_ctx_provider_cls = Mock
        self.default_non_recoverable_exceptions = (RuntimeError,)
        self.default_recoverable_exceptions = (IOError,)

        self.some_args = ('x', 'y', 'z')
        self.some_kwargs = {'a': 1, 'b': 2, 'c': 3}

    def tearDown(self):
        current_ctx.clear()
        super(TestRunWith, self).tearDown()

    @property
    def default_init_input_args(self):
        return {
            'runner_class':
                self.default_runner_class,
            'input_arguments_resolve_rules':
                self.default_input_arguments_resolve_rules,
            'input_arguments_sources_order':
                self.default_input_arguments_sources_order,
            'api_ctx_provider_cls':
                self.default_api_ctx_provider_cls,
            'non_recoverable_exceptions':
                self.default_non_recoverable_exceptions,
            'recoverable_exceptions':
                self.default_recoverable_exceptions
        }

    def assert_default_call(self, call):
        self.assertEquals(call.ctx, self.mocked_ctx)
        self.assertEquals(
            call.resolving_rules,
            self.default_input_arguments_resolve_rules
        )
        self.assertEquals(
            call.sources_order,
            self.default_input_arguments_sources_order
        )
        self.assertEquals(
            call.api_ctx_provider_cls,
            self.default_api_ctx_provider_cls
        )
        self.assertEquals(call.args, self.some_args)
        self.assertEquals(call.kwargs, self.some_kwargs)

    def test_call_full_init_no_exceptions(self):
        # given
        task = self.MockedTask()

        # when
        run_with(**self.default_init_input_args).call(
            task,
            self.mocked_ctx,
            *self.some_args,
            **self.some_kwargs
        )

        # then
        self.assertEquals(len(task.calls), 1)
        self.assert_default_call(task.calls[0])

    def test_call_minimal_init_no_exceptions(self):
        # given
        task = self.MockedTask()

        # when
        run_with(self.default_runner_class).call(
            task,
            self.mocked_ctx,
        )

        # then
        self.assertEquals(len(task.calls), 1)

        call = task.calls[0]
        self.assertEquals(call.ctx, self.mocked_ctx)
        self.assertEquals(call.resolving_rules, [])
        self.assertEquals(call.sources_order, SOURCES_DEFAULT_ORDER)
        self.assertEquals(call.api_ctx_provider_cls, None)
        self.assertEquals(call.args, ())
        self.assertEquals(call.kwargs, {})

    def test_call_full_init_no_runner(self):
        # given
        task = self.MockedTask()

        # then
        with self.assertRaises(NonRecoverableError):
            # when
            run_with(None).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_init_recoverableerror_reraise(self):
        # given
        def task(args, kwargs, **rp):
            raise RecoverableError()

        # then
        with self.assertRaises(RecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_init_nonrecoverableerror_reraise(self):
        # given
        def task(args, kwargs, **rp):
            raise NonRecoverableError()

        # then
        with self.assertRaises(NonRecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_init_common_recoverable_exception(self):
        # given
        def task(args, kwargs, **rp):
            raise IOError()

        # then
        with self.assertRaises(RecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_init_common_nonrecoverable_exception(self):
        # given
        def task(args, kwargs, **rp):
            raise RuntimeError()

        # then
        with self.assertRaises(NonRecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_init_recoverable_exception(self):

        # given
        def task(args, kwargs, **rp):
            raise UnreachableApiError()

        # then
        with self.assertRaises(NonRecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_init_nonrecoverable_exception(self):
        # given
        def task(args, kwargs, **rp):
            raise AttributeError()

        decorators.COMMON_RECOVERABLE_EXCEPTIONS = (AttributeError)

        # then
        with self.assertRaises(RecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test_call_full_unknown_exception(self):
        # given
        def task(args, kwargs, **rp):
            raise KeyError()

        # then
        with self.assertRaises(RecoverableError):
            # when
            run_with(**self.default_init_input_args).call(
                task,
                self.mocked_ctx,
                *self.some_args,
                **self.some_kwargs
            )

    def test__call__(self):
        # given
        task = self.MockedTask()
        mocked_run_with_call = Mock()
        rw = run_with(**self.default_init_input_args)
        rw.call = mocked_run_with_call

        # when
        rw(task)(self.mocked_ctx, self.some_args, self.some_kwargs)

        # then
        mocked_run_with_call.assert_called_once()
