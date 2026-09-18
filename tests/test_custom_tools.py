import copy
import json
from pathlib import Path
import runpy
import unittest

BRIDGE = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'custom_tools.py'))


class CustomTools(unittest.TestCase):
    def setUp(self):
        self.request = {'tools': [{'type': 'custom', 'name': 'apply_patch',
                                   'description': 'Apply a patch',
                                   'format': {'type': 'grammar', 'definition': 'start: "patch"'}},
                                  {'type': 'function', 'name': 'exec_command', 'parameters': {}}],
                        'input': [{'type': 'custom_tool_call', 'name': 'apply_patch',
                                   'call_id': 'call-one', 'input': 'patch'},
                                  {'type': 'custom_tool_call_output', 'call_id': 'call-one', 'output': 'ok'}]}

    def test_request_and_history_round_trip(self):
        before = copy.deepcopy(self.request)
        encoded = BRIDGE['encode_request'](self.request)
        self.assertEqual(self.request, before)
        self.assertEqual(encoded['tools'][0]['type'], 'function')
        self.assertIn('start: "patch"', encoded['tools'][0]['description'])
        self.assertIn('bare @@ line', encoded['tools'][0]['description'])
        self.assertEqual(encoded['input'][0]['type'], 'function_call')
        self.assertEqual(json.loads(encoded['input'][0]['arguments']), {'input': 'patch'})
        self.assertEqual(encoded['input'][1]['type'], 'function_call_output')
        self.assertEqual(encoded['tools'][1], self.request['tools'][1])

    def test_stream_sequence_preserves_raw_input_and_ids(self):
        decoder = BRIDGE['CustomToolDecoder'](self.request)
        item = {'type': 'function_call', 'name': 'apply_patch', 'id': 'fc-one',
                'call_id': 'call-one', 'arguments': ''}
        added = decoder({'type': 'response.output_item.added', 'item': item})
        self.assertEqual(added['item']['type'], 'custom_tool_call')
        self.assertEqual(added['item']['input'], '')
        raw = '*** Begin Patch\n*** Add File: café.txt\n+"hello"\n*** End Patch'
        args = json.dumps({'input': raw})
        delta = decoder({'type': 'response.function_call_arguments.delta', 'item_id': 'fc-one', 'delta': args})
        self.assertEqual(delta['type'], 'response.custom_tool_call_input.delta')
        self.assertEqual(delta['delta'], raw)
        done = decoder({'type': 'response.function_call_arguments.done', 'item_id': 'fc-one', 'arguments': args})
        self.assertEqual(done['input'], raw)
        final_item = decoder({'type': 'response.output_item.done', 'item': {**item, 'arguments': args}})['item']
        self.assertEqual(final_item['input'], raw)
        self.assertEqual(final_item['call_id'], 'call-one')
        terminal = decoder({'type': 'response.completed', 'response': {'output': [{**item, 'arguments': args}]}})
        self.assertEqual(terminal['response']['output'], [final_item])

    def test_regular_function_events_unchanged(self):
        decoder = BRIDGE['CustomToolDecoder'](self.request)
        event = {'type': 'response.output_item.added', 'item': {'type': 'function_call', 'name': 'exec_command', 'id': 'normal', 'arguments': ''}}
        self.assertEqual(decoder(event), event)

    def test_missing_input_is_rejected(self):
        with self.assertRaises(ValueError):
            BRIDGE['raw_input']('{"cmd":"unexpected"}')

    def test_forced_custom_choice(self):
        self.request['tool_choice'] = {'type': 'custom', 'name': 'apply_patch'}
        encoded = BRIDGE['encode_request'](self.request)
        self.assertEqual(encoded['tool_choice'], {'type': 'function', 'name': 'apply_patch'})

    def test_null_tools_are_supported(self):
        self.assertEqual(BRIDGE['encode_request']({'tools': None, 'input': 'hello'}),
                         {'tools': None, 'input': 'hello'})
        self.assertEqual(BRIDGE['custom_names']({'tools': None}), set())

    def test_union_types_are_collapsed_for_google(self):
        # Antigravity answers HTTP 400 for `"type": ["number", "null"]` and names nothing, so this
        # is the shape that has to leave the gateway: one concrete type plus Gemini's `nullable`.
        request = {'tools': [{'type': 'function', 'name': 'grep', 'parameters': {
            'type': 'object',
            'properties': {
                'pattern': {'type': 'string'},
                'skip': {'type': ['number', 'null']},
                'rows': {'type': 'array', 'items': {'type': ['string', 'null']}},
            },
            'required': ['pattern'],
        }}]}
        properties = BRIDGE['encode_request'](request)['tools'][0]['parameters']['properties']
        self.assertEqual(properties['skip'], {'type': 'number', 'nullable': True})
        self.assertEqual(properties['rows']['items'], {'type': 'string', 'nullable': True})
        self.assertEqual(properties['pattern'], {'type': 'string'})

    def test_property_named_type_survives_the_collapse(self):
        request = {'tools': [{'type': 'function', 'name': 'shape', 'parameters': {
            'type': 'object',
            'properties': {'type': {'type': ['string', 'null']}},
            'required': ['type'],
        }}]}
        parameters = BRIDGE['encode_request'](request)['tools'][0]['parameters']
        self.assertEqual(parameters['type'], 'object')
        self.assertEqual(parameters['properties']['type'], {'type': 'string', 'nullable': True})
        self.assertEqual(parameters['required'], ['type'])
