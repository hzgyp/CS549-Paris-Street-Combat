import unittest
from audit_recoil import validate_receipt


class ReceiptAudit(unittest.TestCase):
    def setUp(self):
        self.receipt = {"status": "pass_native", "errors": [], "protected_count": 703}
        self.log = {"strict_errors": 0, "exit_code": 0, "timed_out": False}

    def test_good(self):
        validate_receipt(self.receipt, self.log)

    def test_failed_status(self):
        self.receipt["status"] = "failed_native"
        with self.assertRaises(AssertionError): validate_receipt(self.receipt, self.log)

    def test_error_not_hidden_by_status(self):
        self.receipt["errors"].append("bad source")
        with self.assertRaises(AssertionError): validate_receipt(self.receipt, self.log)

    def test_crash_not_hidden_by_receipt(self):
        self.log["exit_code"] = 3
        with self.assertRaises(AssertionError): validate_receipt(self.receipt, self.log)

    def test_strict_log(self):
        self.log["strict_errors"] = 1
        with self.assertRaises(AssertionError): validate_receipt(self.receipt, self.log)

    def test_timeout(self):
        self.log["timed_out"] = True
        with self.assertRaises(AssertionError): validate_receipt(self.receipt, self.log)

    def test_epoch(self):
        self.receipt["protected_count"] = 678
        with self.assertRaises(AssertionError): validate_receipt(self.receipt, self.log)


if __name__ == "__main__": unittest.main()
