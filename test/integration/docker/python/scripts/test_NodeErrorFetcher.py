import os
import unittest
from datetime import datetime
from shutil import rmtree

import pandas as pd
from common import ErrorCSVHandler, PropertiesReader
from node_to_csv import NodeErrorFetcher

from BrokerNodeDummy import BrokerNodeDummy, BrokerNodeError


class TestNodeErrorFetcher(unittest.TestCase):
    __DEFAULT_NODE_ID: str = '0'
    __DEFAULT_API_KEY: str = 'xxxApiKey123'
    __DIR_ROOT: str = None

    @classmethod
    def setUpClass(cls):
        PropertiesReader().load_properties_as_env_vars('settings.json')
        cls.__DIR_ROOT = os.environ['ROOT_DIR'] if os.environ['ROOT_DIR'] else os.getcwd()
        cls.__CSV_HANDLER = ErrorCSVHandler()
        name_csv = ErrorCSVHandler().generate_csv_name(cls.__DEFAULT_NODE_ID)
        cls.__DEFAULT_CSV_PATH = os.path.join(cls.__DIR_ROOT, cls.__DEFAULT_NODE_ID, name_csv)
        cls.__FETCHER = NodeErrorFetcher()
        cls.__DUMMY = BrokerNodeDummy(cls.__DEFAULT_API_KEY)

    def setUp(self):
        stats = self.__create_error1()
        self.__DUMMY.put_import_info_on_broker(stats)
        self.__FETCHER.fetch_broker_data_to_file(self.__DEFAULT_NODE_ID)

    def tearDown(self):
        [rmtree(name) for name in os.listdir(self.__DIR_ROOT) if os.path.isdir(name) and len(name) <= 2]

    def test_init_working_csv(self):
        self.__init_new_dummy_and_put_default_error_on_node(self.__DEFAULT_API_KEY)
        self.__init_new_dummy_and_put_default_error_on_node('xxxApiKey567')
        self.__make_new_fetching_and_check_csv_count(self.__DEFAULT_NODE_ID, 1)
        self.__make_new_fetching_and_check_csv_count(self.__DEFAULT_NODE_ID, 1)
        self.__make_new_fetching_and_check_csv_count('1', 2)

    def __init_new_dummy_and_put_default_error_on_node(self, api_key: str):
        stats = self.__create_error1()
        dummy = BrokerNodeDummy(api_key)
        dummy.put_import_info_on_broker(stats)

    def __make_new_fetching_and_check_csv_count(self, id_node: str, count: int):
        self.__FETCHER.fetch_broker_data_to_file(id_node)
        list_csv = self.__list_csv_in_working_directory()
        self.assertEqual(count, len(list_csv))

    def __list_csv_in_working_directory(self) -> list:
        list_csv = []
        for root, dirs, files in os.walk(self.__DIR_ROOT):
            for name in files:
                if name.endswith('.csv'):
                    list_csv.append(name)
        return list_csv

    def test_csv_columns(self):
        df = self.__CSV_HANDLER.read_csv_as_df(self.__DEFAULT_CSV_PATH)
        header = list(df.columns)
        expected_columns = ['timestamp', 'repeats', 'content']
        self.assertTrue(len(expected_columns), len(header))
        self.assertCountEqual(expected_columns, header)

    def test_fetch_default_error_to_csv(self):
        df = self.__CSV_HANDLER.read_csv_as_df(self.__DEFAULT_CSV_PATH)
        self.assertEqual(1, df.shape[0])
        ts_expected = ''.join([str(datetime.now().year), '-01-01 01:00:00'])
        self.__check_error_row_from_csv(df.iloc[0], ts_expected, '5', 'TestError')

    def test_update_error_in_csv(self):
        """
        Expected timestamp is a hour later because timezone of script is Europe/Berlin (summer time)
        """
        error = self.__create_error1_update()
        df = self.__put_import_error_on_broker_and_get_fetched_csv_as_df(error)
        self.assertEqual(1, df.shape[0])
        ts_expected = ''.join([str(datetime.now().year), '-10-10 01:00:00'])
        self.__check_error_row_from_csv(df.iloc[0], ts_expected, '10', 'TestError')

    def test_fetch_next_error_to_csv(self):
        error = self.__create_error2()
        df = self.__put_import_error_on_broker_and_get_fetched_csv_as_df(error)
        self.assertEqual(2, df.shape[0])
        ts_expected = ''.join([str(datetime.now().year), '-05-05 01:00:00'])
        self.__check_error_row_from_csv(df.iloc[0], ts_expected, '5', 'TestError2')
        ts_expected2 = ''.join([str(datetime.now().year), '-01-01 01:00:00'])
        self.__check_error_row_from_csv(df.iloc[1], ts_expected2, '5', 'TestError')

    def test_fetch_default_error_to_csv_with_missing_repeats(self):
        error = self.__create_error_without_repeats()
        df = self.__put_import_error_on_broker_and_get_fetched_csv_as_df(error)
        self.assertEqual(1, df.shape[0])
        ts_expected = ''.join([str(datetime.now().year), '-01-01 01:00:00'])
        self.__check_error_row_from_csv(df.iloc[0], ts_expected, '1', 'TestError')

    def test_fetch_identical_error_to_csv(self):
        error = self.__create_error1()
        df = self.__put_import_error_on_broker_and_get_fetched_csv_as_df(error)
        self.assertEqual(1, df.shape[0])
        ts_expected = ''.join([str(datetime.now().year), '-01-01 01:00:00'])
        self.__check_error_row_from_csv(df.iloc[0], ts_expected, '5', 'TestError')

    def test_fetch_error_from_last_year_to_csv(self):
        self.tearDown()
        error = self.__create_error_last_year()
        df = self.__put_import_error_on_broker_and_get_fetched_csv_as_df(error)
        self.assertEqual(0, df.shape[0])

    @staticmethod
    def __create_error1():
        ts_error = ''.join([str(datetime.now().year), '-01-01T01:00:00+01:00'])
        return BrokerNodeError(ts_error, '5', 'TestError')

    @staticmethod
    def __create_error1_update():
        ts_error = ''.join([str(datetime.now().year), '-10-10T01:00:00+01:00'])
        return BrokerNodeError(ts_error, '10', 'TestError')

    @staticmethod
    def __create_error2():
        ts_error = ''.join([str(datetime.now().year), '-05-05T01:00:00+01:00'])
        return BrokerNodeError(ts_error, '5', 'TestError2')

    @staticmethod
    def __create_error_last_year():
        ts_error = ''.join([str(datetime.now().year - 1), '-01-01T01:00:00+01:00'])
        return BrokerNodeError(ts_error, '1', 'TestError')

    @staticmethod
    def __create_error_without_repeats():
        ts_error = ''.join([str(datetime.now().year), '-01-01T01:00:00+01:00'])
        return BrokerNodeError(ts_error, '', 'TestError')

    def __check_error_row_from_csv(self, row: pd.Series, timestamp: str, repeats: str, content: str):
        self.assertEqual(timestamp, row['timestamp'])
        self.assertEqual(repeats, row['repeats'])
        self.assertEqual(content, row['content'])

    def __put_import_error_on_broker_and_get_fetched_csv_as_df(self, payload):
        self.__DUMMY.put_import_info_on_broker(payload)
        self.__FETCHER.fetch_broker_data_to_file(self.__DEFAULT_NODE_ID)
        return self.__CSV_HANDLER.read_csv_as_df(self.__DEFAULT_CSV_PATH)


if __name__ == '__main__':
    unittest.main()
