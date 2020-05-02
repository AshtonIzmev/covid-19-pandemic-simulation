import unittest

from tests.helper import helpers_test
from tests.simulator import simulator_test, store_propagation_test, day_incrementation_test, house_propagation_test, \
    transport_propagation_test, workplace_propagation_test, environment_test
from tests.scenario import examples_test

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(helpers_test.TestHelpers))
    suite.addTests(loader.loadTestsFromTestCase(environment_test.TestInitiation))
    suite.addTests(loader.loadTestsFromTestCase(simulator_test.TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(house_propagation_test.TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(transport_propagation_test.TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(workplace_propagation_test.TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(store_propagation_test.TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(day_incrementation_test.TestSimulation))
    suite.addTests(loader.loadTestsFromTestCase(examples_test.TestScenarios))
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
