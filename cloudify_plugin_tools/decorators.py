from cloudify.exceptions import (
    NonRecoverableError,
    RecoverableError
)

from .constants import SOURCES_DEFAULT_ORDER
from .exceptions import (
    reraise,
    COMMON_RECOVERABLE_EXCEPTIONS,
    COMMON_NON_RECOVERABLE_EXCEPTIONS
)


class run_with(object):

    def __init__(self,
                 runner_class,
                 input_arguments_resolve_rules=None,
                 input_arguments_sources_order=SOURCES_DEFAULT_ORDER,
                 api_ctx_provider_cls=None,
                 non_recoverable_exceptions=(),
                 recoverable_exceptions=()):

        self.runner_class = runner_class
        self.input_arguments_resolve_rules = input_arguments_resolve_rules
        self.input_arguments_sources_order = input_arguments_sources_order
        self.api_ctx_provider_cls = api_ctx_provider_cls
        self.non_recoverable_exceptions = non_recoverable_exceptions
        self.recoverable_exceptions = recoverable_exceptions

    def __call__(self, func):
        def _do_call(ctx, *args, **kwargs):
            self.call(func, ctx, *args, **kwargs)

        return _do_call

    def call(self, func, ctx, *args, **kwargs):
        if self.runner_class:
            try:
                self.runner_class(
                    ctx,
                    self.input_arguments_resolve_rules or [],
                    self.input_arguments_sources_order,
                    self.api_ctx_provider_cls
                ).run(func, *args, **kwargs)
            except (NonRecoverableError, RecoverableError):
                raise
            except COMMON_NON_RECOVERABLE_EXCEPTIONS:
                reraise(NonRecoverableError)
            except self.non_recoverable_exceptions:
                reraise(NonRecoverableError)
            except COMMON_RECOVERABLE_EXCEPTIONS:
                reraise(RecoverableError)
            except self.recoverable_exceptions:
                reraise(RecoverableError)
            except BaseException:
                reraise(
                    RecoverableError,
                    'Unknown exception during task execution - '
                    'trying to rerun task'
                )
        else:
            raise NonRecoverableError(
                'Cannot run {0} task. Runner class is not defined.'
                .format(func)
            )
