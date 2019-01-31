import unittest

from cloudify.mocks import (
    MockNodeContext,
    MockNodeInstanceContext,
    MockRelationshipContext,
    MockRelationshipSubjectContext
)
from mock import (
    Mock,
    call
)

from cloudify_plugin_tools.constants import SOURCES_DEFAULT_ORDER
from cloudify_plugin_tools.exceptions import InputArgumentResolvingError
from cloudify_plugin_tools.input_arguments import (
    InputArgumentResolvingRule,
    InputArgumentResolver,
    InstanceInputArgumentResolver,
    RelationshipInputArgumentResolver,
    InputArgumentProvider
)


class TestInputArgumentResolvingRule(unittest.TestCase):

    def setUp(self):
        self.argument_name = 'test_variable'
        self.node_type = 'cloudify.nodes.Test'
        self.relationship_type = 'cloudify.relationships.Test'
        self.runtime_properties_path = ['key', 'nested_key1', 'nested_key2']

        self.full_rule = InputArgumentResolvingRule(
            self.argument_name,
            node_type=self.node_type,
            relationship_type=self.relationship_type,
            runtime_properties_path=self.runtime_properties_path
        )
        self.minimal_rule = InputArgumentResolvingRule(
            self.argument_name
        )

    def test_check_node_type_full_type_in_hierarchy(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root', self.node_type]

        # when
        result = self.full_rule.check_node_type(node_type_hierarchy)

        # then
        self.assertTrue(result)

    def test_check_node_type_full_type_not_in_hierarchy(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root']

        # when
        result = self.full_rule.check_node_type(node_type_hierarchy)

        # then
        self.assertFalse(result)

    def test_check_node_type_minimal_type_in_hierarchy(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root', self.node_type]

        # when
        result = self.minimal_rule.check_node_type(node_type_hierarchy)

        # then
        self.assertTrue(result)

    def test_check_node_type_minimal_type_not_in_hierarchy(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root']

        # when
        result = self.minimal_rule.check_node_type(node_type_hierarchy)

        # then
        self.assertTrue(result)

    def test_check_relationship_type_full_type_in_hierarchy(self):
        # given
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        # when
        result = self.full_rule.check_relationship_type(
            relationship_type_hierarchy
        )

        # then
        self.assertTrue(result)

    def test_check_relationship_type_full_type_not_in_hierarchy(self):
        # given
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to'
        ]

        # when
        result = self.full_rule.check_relationship_type(
            relationship_type_hierarchy
        )

        # then
        self.assertFalse(result)

    def test_check_relationship_type_minimal_type_in_hierarchy(self):
        # given
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        # when
        result = self.minimal_rule.check_relationship_type(
            relationship_type_hierarchy
        )

        # then
        self.assertTrue(result)

    def test_check_relationship_type_minimal_type_not_in_hierarchy(self):
        # given
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to'
        ]

        # when
        result = self.minimal_rule.check_relationship_type(
            relationship_type_hierarchy
        )

        # then
        self.assertTrue(result)

    def test_check_full_positive(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root', self.node_type]
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        # when
        result = self.full_rule.check(
            relationship_type_hierarchy,
            node_type_hierarchy
        )

        # then
        self.assertTrue(result)

    def test_check_full_negative(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root']
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        # when
        result = self.full_rule.check(
            relationship_type_hierarchy,
            node_type_hierarchy
        )

        # then
        self.assertFalse(result)

    def test_check_minimal_positive_1(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root', self.node_type]
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        # when
        result = self.minimal_rule.check(
            relationship_type_hierarchy,
            node_type_hierarchy
        )

        # then
        self.assertTrue(result)

    def test_check_minimal_positive_2(self):
        # given
        node_type_hierarchy = ['cloudify.nodes.Root']
        relationship_type_hierarchy = [
            'cloudify.relationships.connected_to'
        ]

        # when
        result = self.minimal_rule.check(
            relationship_type_hierarchy,
            node_type_hierarchy
        )

        # then
        self.assertTrue(result)

    def test_get_runtime_property_positive_simple_value(self):
        # given
        value = 5
        runtime_properties = {
            'key': {
                'nested_key1': {
                    'nested_key2': value
                }
            },
            'other_key': 'blahblahblah'
        }
        instance_ctx = MockNodeInstanceContext(
            runtime_properties=runtime_properties
        )

        # when
        result = self.full_rule.get_runtime_property(instance_ctx)

        # then
        self.assertEquals(result, value)

    def test_get_runtime_property_positive_list(self):
        # given
        value = 5
        runtime_properties = {
            'key': [
                {},
                {},
                {
                    'nested_key1': {
                        'nested_key2': value
                    }
                },
                {}

            ],
            'other_key': 'blahblahblah'
        }
        instance_ctx = MockNodeInstanceContext(
            runtime_properties=runtime_properties
        )

        rule = InputArgumentResolvingRule(
            self.argument_name,
            node_type=self.node_type,
            relationship_type=self.relationship_type,
            runtime_properties_path=['key', 2, 'nested_key1', 'nested_key2']
        )
        # when
        result = rule.get_runtime_property(instance_ctx)

        # then
        self.assertEquals(result, value)

    def test_get_runtime_property_negative_wrong_runtime_properties(self):
        # given
        runtime_properties = {
            'emptiness': None
        }
        instance_ctx = MockNodeInstanceContext(
            runtime_properties=runtime_properties
        )

        # then
        with self.assertRaises(InputArgumentResolvingError):
            # when
            self.full_rule.get_runtime_property(instance_ctx)

    def test_get_runtime_property_negative_wrong_path(self):
        # given
        value = 5
        runtime_properties = {
            'key': {
                'nested_key1': {
                    'nested_key2': value
                }
            },
            'other_key': 'blahblahblah'
        }
        instance_ctx = MockNodeInstanceContext(
            runtime_properties=runtime_properties
        )

        rule = InputArgumentResolvingRule(
            self.argument_name,
            node_type=self.node_type,
            relationship_type=self.relationship_type,
            runtime_properties_path=['a', 'b', 'cxvcxvcxvxvc']
        )

        # then
        with self.assertRaises(InputArgumentResolvingError):
            # when
            rule.get_runtime_property(instance_ctx)

    def test_evaluate_positive(self):
        # given
        value = 5
        runtime_properties = {
            'key': {
                'nested_key1': {
                    'nested_key2': value
                }
            },
            'other_key': 'blahblahblah'
        }

        node_ctx = MockNodeContext()
        node_ctx.type_hierarchy = ['cloudify.nodes.Root', self.node_type]

        relationship_ctx = MockRelationshipContext(
            target=None,
            type=self.relationship_type
        )
        relationship_ctx.type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        instance_ctx = MockNodeInstanceContext(
            runtime_properties=runtime_properties
        )

        # when
        result = self.full_rule.evaluate(
            relationship_ctx,
            node_ctx,
            instance_ctx
        )

        # then
        self.assertEquals((True, value), result)

    def test_evaluate_negative(self):
        # given
        value = 5
        runtime_properties = {
            'key': {
                'nested_key1': {
                    'nested_key2': value
                }
            },
            'other_key': 'blahblahblah'
        }

        node_ctx = MockNodeContext()
        node_ctx.type_hierarchy = ['cloudify.nodes.Root']

        relationship_ctx = MockRelationshipContext(
            target=None,
            type=self.relationship_type
        )
        relationship_ctx.type_hierarchy = [
            'cloudify.relationships.connected_to',
            self.relationship_type
        ]

        instance_ctx = MockNodeInstanceContext(
            runtime_properties=runtime_properties
        )

        # when
        result = self.full_rule.evaluate(
            relationship_ctx,
            node_ctx,
            instance_ctx
        )

        # then
        self.assertEquals((False, None), result)


class TestInputArgumentResolver(unittest.TestCase):

    def test_resolve_1(self):
        # given
        argument1_name = 'var1'
        argument2_name = 'var2'
        rule1 = InputArgumentResolvingRule(argument1_name)
        rule2 = InputArgumentResolvingRule(argument2_name)
        rules = [rule1, rule2]
        resolve_value = 'some_value'

        resolver = InputArgumentResolver(rules)
        _resolve_mock = Mock(return_value=resolve_value)
        resolver._resolve = _resolve_mock
        ctx_mock = Mock()

        # when
        result = resolver.resolve(ctx_mock)

        # then
        self.assertEquals(result, {
            argument1_name: resolve_value,
            argument2_name: resolve_value
        })

        expected_calls = [
            call(rule1, ctx_mock),
            call(rule2, ctx_mock)
        ]

        _resolve_mock.assert_has_calls(expected_calls)

    def test_resolve_2(self):
        # given
        argument1_name = 'var1'
        argument2_name = 'var2'
        rule1 = InputArgumentResolvingRule(argument1_name)
        rule2 = InputArgumentResolvingRule(argument2_name)
        rules = [rule1, rule2]

        resolver = InputArgumentResolver(rules)
        ctx_mock = Mock()

        # when
        result = resolver.resolve(ctx_mock)

        # then
        self.assertEquals(result, {
            argument1_name: None,
            argument2_name: None
        })


class TestInstanceInputArgumentResolver(unittest.TestCase):

    def test_resolve_positive(self):
        # given
        argument1_name = 'var1'
        argument2_name = 'var2'

        rule1 = Mock()
        rule1.argument_name = argument1_name
        rule1_evaluate_value = 'value1'
        rule1_evaluate_mock = Mock(return_value=(True, rule1_evaluate_value))
        rule1.evaluate = rule1_evaluate_mock

        rule2 = Mock()
        rule2.argument_name = argument2_name
        rule2_evaluate_value = 'value2'
        rule2_evaluate_mock = Mock(return_value=(True, rule2_evaluate_value))
        rule2.evaluate = rule2_evaluate_mock

        rules = [rule1, rule2]

        resolver = InstanceInputArgumentResolver(rules)
        relationship_target_node_mock = Mock()
        relationship_target_instance_mock = Mock()
        relationship_mock = MockRelationshipContext(
            target=MockRelationshipSubjectContext(
                node=relationship_target_node_mock,
                instance=relationship_target_instance_mock
            ),
            type='cloudify.relationships.connected_to'
        )
        ctx_mock = Mock()
        ctx_instance_mock = Mock()
        ctx_instance_mock.relationships = [relationship_mock]
        ctx_mock.instance = ctx_instance_mock

        # when
        result = resolver.resolve(ctx_mock)

        # then
        self.assertEquals(result, {
            argument1_name: rule1_evaluate_value,
            argument2_name: rule2_evaluate_value
        })

        rule1_evaluate_mock.assert_called_once_with(
            relationship_mock,
            relationship_target_node_mock,
            relationship_target_instance_mock
        )

        rule2_evaluate_mock.assert_called_once_with(
            relationship_mock,
            relationship_target_node_mock,
            relationship_target_instance_mock
        )

    def test_resolve_negative(self):
        # given
        argument1_name = 'var1'
        rule1 = Mock()
        rule1.argument_name = argument1_name
        rule1_evaluate_value = None
        rule1_evaluate_mock = Mock(return_value=(False, rule1_evaluate_value))
        rule1.evaluate = rule1_evaluate_mock

        rules = [rule1]

        resolver = InstanceInputArgumentResolver(rules)
        relationship_target_node_mock = Mock()
        relationship_target_instance_mock = Mock()
        relationship_mock = MockRelationshipContext(
            target=MockRelationshipSubjectContext(
                node=relationship_target_node_mock,
                instance=relationship_target_instance_mock
            ),
            type='cloudify.relationships.connected_to'
        )
        ctx_mock = Mock()
        ctx_instance_mock = Mock()
        ctx_instance_mock.relationships = [relationship_mock]
        ctx_mock.instance = ctx_instance_mock

        # then
        with self.assertRaises(InputArgumentResolvingError):
            # when
            resolver.resolve(ctx_mock)


class TestRelationshipInputArgumentResolver(unittest.TestCase):

    def test_resolve_positive(self):
        # given
        argument1_name = 'var1'
        argument2_name = 'var2'

        relationship_target_node_mock = Mock()
        relationship_target_instance_mock = Mock()
        relationship_target_instance_mock.id = '5'

        relationship_source_node_mock = Mock()
        relationship_source_instance_mock = Mock()
        relationship_ctx = MockRelationshipContext(
            target=MockRelationshipSubjectContext(
                node=relationship_target_node_mock,
                instance=relationship_target_instance_mock
            )
        )

        relationship_source_instance_mock.relationships = [
            relationship_ctx
        ]

        rule1 = Mock()
        rule1.argument_name = argument1_name
        rule1_evaluate_value = 'value1'
        rule1_evaluate_mock = Mock(
            side_effect=lambda ctx, node, instance:
            (True, rule1_evaluate_value)
            if (
                    node == relationship_source_node_mock and
                    instance == relationship_source_instance_mock
            )
            else (False, None)
        )
        rule1.evaluate = rule1_evaluate_mock

        rule2 = Mock()
        rule2.argument_name = argument2_name
        rule2_evaluate_value = 'value2'
        rule2_evaluate_mock = Mock(
            side_effect=lambda ctx, node, instance:
            (True, rule2_evaluate_value)
            if (
                    node == relationship_target_node_mock and
                    instance == relationship_target_instance_mock
            )
            else (False, None)
        )
        rule2.evaluate = rule2_evaluate_mock

        rules = [rule1, rule2]

        resolver = RelationshipInputArgumentResolver(rules)

        ctx_mock = Mock()
        ctx_mock.target = MockRelationshipSubjectContext(
            node=relationship_target_node_mock,
            instance=relationship_target_instance_mock
        )
        ctx_mock.source = MockRelationshipSubjectContext(
            node=relationship_source_node_mock,
            instance=relationship_source_instance_mock
        )
        # when
        result = resolver.resolve(ctx_mock)

        # then
        self.assertEquals(result, {
            argument1_name: rule1_evaluate_value,
            argument2_name: rule2_evaluate_value
        })

        rule1_evaluate_mock_expected_calls = [
            call(
                relationship_ctx,
                relationship_target_node_mock,
                relationship_target_instance_mock
            ),
            call(
                relationship_ctx,
                relationship_source_node_mock,
                relationship_source_instance_mock
            )
        ]

        rule1_evaluate_mock.assert_has_calls(
            rule1_evaluate_mock_expected_calls
        )

        rule2_evaluate_mock_expected_calls = [
            call(
                relationship_ctx,
                relationship_target_node_mock,
                relationship_target_instance_mock
            )
        ]

        rule2_evaluate_mock.assert_has_calls(
            rule2_evaluate_mock_expected_calls
        )

    def test_resolve_negative(self):
        # given
        argument1_name = 'var1'
        argument2_name = 'var2'

        relationship_target_node_mock = Mock()
        relationship_target_instance_mock = Mock()
        relationship_target_instance_mock.id = '6'

        relationship_source_node_mock = Mock()
        relationship_source_instance_mock = Mock()
        relationship_ctx = MockRelationshipContext(
            target=MockRelationshipSubjectContext(
                node=relationship_target_node_mock,
                instance=relationship_target_instance_mock
            )
        )

        relationship_source_instance_mock.relationships = [
            relationship_ctx
        ]

        rule1 = Mock()
        rule1.argument_name = argument1_name
        rule1_evaluate_value = 'value1'
        rule1_evaluate_mock = Mock(
            side_effect=lambda ctx, node, instance:
            (True, rule1_evaluate_value)
            if (
                    node == relationship_source_node_mock and
                    instance == relationship_source_instance_mock
            )
            else (False, None)
        )
        rule1.evaluate = rule1_evaluate_mock

        rule2 = Mock()
        rule2.argument_name = argument2_name
        rule2_evaluate_mock = Mock(return_value=(False, None))
        rule2.evaluate = rule2_evaluate_mock

        rules = [rule1, rule2]

        resolver = RelationshipInputArgumentResolver(rules)

        ctx_mock = Mock()
        ctx_mock.target = MockRelationshipSubjectContext(
            node=relationship_target_node_mock,
            instance=relationship_target_instance_mock
        )
        ctx_mock.source = MockRelationshipSubjectContext(
            node=relationship_source_node_mock,
            instance=relationship_source_instance_mock
        )

        # then
        with self.assertRaises(InputArgumentResolvingError):
            # when
            resolver.resolve(ctx_mock)


class TestInputArgumentProvider(unittest.TestCase):

    def setUp(self):
        self.properties = {'a': 1, 'b': 2}
        self.runtime_properties = {'a': 1, 'b': 2, 'c': 3}
        self.input_args = {'b': 11, 'c': 4, 'd': 5, 'e': 6}
        self.resolved_values = {'a': 10, 'd': 7, 'e': 8, 'f': 9}
        self.expected_result = {
            'a': 1, 'b': 2, 'c': 3, 'd': 5, 'e': 6, 'f': 9
        }

        self.mocked_node = MockNodeContext(
            properties=self.properties
        )
        self.mocked_instance = MockNodeInstanceContext(
            runtime_properties=self.runtime_properties
        )
        self.mocked_logger = Mock()
        self.mocked_logger_warn = Mock()
        self.mocked_logger.warn = self.mocked_logger_warn

        self.mocked_ctx = Mock()
        self.mocked_ctx.node = self.mocked_node
        self.mocked_ctx.instance = self.mocked_instance
        self.mocked_ctx.logger = self.mocked_logger

        self.mocked_resolver = Mock()
        self.mocked_resolver_resolve = Mock(return_value=self.resolved_values)
        self.mocked_resolver.resolve = self.mocked_resolver_resolve

    def test_get_input_arguments(self):
        # given
        provider = InputArgumentProvider(
            self.mocked_resolver,
            SOURCES_DEFAULT_ORDER
        )

        # when
        result = provider.get_input_arguments(
            self.mocked_ctx,
            **self.input_args
        )

        # then
        self.assertEquals(result, self.expected_result)
        self.mocked_resolver_resolve.assert_called_once_with(self.mocked_ctx)

    def test_get_input_arguments_unknown_method(self):
        # given
        provider = InputArgumentProvider(
            self.mocked_resolver,
            ['unknown_method']
        )

        # when
        result = provider.get_input_arguments(
            self.mocked_ctx,
            **self.input_args
        )

        # then
        self.assertEquals(result, {})
        self.mocked_resolver_resolve.assert_not_called()
        self.mocked_logger_warn.assert_called_once()
