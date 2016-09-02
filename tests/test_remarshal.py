#! /usr/bin/env python

from .context import remarshal
import os
import os.path
import re
import tempfile
import unittest


TEST_DATA_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def test_file_path(filename):
    return os.path.join(TEST_DATA_PATH, filename)


def readFile(filename):
    with open(test_file_path(filename), 'rb') as f:
        content = f.read().decode('utf-8')
    return content


def tomlSignature(data):
    '''A lossy representation for TOML example data for comparison.'''
    def strip_more(line):
        return re.sub(r' *#.*$', '', line.strip()).replace(' ', '')
    def f(lst):
        def q(line):
            return line.startswith('#') or line == u'' or line == u']' or \
                    re.match(r'^".*",?$', line) or re.match(r'^hosts', line)
        return sorted([strip_more(line) for line in lst if
                not q(strip_more(line))])
    return f(data.split("\n"))


class TestRemarshal(unittest.TestCase):

    def tempFilename(self):
        temp_filename = tempfile.mkstemp()[1]
        self.temp_files.append(temp_filename)
        return temp_filename

    def convertAndRead(self, input, input_format, output_format,
                        indent_json=True, wrap=None, unwrap=None):
        output_filename = self.tempFilename()
        remarshal.remarshal(test_file_path(input), output_filename,
                            input_format, output_format,
                            indent_json=indent_json, wrap=wrap, unwrap=unwrap)
        return readFile(output_filename)

    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        for filename in self.temp_files:
            os.remove(filename)

    def test_json2json(self):
        output = self.convertAndRead('example.json', 'json', 'json')
        reference = readFile('example.json')
        self.assertEqual(output, reference)

    def test_toml2toml(self):
        output = self.convertAndRead('example.toml', 'toml', 'toml')
        reference = readFile('example.toml')
        self.assertEqual(tomlSignature(output), tomlSignature(reference))

    def test_yaml2yaml(self):
        output = self.convertAndRead('example.yaml', 'yaml', 'yaml')
        reference = readFile('example.yaml')
        self.assertEqual(output, reference)

    def test_json2toml(self):
        output = self.convertAndRead('example.json', 'json', 'toml')
        reference = readFile('example.toml')
        output_sig = tomlSignature(output)
        # The date in 'example.json' is a string.
        reference_sig = tomlSignature(reference.
                replace('1979-05-27T07:32:00Z', '"1979-05-27T07:32:00+00:00"'))
        self.assertEqual(output_sig, reference_sig)

    def test_json2yaml(self):
        output = self.convertAndRead('example.json', 'json', 'yaml')
        reference = readFile('example.yaml')
        # The date in 'example.json' is a string.
        reference_patched = reference.replace('1979-05-27 07:32:00+00:00',
                "'1979-05-27T07:32:00+00:00'")
        self.assertEqual(output, reference_patched)

    def test_toml2json(self):
        output = self.convertAndRead('example.toml', 'toml', 'json')
        reference = readFile('example.json')
        self.assertEqual(output, reference)

    def test_toml2yaml(self):
        output = self.convertAndRead('example.toml', 'toml', 'yaml')
        reference = readFile('example.yaml')
        self.assertEqual(output, reference)

    def test_yaml2json(self):
        output = self.convertAndRead('example.yaml', 'yaml', 'json')
        reference = readFile('example.json')
        self.assertEqual(output, reference)

    def test_yaml2toml(self):
        output = self.convertAndRead('example.yaml', 'yaml', 'toml')
        reference = readFile('example.toml')
        self.assertEqual(tomlSignature(output), tomlSignature(reference))

    def test_wrap(self):
        output = self.convertAndRead('array.json', 'json', 'toml', wrap='data')
        reference = readFile('array.toml')
        self.assertEqual(output, reference)

    def test_unwrap(self):
        output = self.convertAndRead('array.toml', 'toml', 'json',
                                    unwrap='data', indent_json=None)
        reference = readFile('array.json')
        self.assertEqual(output, reference)

if __name__ == '__main__':
    unittest.main()