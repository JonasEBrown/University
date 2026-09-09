import os
import unittest
from QRCode import QRCode

folder = os.path.dirname(__file__)

class TestQRCode(unittest.TestCase):
    def test_toBinary_padding(self):
        self.assertEqual(QRCode.toBinary(5, 8), "00000101")
        self.assertEqual(QRCode.toBinary(255, 8), "11111111")

    def test_mode_detection(self):
        # Numeric
        qr = QRCode("12345", error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/test_numeric.svg")
        self.assertEqual(qr.mode, QRCode.MODES.NUMERIC)
        # Alphanumeric
        qr2 = QRCode("AB-01", error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/test_alpha.svg")
        self.assertEqual(qr2.mode, QRCode.MODES.ALPHANUMERIC)
        # Byte
        qr3 = QRCode("hello_", error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/test_byte.svg")
        self.assertEqual(qr3.mode, QRCode.MODES.BYTE)

    def test_version_determination_small(self):
        qr = QRCode("HELLO WORLD", error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/v.svg")
        self.assertTrue(1 <= qr.version <= 40)
        self.assertIsInstance(qr.alignment_positions, list)

    def test_bit_string_and_codewords_lengths(self):
        qr = QRCode("HELLO", error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/len.svg")
        # required bit count is total_codewords * 8
        self.assertEqual(qr.required_bit_count, qr.required_codewords * 8)
        # codewords derived from bit_string should match required_codewords
        self.assertEqual(len(qr.codewords), qr.required_codewords)

    def test_format_string_generation_length(self):
        qr = QRCode("HELLO", error_correction=QRCode.ERROR_CORRECTIONS.L, file=f"{folder}/fmt.svg")
        s = qr._generate_format_string()
        self.assertEqual(len(s), 15)

    def test_version_string_length_for_v7_plus(self):
        # Force data big enough to push version >=7
        qr = QRCode('A' * 400, error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/v7.svg")
        if qr.version >= 7:
            s = qr._generate_version_string()
            self.assertEqual(len(s), 18)

    def test_mask_patterns_score_and_selection(self):
        qr = QRCode("HELLO WORLD", error_correction=QRCode.ERROR_CORRECTIONS.M, file=f"{folder}/mask.svg")
        # mask value chosen must be between 0 and 7
        self.assertIn(qr.mask, list(range(8)))
        # qr_matrix must be square of expected size
        self.assertEqual(len(qr.qr_matrix), qr.qr_size)
        self.assertTrue(all(len(row) == qr.qr_size for row in qr.qr_matrix))

    def test_export_svg_creates_file(self):
        fname = f"{folder}/out.svg"
        qr = QRCode("HELLO", error_correction=QRCode.ERROR_CORRECTIONS.M, file=fname)
        self.assertTrue(os.path.exists(fname))
        # basic sanity: file is not empty
        self.assertGreater(os.path.getsize(fname), 0)

    @classmethod
    def tearDownClass(cls):
        for filename in os.listdir(folder):
            if filename.endswith(".svg") and os.path.isfile(os.path.join(folder, filename)):
                with open(f"{folder}\\{filename}", "r") as test, open(f"{folder}\\qrs\\{filename}", "r") as correct:
                    assert (test.read() == correct.read()), f"{filename} not equal to correct qr!"
                os.remove(f"{folder}\\{filename}")

if __name__ == "__main__":
    unittest.main()
