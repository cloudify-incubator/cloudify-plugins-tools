from .constants import (
    SOURCE_PROPERTIES,
    SOURCE_RUNTIME_PROPERTIES,
    SOURCE_INPUTS,
    SOURCE_RESOLVE,
    SOURCE_SOURCE_PROPERTIES,
    SOURCE_SOURCE_RUNTIME_PROPERTIES,
    SOURCE_TARGET_PROPERTIES,
    SOURCE_TARGET_RUNTIME_PROPERTIES,
    SOURCES_DEFAULT_ORDER
)
from .exceptions import InputArgumentResolvingError


# Fix for flake 8
try:
    basestring
except NameError:
    basestring = str


class InputArgumentResolvingRule(object):

    def __init__(self,
                 argument_name,
                 node_type=None,
                 relationship_type=None,
                 runtime_properties_path=None):

        self.argument_name = argument_name
        self.node_type = node_type
        self.relationship_type = relationship_type
        self.runtime_properties_path = runtime_properties_path or []

    def check_node_type(self, node_type_hierarchy):
        if self.node_type:
            return self.node_type in node_type_hierarchy

        return True

    def check_relationship_type(self, relationship_type_hierarchy):
        if self.relationship_type:
            return self.relationship_type in relationship_type_hierarchy

        return True

    def check(self, relationship_type_hierarchy, node_type_hierarchy):
        return self.check_relationship_type(relationship_type_hierarchy) and \
               self.check_node_type(node_type_hierarchy)

    def get_runtime_property(self, instance):
        data = instance.runtime_properties

        for name in self.runtime_properties_path:
            if isinstance(name, int) and isinstance(data, list):
                data = data[name]
                continue

            if isinstance(name, basestring) and \
                    isinstance(data, dict) and \
                    name in data:

                data = data[name]
                continue

            raise InputArgumentResolvingError(
                'Cannot resolve {0} - "{1}" key is not present in {2} '
                'value got from runtime_properties'
                .format(str(self), name, data)
            )

        return data

    def evaluate(self, relationship, node, instance):
        if self.check(relationship.type_hierarchy, node.type_hierarchy):
            return True, self.get_runtime_property(instance)

        return False, None

    def __repr__(self):
        details = ''.join(
            '{0}={1}, '.format(k, v)
            for k, v in filter(lambda x: x[1], vars(self).items())
            if not k == 'argument_name'
        )

        return 'input argument "{0}" ({1}) '.format(
            self.argument_name,
            details
        )


class InputArgumentResolver(object):

    def __init__(self, rules):
        self.rules = rules

    def _resolve(self, rule, ctx):
        pass

    def resolve(self, ctx):
        result = {}

        for rule in self.rules:
            result[rule.argument_name] = self._resolve(rule, ctx)

        return result


class InstanceInputArgumentResolver(InputArgumentResolver):

    def _resolve(self, rule, ctx):
        for relationship in ctx.instance.relationships:
            is_successful, result = rule.evaluate(
                relationship,
                relationship.target.node,
                relationship.target.instance
            )

            if is_successful:
                return result

        raise InputArgumentResolvingError(
            'Cannot resolve {0} - no suitable relationships / nodes found'
            .format(str(rule))
        )


class RelationshipInputArgumentResolver(InputArgumentResolver):

    def _get_relationship_ctx(self, ctx):
        for relationship in ctx.source.instance.relationships:
            if relationship.target.instance.id == ctx.target.instance.id:
                return relationship

    def _resolve(self, rule, ctx):
        relationship_ctx = self._get_relationship_ctx(ctx)

        if relationship_ctx:
            is_successful, result = rule.evaluate(
                relationship_ctx,
                ctx.target.node,
                ctx.target.instance
            )

            if is_successful:
                return result

            is_successful, result = rule.evaluate(
                relationship_ctx,
                ctx.source.node,
                ctx.source.instance
            )

            if is_successful:
                return result

        raise InputArgumentResolvingError(
            'Cannot resolve {0} - source and target nodes cannot be used'
            .format(str(rule))
        )


class InputArgumentProvider(object):

    SOURCES = {
        SOURCE_PROPERTIES:
            lambda ctx, provider, kwargs: ctx.node.properties,
        SOURCE_RUNTIME_PROPERTIES:
            lambda ctx, provider, kwargs: ctx.instance.runtime_properties,
        SOURCE_SOURCE_PROPERTIES:
            lambda ctx, provider, kwargs: ctx.source.node.properties,
        SOURCE_SOURCE_RUNTIME_PROPERTIES:
            lambda ctx, provider, kwargs:
            ctx.source.instance.runtime_properties,
        SOURCE_TARGET_PROPERTIES:
            lambda ctx, provider, kwargs: ctx.target.node.properties,
        SOURCE_TARGET_RUNTIME_PROPERTIES:
            lambda ctx, provider, kwargs:
            ctx.target.instance.runtime_properties,
        SOURCE_INPUTS:
            lambda ctx, provider, kwargs: kwargs,
        SOURCE_RESOLVE:
            lambda ctx, provider, kwargs: provider.resolver.resolve(ctx)
            if provider.resolver else {}
    }

    @staticmethod
    def _combine(result, items_to_add):
        for k, v in items_to_add.iteritems():
            if k not in result:
                result[k] = v

    def __init__(self, resolver=None, sources_order=SOURCES_DEFAULT_ORDER):
        self.sources_order = sources_order
        self.resolver = resolver

    def get_input_arguments(self, ctx, **kwargs):
        result_kwargs = {}

        for method_name in self.sources_order:
            if method_name not in self.SOURCES:
                ctx.logger.warn(
                    'Unknown input arguments source: {0}. '
                    'Skipping.'
                    .format(method_name)
                )

                continue

            self._combine(
                result_kwargs,
                self.SOURCES[method_name](ctx, self, kwargs)
            )

        return result_kwargs
