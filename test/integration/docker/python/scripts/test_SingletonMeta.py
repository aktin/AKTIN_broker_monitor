import unittest

from common import load_properties_file_as_environment
from common import InfoCSVHandler
from common import ErrorCSVHandler
from common import BrokerNodeConnection
from common import ConfluenceConnection
from common import ConfluenceNodeMapper


class TestSingletonMeta(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_properties_file_as_environment('settings.json')

    def test_BrokerNodeConnection(self):
        connection1 = BrokerNodeConnection()
        connection2 = BrokerNodeConnection()
        self.assertEqual(id(connection1), id(connection2))

    def test_ConfluenceConnection(self):
        connection1 = ConfluenceConnection()
        connection2 = ConfluenceConnection()
        self.assertEqual(id(connection1), id(connection2))

    def test_ConfluenceNodeMapper(self):
        mapper1 = ConfluenceNodeMapper()
        mapper2 = ConfluenceNodeMapper()
        self.assertEqual(id(mapper1), id(mapper2))