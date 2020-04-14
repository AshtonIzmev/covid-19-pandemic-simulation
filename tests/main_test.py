import unittest

from tests import helpers_test
from tests import initiator_test


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(helpers_test.TestHelpers))
    suite.addTests(loader.loadTestsFromTestCase(initiator_test.TestInitiation))
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
