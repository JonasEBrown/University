
# IMPORT MODULES #

import os
import sys
import unittest

from QRCode import QRCode

# RUNTIME #

if __name__ == "__main__":
    args = [arg if arg != "" else None for arg in sys.argv[1:]] + ([None] * 5)
    function = args.pop(0)
    function = input("> ") if function is None else function
    match function:
        case "create":
            assert args[0], "No data input."
            assert args[1] is None or args[1] in "LMQH", "Must enter a valid quality (L, M, Q, H)."
            QRCode(*args[:4])
        case "test":
            start_dir = (os.path.dirname(__file__) or '.') + "/tests"
            suite = unittest.defaultTestLoader.discover(start_dir, pattern="test_*.py")
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            raise SystemExit(0 if result.wasSuccessful() else 1)
        case "help":
            print("""
Usage: main.py <create|test>
    - create <data> <quality?> <file?> <showTags?> (Creates a QR code)
        - <data> (Required): the data to create the QR code.
        - <quality?> (Optional): the quality of the QR code (L, M, Q, H).
        - <file?> (Optional): the file to write the QR code to.
        - <showDebug?> (Optional): output the debug snapshots of the matrix?
    - test (Tests the modules)
            """)
        case _:
            raise RuntimeError("It's unclear what you want to do. Run the module with argument \"help\" for help.")