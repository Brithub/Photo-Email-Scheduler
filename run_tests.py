import unittest
from test_time_helper import TestTimeHelper
from test_response_api import TestResponseApi
from test_email_sender import TestEmailSender

if __name__ == '__main__':
    # Create a test suite with all test cases
    test_suite = unittest.TestSuite()

    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestTimeHelper))
    test_suite.addTest(unittest.makeSuite(TestResponseApi))
    test_suite.addTest(unittest.makeSuite(TestEmailSender))

    # Run the tests
    unittest.TextTestRunner(verbosity=2).run(test_suite)