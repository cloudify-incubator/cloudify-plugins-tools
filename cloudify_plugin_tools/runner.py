from .input_arguments import (
    InputArgumentProvider,
    InputArgumentResolver,
    InstanceInputArgumentResolver,
    RelationshipInputArgumentResolver
)


class TaskRunner(object):

    RESOLVER_CLASS = InputArgumentResolver

    INPUTS_PROVIDER_CLASS = InputArgumentProvider

    def __init__(self,
                 ctx,
                 resolving_rules,
                 sources_order,
                 api_ctx_provider_cls=None):

        self.ctx = ctx

        self.inputs_resolver = self.RESOLVER_CLASS(resolving_rules)
        self.inputs_provider = self.INPUTS_PROVIDER_CLASS(
            self.inputs_resolver,
            sources_order
        )

        self.api_ctx_provider = api_ctx_provider_cls(ctx.logger) \
            if api_ctx_provider_cls else None

    def prepare_input_arguments(self, **kwargs):
        return self.inputs_provider.get_input_arguments(self.ctx, **kwargs)

    def prepare_api_context(self, input_parameters):
        if self.api_ctx_provider:
            return self.api_ctx_provider.get_api_ctx(input_parameters)

        return None

    def do_run(self, task, input_arguments, api_ctx):
        if api_ctx:
            return task(self.ctx, api_ctx, **input_arguments)

        return task(self.ctx, **input_arguments)

    def run(self, task, *args, **kwargs):
        input_arguments = self.prepare_input_arguments(**kwargs)
        api_ctx = self.prepare_api_context(input_arguments)

        return self.do_run(task, input_arguments, api_ctx)


class RelationshipTaskRunner(TaskRunner):

    RESOLVER_CLASS = RelationshipInputArgumentResolver


class InstanceTaskRunner(TaskRunner):

    RESOLVER_CLASS = InstanceInputArgumentResolver
