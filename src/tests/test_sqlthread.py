"""Tests for SQL thread"""
# flake8: noqa:E402
import os
import tempfile
import unittest

os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()

from pybitmessage.class_sqlThread import TestDB  # noqa:E402
from pybitmessage.addresses import encodeAddress  # noqa:E402


def filter_table_column(schema, column):
    """
        Filter column from schema
    """
    for x in schema:
        for y in x:
            if y == column:
                yield y


class TestSqlBase(object):  # pylint: disable=E1101, too-few-public-methods, E1004, W0232
    """ Base for test case """

    __name__ = None
    root_path = os.path.dirname(os.path.dirname(__file__))
    test_db = None

    def _setup_db(self):  # pylint: disable=W0622, redefined-builtin
        """
            Drop all tables before each test case start
        """
        self.test_db = TestDB()
        self.test_db.create_sql_function()
        self.test_db.initialize_schema()

    def get_table_schema(self, table_name):
        """Get table list of column names and value types by table name"""
        self.test_db.cur.execute("""PRAGMA table_info({})""".format(table_name))
        res = self.test_db.cur.fetchall()
        res = [[x[1], x[2]] for x in res]
        return res

    def initialise_database(self, test_db_cur, file):  # pylint: disable=W0622, redefined-builtin
        """
            Initialise DB
        """

        with open(os.path.join(self.root_path, "tests/sql/{}.sql".format(file)), 'r') as sql_as_string:
            sql_as_string = sql_as_string.read()

        test_db_cur.cur.executescript(sql_as_string)


class TestFnBitmessageDB(TestSqlBase, unittest.TestCase):  # pylint: disable=protected-access
    """ Test case for Sql function"""

    def setUp(self):
        """
            setup for test case
        """
        self._setup_db()

    def test_create_function(self):
        """Check the result of enaddr function"""
        st = "21122112211221122112".encode()
        encoded_str = encodeAddress(4, 1, st)

        item = '''SELECT enaddr(4, 1, ?);'''
        parameters = (st, )
        self.test_db.cur.execute(item, parameters)
        query = self.test_db.cur.fetchall()
        self.assertEqual(query[0][-1], encoded_str, "test case fail for create_function")


class TestInitializerBitmessageDB(TestSqlBase, unittest.TestCase):
    """Test case for SQL initializer"""

    def setUp(self):
        """
            Setup DB schema before start.
            And applying default schema for initializer test.
        """
        self._setup_db()

    def test_inbox_table_init(self):
        """
            Test inbox table
        """
        res = self.get_table_schema("inbox")
        check = [['msgid', 'blob'],
                 ['toaddress', 'text'],
                 ['fromaddress', 'text'],
                 ['subject', 'text'],
                 ['received', 'text'],
                 ['message', 'text'],
                 ['folder', 'text'],
                 ['encodingtype', 'int'],
                 ['read', 'bool'],
                 ['sighash', 'blob']]
        self.assertEqual(res, check, "inbox table not valid")

    def test_sent_table_init(self):
        """
            Test sent table
        """
        res = self.get_table_schema("sent")
        check = [['msgid', 'blob'],
                 ['toaddress', 'text'],
                 ['toripe', 'blob'],
                 ['fromaddress', 'text'],
                 ['subject', 'text'],
                 ['message', 'text'],
                 ['ackdata', 'blob'],
                 ['senttime', 'integer'],
                 ['lastactiontime', 'integer'],
                 ['sleeptill', 'integer'],
                 ['status', 'text'],
                 ['retrynumber', 'integer'],
                 ['folder', 'text'],
                 ['encodingtype', 'int'],
                 ['ttl', 'int']]
        self.assertEqual(res, check, "sent table not valid")

    def test_subscriptions_table_init(self):
        """
            Test subscriptions table
        """
        res = self.get_table_schema("subscriptions")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "subscriptions table not valid")

    def test_addressbook_table_init(self):
        """
            Test addressbook table
        """
        res = self.get_table_schema("addressbook")
        check = [['label', 'text'],
                 ['address', 'text']]
        self.assertEqual(res, check, "addressbook table not valid")

    def test_blacklist_table_init(self):
        """
            Test blacklist table
        """
        res = self.get_table_schema("blacklist")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "blacklist table not valid")

    def test_whitelist_table_init(self):
        """
            Test whitelist table
        """
        res = self.get_table_schema("whitelist")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "whitelist table not valid")

    def test_pubkeys_table_init(self):
        """
            Test pubkeys table
        """
        res = self.get_table_schema("pubkeys")
        check = [['address', 'text'],
                 ['addressversion', 'int'],
                 ['transmitdata', 'blob'],
                 ['time', 'int'],
                 ['usedpersonally', 'text']]
        self.assertEqual(res, check, "pubkeys table not valid")

    def test_inventory_table_init(self):
        """
            Test inventory table
        """
        res = self.get_table_schema("inventory")
        check = [['hash', 'blob'],
                 ['objecttype', 'int'],
                 ['streamnumber', 'int'],
                 ['payload', 'blob'],
                 ['expirestime', 'integer'],
                 ['tag', 'blob']]
        self.assertEqual(res, check, "inventory table not valid")

    def test_settings_table_init(self):
        """
            Test settings table
        """
        res = self.get_table_schema("settings")
        check = [['key', 'blob'],
                 ['value', 'blob']]
        self.assertEqual(res, check, "settings table not valid")

    def test_objectprocessorqueue_table_init(self):
        """
            Test objectprocessorqueue table
        """
        res = self.get_table_schema("objectprocessorqueue")
        check = [['objecttype', 'int'],
                 ['data', 'blob']]
        self.assertEqual(res, check, "objectprocessorqueue table not valid")


class TestUpgradeBitmessageDB(TestSqlBase, unittest.TestCase):  # pylint: disable=protected-access
    """Test case for SQL versions"""

    def setUp(self):
        """
            Setup DB schema before start.
            And applying default schema for version test.
        """
        self._setup_db()
        self.test_db.cur.execute('''INSERT INTO settings VALUES('version','2')''')

    def version(self):
        """
            Run SQL Scripts, Initialize DB with respect to versioning
            and Upgrade DB schema for all versions
        """
        def wrapper(*args):
            """
                Run SQL and mocking DB for versions
            """
            self = args[0]
            func_name = func.__name__
            version = func_name.rsplit('_', 1)[-1]
            self.test_db._upgrade_one_level_sql_statement(int(version))   # pylint: disable= W0212, protected-access

            # Update versions DB mocking
            self.initialise_database(self.test_db, "init_version_{}".format(version))

            return func(*args)  # <-- use (self, ...)
        func = self
        return wrapper

    @version
    def test_bm_db_version_2(self):
        """
            Test with version 2
        """
        res = self.test_db.cur.execute(''' SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='inventory_backup' ''')
        self.assertNotEqual(res, 1, "Table inventory_backup not deleted in versioning 2")

    @version
    def test_bm_db_version_3(self):
        """
            Test with version 1
            Version 1 and 3 are same so will skip 3
        """
        res = self.test_db.cur.execute('''PRAGMA table_info('inventory');''')
        result = list(filter_table_column(res, "tag"))
        self.assertEqual(result, ['tag'], "Data not migrated for version 3")

    @version
    def test_bm_db_version_4(self):
        """
            Test with version 4
        """
        self.test_db.cur.execute("select * from pubkeys where addressversion = '1';")
        res = self.test_db.cur.fetchall()
        self.assertEqual(len(res), 1, "Table inventory not deleted in versioning 4")

    @version
    def test_bm_db_version_5(self):
        """
            Test with version 5
        """
        self.test_db.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='knownnodes' ''')  # noqa
        res = self.test_db.cur.fetchall()
        self.assertNotEqual(res[0][0], 1, "Table knownnodes not deleted in versioning 5")
        self.test_db.cur.execute(''' SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='objectprocessorqueue'; ''')
        res = self.test_db.cur.fetchall()
        self.assertNotEqual(len(res), 0, "Table objectprocessorqueue not created in versioning 5")
        self.test_db.cur.execute(''' SELECT * FROM objectprocessorqueue where objecttype='hash' ; ''')
        res = self.test_db.cur.fetchall()
        self.assertNotEqual(len(res), 0, "Table objectprocessorqueue not created in versioning 5")

    @version
    def test_bm_db_version_6(self):
        """
            Test with version 6
        """
        self.test_db.cur.execute('''PRAGMA table_info('inventory');''')
        inventory = self.test_db.cur.fetchall()
        inventory = list(filter_table_column(inventory, "expirestime"))
        self.assertEqual(inventory, ['expirestime'], "Data not migrated for version 6")

        self.test_db.cur.execute('''PRAGMA table_info('objectprocessorqueue');''')
        objectprocessorqueue = self.test_db.cur.fetchall()
        objectprocessorqueue = list(filter_table_column(objectprocessorqueue, "objecttype"))
        self.assertEqual(objectprocessorqueue, ['objecttype'], "Data not migrated for version 6")

    @version
    def test_bm_db_version_7(self):
        """
            Test with version 7
        """
        self.test_db.cur.execute('''SELECT * FROM pubkeys ''')
        pubkeys = self.test_db.cur.fetchall()
        self.assertEqual(pubkeys, [], "Data not migrated for version 7")

        self.test_db.cur.execute('''SELECT * FROM inventory ''')
        inventory = self.test_db.cur.fetchall()
        self.assertEqual(inventory, [], "Data not migrated for version 7")

        self.test_db.cur.execute('''SELECT status FROM sent ''')
        sent = self.test_db.cur.fetchall()
        self.assertEqual(sent, [('msgqueued',), ('msgqueued',)], "Data not migrated for version 7")

    @version
    def test_bm_db_version_8(self):
        """
            Test with version 8
        """
        self.test_db.cur.execute('''PRAGMA table_info('inbox');''')
        res = self.test_db.cur.fetchall()
        result = list(filter_table_column(res, "sighash"))
        self.assertEqual(result, ['sighash'], "Data not migrated for version 8")

    @version
    def test_bm_db_version_9(self):
        """
            Test with version 9
        """
        self.test_db.cur.execute("SELECT count(name) FROM  sqlite_master WHERE type='table' AND name='pubkeys_backup'")  # noqa
        res = self.test_db.cur.fetchall()
        self.assertNotEqual(res[0][0], 1, "Table pubkeys_backup not deleted")

    @version
    def test_bm_db_version_10(self):
        """
            Test with version 10
        """
        label = "test"
        self.test_db.cur.execute("SELECT * FROM addressbook WHERE label='test' ")  # noqa
        res = self.test_db.cur.fetchall()
        self.assertEqual(res[0][0], label, "Data not migrated for version 10")

    def test_bm_db_version_type(self):
        """
            Test version type
        """
        self.test_db.cur.execute('''INSERT INTO settings VALUES('version','test_string')''')  # noqa
        res = self.test_db.sql_schema_version
        self.assertEqual(type(res), int)
