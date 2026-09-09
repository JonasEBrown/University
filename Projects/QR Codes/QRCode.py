# IMPORTS #

from __future__ import annotations
from typing import Any, List, Dict, Tuple, Union, TypeVar, Callable

import math
import copy
from enum import Enum
import itertools

from Polynomial import Polynomial
from GaloisField import GaloisField

# TYPES #

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

type MaskFunction = Callable[[int, int, int], int]
type Matrix[T] = List[List[T]]
type TagMatrix[T: Enum] = Matrix[T]
type TupleDict[K,V] = Dict[Tuple[K, ...], V]
type Codewords = List[int]
type CodewordGroups = Matrix[Codewords]

# QR CODE CLASS #

class QRCode:
    """
        This class contains constants and enumerations used in QR code generation and decoding.

        Attributes:
            ALPHANUMERIC_CHARACTERS (List[str]): List of characters supported in alphanumeric mode.
            CORRESPONDING_ERROR_MARGINS (List[float]): List of error correction margins corresponding to error correction levels.
            ALIGNMENT_POSITIONS (Matrix[int]): List of alignment pattern positions for different QR code versions.
            CAPACITIES (TupleDict[int, int]): Dictionary mapping (version, error correction level, mode) to maximum data capacity.
            TOTAL_CODEWORDS (TupleDict[int, int]): Dictionary mapping (version, error_correction_level) to total codewords.
            CODEWORD_BLOCK_GROUP_DISTRIBUTIONS (TupleDict[int, List[int]): Dictionary mapping (version, error_correction_level) to codeword group distributions.
            ERROR_CORRECTION_CODEWORDS (TupleDict[int, int]): Dictionary mapping (version, error_correction_level) to total error correction codewords.
            CHARACTER_COUNT_INDICATORS (List[Tuple[int, int, List[int]]]): Character count indicator bit lengths for each mode and version range.
            REMAINDER_BITS (List[int]): Remainder bit lengths for each mode and version range.
            FINDER_PATTERN (Matrix[int]): The binary for a finder pattern.
            ALIGNMENT_PATTERN (Matrix[int]): The binary for an alignment pattern.
            MASK_PATTERNS (List[MaskFunction]): All the masking functions for QR codes.
            TAG_COLOUR_CODES (List[str]): List of colour codes (HTML/SVG) for QR code versions.

            QRCode.MODES (MODES): Enumeration for different encoding modes in QR codes.
            QRCode.ERROR_CORRECTIONS (ERROR_CORRECTIONS): Enumeration for different error correction levels in QR codes.
            QRCode.TAGS (TAGS): Enumeration for different tags in QR codes.
    """

    class MODES(Enum):
        """
            Enumeration for different encoding modes in QR codes.

            Enums:
                NUMERIC (int): Numeric mode.
                ALPHANUMERIC (int): Alphanumeric mode.
                BYTE (int): Byte mode.
                KANJI (int): Kanji mode.
        """
        NUMERIC = 0b0001
        ALPHANUMERIC = 0b0010
        BYTE = 0b0100
        KANJI = 0b1000

    class ERROR_CORRECTIONS(Enum):
        """
            Enumeration for different error correction levels in QR codes.

            Enums:
                L (int): Low error correction level.
                M (int): Medium error correction level.
                Q (int): Quartile error correction level.
                H (int): High error correction level.
        """
        L = 0b01
        M = 0b00
        Q = 0b11
        H = 0b10

    class TAGS(Enum):
        """
            Enumeration for different tags used in QR code matrix.

            Enums:
                UNASSIGNED (int): Tag for unassigned modules.
                DATASET (int): Tag for dataset modules.
                FINDER_PATTERN (int): Tag for finder patterns.
                ALIGNMENT_PATTERN (int): Tag for alignment patterns.
                TIMING_PATTERN (int): Tag for timing patterns.
                DARK_MODULE (int): Tag for the dark module.
                RESERVED (int): Tag for reserved areas.
        """
        UNASSIGNED = -1
        DATA = 0
        FINDER_PATTERN = 1
        ALIGNMENT_PATTERN = 1
        TIMING_PATTERN = 1
        DARK_MODULE = 1
        FORMAT_INFO = 2
        VERSION_INFO = 2
        RESERVED = 2

    # Alphanumeric characters supported in QR codes.
    ALPHANUMERIC_CHARACTERS: List[str] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", " ", "$", "%", "*", "+", "-", ".", "/", ":",]
    # Error correction margins corresponding to error correction levels L, M, Q, H.
    CORRESPONDING_ERROR_MARGINS: List[float] = [0.07, 0.15, 0.25, 0.3]
    # Alignment pattern positions for different QR code versions.
    ALIGNMENT_POSITIONS: Matrix[int] = [
        [],
        [],
        [6, 18],
        [6, 22],
        [6, 26],
        [6, 30],
        [6, 34],
        [6, 22, 38],
        [6, 24, 42],
        [6, 26, 46],
        [6, 28, 50],
        [6, 30, 54],
        [6, 32, 58],
        [6, 34, 62],
        [6, 26, 46, 66],
        [6, 26, 48, 70],
        [6, 26, 50, 74],
        [6, 30, 54, 78],
        [6, 30, 56, 82],
        [6, 30, 58, 86],
        [6, 34, 62, 90],
        [6, 28, 50, 72, 94],
        [6, 26, 50, 74, 98],
        [6, 30, 54, 78, 102],
        [6, 28, 54, 80, 106],
        [6, 32, 58, 84, 110],
        [6, 30, 58, 86, 114],
        [6, 34, 62, 90, 118],
        [6, 26, 50, 74, 98, 122],
        [6, 30, 54, 78, 102, 126],
        [6, 26, 52, 78, 104, 130],
        [6, 30, 56, 82, 108, 134],
        [6, 34, 60, 86, 112, 138],
        [6, 30, 58, 86, 114, 142],
        [6, 34, 62, 90, 118, 146],
        [6, 30, 54, 78, 102, 126, 150],
        [6, 24, 50, 76, 102, 128, 154],
        [6, 28, 54, 80, 106, 132, 158],
        [6, 32, 58, 84, 110, 136, 162],
        [6, 26, 54, 82, 110, 138, 166],
        [6, 30, 58, 86, 114, 142, 170],
    ]
    # Maximum data capacities for different versions, error correction levels, and modes.
    CAPACITIES: TupleDict[int, int] = {(1, 1, 1): 41, (1, 1, 2): 25, (1, 1, 4): 17, (1, 1, 8): 10, (1, 0, 1): 34, (1, 0, 2): 20,
                  (1, 0, 4): 14, (1, 0, 8): 8, (1, 3, 1): 27, (1, 3, 2): 16, (1, 3, 4): 11, (1, 3, 8): 7, (1, 2, 1): 17,
                  (1, 2, 2): 10, (1, 2, 4): 7, (1, 2, 8): 4, (2, 1, 1): 77, (2, 1, 2): 47, (2, 1, 4): 32, (2, 1, 8): 20,
                  (2, 0, 1): 63, (2, 0, 2): 38, (2, 0, 4): 26, (2, 0, 8): 16, (2, 3, 1): 48, (2, 3, 2): 29,
                  (2, 3, 4): 20, (2, 3, 8): 12, (2, 2, 1): 34, (2, 2, 2): 20, (2, 2, 4): 14, (2, 2, 8): 8,
                  (3, 1, 1): 127, (3, 1, 2): 77, (3, 1, 4): 53, (3, 1, 8): 32, (3, 0, 1): 101, (3, 0, 2): 61,
                  (3, 0, 4): 42, (3, 0, 8): 26, (3, 3, 1): 77, (3, 3, 2): 47, (3, 3, 4): 32, (3, 3, 8): 20,
                  (3, 2, 1): 58, (3, 2, 2): 35, (3, 2, 4): 24, (3, 2, 8): 15, (4, 1, 1): 187, (4, 1, 2): 114,
                  (4, 1, 4): 78, (4, 1, 8): 48, (4, 0, 1): 149, (4, 0, 2): 90, (4, 0, 4): 62, (4, 0, 8): 38,
                  (4, 3, 1): 111, (4, 3, 2): 67, (4, 3, 4): 46, (4, 3, 8): 28, (4, 2, 1): 82, (4, 2, 2): 50,
                  (4, 2, 4): 34, (4, 2, 8): 21, (5, 1, 1): 255, (5, 1, 2): 154, (5, 1, 4): 106, (5, 1, 8): 65,
                  (5, 0, 1): 202, (5, 0, 2): 122, (5, 0, 4): 84, (5, 0, 8): 52, (5, 3, 1): 144, (5, 3, 2): 87,
                  (5, 3, 4): 60, (5, 3, 8): 37, (5, 2, 1): 106, (5, 2, 2): 64, (5, 2, 4): 44, (5, 2, 8): 27,
                  (6, 1, 1): 322, (6, 1, 2): 195, (6, 1, 4): 134, (6, 1, 8): 82, (6, 0, 1): 255, (6, 0, 2): 154,
                  (6, 0, 4): 106, (6, 0, 8): 65, (6, 3, 1): 178, (6, 3, 2): 108, (6, 3, 4): 74, (6, 3, 8): 45,
                  (6, 2, 1): 139, (6, 2, 2): 84, (6, 2, 4): 58, (6, 2, 8): 36, (7, 1, 1): 370, (7, 1, 2): 224,
                  (7, 1, 4): 154, (7, 1, 8): 95, (7, 0, 1): 293, (7, 0, 2): 178, (7, 0, 4): 122, (7, 0, 8): 75,
                  (7, 3, 1): 207, (7, 3, 2): 125, (7, 3, 4): 86, (7, 3, 8): 53, (7, 2, 1): 154, (7, 2, 2): 93,
                  (7, 2, 4): 64, (7, 2, 8): 39, (8, 1, 1): 461, (8, 1, 2): 279, (8, 1, 4): 192, (8, 1, 8): 118,
                  (8, 0, 1): 365, (8, 0, 2): 221, (8, 0, 4): 152, (8, 0, 8): 93, (8, 3, 1): 259, (8, 3, 2): 157,
                  (8, 3, 4): 108, (8, 3, 8): 66, (8, 2, 1): 202, (8, 2, 2): 122, (8, 2, 4): 84, (8, 2, 8): 52,
                  (9, 1, 1): 552, (9, 1, 2): 335, (9, 1, 4): 230, (9, 1, 8): 141, (9, 0, 1): 432, (9, 0, 2): 262,
                  (9, 0, 4): 180, (9, 0, 8): 111, (9, 3, 1): 312, (9, 3, 2): 189, (9, 3, 4): 130, (9, 3, 8): 80,
                  (9, 2, 1): 235, (9, 2, 2): 143, (9, 2, 4): 98, (9, 2, 8): 60, (10, 1, 1): 652, (10, 1, 2): 395,
                  (10, 1, 4): 271, (10, 1, 8): 167, (10, 0, 1): 513, (10, 0, 2): 311, (10, 0, 4): 213, (10, 0, 8): 131,
                  (10, 3, 1): 364, (10, 3, 2): 221, (10, 3, 4): 151, (10, 3, 8): 93, (10, 2, 1): 288, (10, 2, 2): 174,
                  (10, 2, 4): 119, (10, 2, 8): 74, (11, 1, 1): 772, (11, 1, 2): 468, (11, 1, 4): 321, (11, 1, 8): 198,
                  (11, 0, 1): 604, (11, 0, 2): 366, (11, 0, 4): 251, (11, 0, 8): 155, (11, 3, 1): 427, (11, 3, 2): 259,
                  (11, 3, 4): 177, (11, 3, 8): 109, (11, 2, 1): 331, (11, 2, 2): 200, (11, 2, 4): 137, (11, 2, 8): 85,
                  (12, 1, 1): 883, (12, 1, 2): 535, (12, 1, 4): 367, (12, 1, 8): 226, (12, 0, 1): 691, (12, 0, 2): 419,
                  (12, 0, 4): 287, (12, 0, 8): 177, (12, 3, 1): 489, (12, 3, 2): 296, (12, 3, 4): 203, (12, 3, 8): 125,
                  (12, 2, 1): 374, (12, 2, 2): 227, (12, 2, 4): 155, (12, 2, 8): 96, (13, 1, 1): 1022, (13, 1, 2): 619,
                  (13, 1, 4): 425, (13, 1, 8): 262, (13, 0, 1): 796, (13, 0, 2): 483, (13, 0, 4): 331, (13, 0, 8): 204,
                  (13, 3, 1): 580, (13, 3, 2): 352, (13, 3, 4): 241, (13, 3, 8): 149, (13, 2, 1): 427, (13, 2, 2): 259,
                  (13, 2, 4): 177, (13, 2, 8): 109, (14, 1, 1): 1101, (14, 1, 2): 667, (14, 1, 4): 458, (14, 1, 8): 282,
                  (14, 0, 1): 871, (14, 0, 2): 528, (14, 0, 4): 362, (14, 0, 8): 223, (14, 3, 1): 621, (14, 3, 2): 376,
                  (14, 3, 4): 258, (14, 3, 8): 159, (14, 2, 1): 468, (14, 2, 2): 283, (14, 2, 4): 194, (14, 2, 8): 120,
                  (15, 1, 1): 1250, (15, 1, 2): 758, (15, 1, 4): 520, (15, 1, 8): 320, (15, 0, 1): 991, (15, 0, 2): 600,
                  (15, 0, 4): 412, (15, 0, 8): 254, (15, 3, 1): 703, (15, 3, 2): 426, (15, 3, 4): 292, (15, 3, 8): 180,
                  (15, 2, 1): 530, (15, 2, 2): 321, (15, 2, 4): 220, (15, 2, 8): 136, (16, 1, 1): 1408, (16, 1, 2): 854,
                  (16, 1, 4): 586, (16, 1, 8): 361, (16, 0, 1): 1082, (16, 0, 2): 656, (16, 0, 4): 450, (16, 0, 8): 277,
                  (16, 3, 1): 775, (16, 3, 2): 470, (16, 3, 4): 322, (16, 3, 8): 198, (16, 2, 1): 602, (16, 2, 2): 365,
                  (16, 2, 4): 250, (16, 2, 8): 154, (17, 1, 1): 1548, (17, 1, 2): 938, (17, 1, 4): 644, (17, 1, 8): 397,
                  (17, 0, 1): 1212, (17, 0, 2): 734, (17, 0, 4): 504, (17, 0, 8): 310, (17, 3, 1): 876, (17, 3, 2): 531,
                  (17, 3, 4): 364, (17, 3, 8): 224, (17, 2, 1): 674, (17, 2, 2): 408, (17, 2, 4): 280, (17, 2, 8): 173,
                  (18, 1, 1): 1725, (18, 1, 2): 1046, (18, 1, 4): 718, (18, 1, 8): 442, (18, 0, 1): 1346,
                  (18, 0, 2): 816, (18, 0, 4): 560, (18, 0, 8): 345, (18, 3, 1): 948, (18, 3, 2): 574, (18, 3, 4): 394,
                  (18, 3, 8): 243, (18, 2, 1): 746, (18, 2, 2): 452, (18, 2, 4): 310, (18, 2, 8): 191, (19, 1, 1): 1903,
                  (19, 1, 2): 1153, (19, 1, 4): 792, (19, 1, 8): 488, (19, 0, 1): 1500, (19, 0, 2): 909,
                  (19, 0, 4): 624, (19, 0, 8): 384, (19, 3, 1): 1063, (19, 3, 2): 644, (19, 3, 4): 442, (19, 3, 8): 272,
                  (19, 2, 1): 813, (19, 2, 2): 493, (19, 2, 4): 338, (19, 2, 8): 208, (20, 1, 1): 2061,
                  (20, 1, 2): 1249, (20, 1, 4): 858, (20, 1, 8): 528, (20, 0, 1): 1600, (20, 0, 2): 970,
                  (20, 0, 4): 666, (20, 0, 8): 410, (20, 3, 1): 1159, (20, 3, 2): 702, (20, 3, 4): 482, (20, 3, 8): 297,
                  (20, 2, 1): 919, (20, 2, 2): 557, (20, 2, 4): 382, (20, 2, 8): 235, (21, 1, 1): 2232,
                  (21, 1, 2): 1352, (21, 1, 4): 929, (21, 1, 8): 572, (21, 0, 1): 1708, (21, 0, 2): 1035,
                  (21, 0, 4): 711, (21, 0, 8): 438, (21, 3, 1): 1224, (21, 3, 2): 742, (21, 3, 4): 509, (21, 3, 8): 314,
                  (21, 2, 1): 969, (21, 2, 2): 587, (21, 2, 4): 403, (21, 2, 8): 248, (22, 1, 1): 2409,
                  (22, 1, 2): 1460, (22, 1, 4): 1003, (22, 1, 8): 618, (22, 0, 1): 1872, (22, 0, 2): 1134,
                  (22, 0, 4): 779, (22, 0, 8): 480, (22, 3, 1): 1358, (22, 3, 2): 823, (22, 3, 4): 565, (22, 3, 8): 348,
                  (22, 2, 1): 1056, (22, 2, 2): 640, (22, 2, 4): 439, (22, 2, 8): 270, (23, 1, 1): 2620,
                  (23, 1, 2): 1588, (23, 1, 4): 1091, (23, 1, 8): 672, (23, 0, 1): 2059, (23, 0, 2): 1248,
                  (23, 0, 4): 857, (23, 0, 8): 528, (23, 3, 1): 1468, (23, 3, 2): 890, (23, 3, 4): 611, (23, 3, 8): 376,
                  (23, 2, 1): 1108, (23, 2, 2): 672, (23, 2, 4): 461, (23, 2, 8): 284, (24, 1, 1): 2812,
                  (24, 1, 2): 1704, (24, 1, 4): 1171, (24, 1, 8): 721, (24, 0, 1): 2188, (24, 0, 2): 1326,
                  (24, 0, 4): 911, (24, 0, 8): 561, (24, 3, 1): 1588, (24, 3, 2): 963, (24, 3, 4): 661, (24, 3, 8): 407,
                  (24, 2, 1): 1228, (24, 2, 2): 744, (24, 2, 4): 511, (24, 2, 8): 315, (25, 1, 1): 3057,
                  (25, 1, 2): 1853, (25, 1, 4): 1273, (25, 1, 8): 784, (25, 0, 1): 2395, (25, 0, 2): 1451,
                  (25, 0, 4): 997, (25, 0, 8): 614, (25, 3, 1): 1718, (25, 3, 2): 1041, (25, 3, 4): 715,
                  (25, 3, 8): 440, (25, 2, 1): 1286, (25, 2, 2): 779, (25, 2, 4): 535, (25, 2, 8): 330,
                  (26, 1, 1): 3283, (26, 1, 2): 1990, (26, 1, 4): 1367, (26, 1, 8): 842, (26, 0, 1): 2544,
                  (26, 0, 2): 1542, (26, 0, 4): 1059, (26, 0, 8): 652, (26, 3, 1): 1804, (26, 3, 2): 1094,
                  (26, 3, 4): 751, (26, 3, 8): 462, (26, 2, 1): 1425, (26, 2, 2): 864, (26, 2, 4): 593, (26, 2, 8): 365,
                  (27, 1, 1): 3517, (27, 1, 2): 2132, (27, 1, 4): 1465, (27, 1, 8): 902, (27, 0, 1): 2701,
                  (27, 0, 2): 1637, (27, 0, 4): 1125, (27, 0, 8): 692, (27, 3, 1): 1933, (27, 3, 2): 1172,
                  (27, 3, 4): 805, (27, 3, 8): 496, (27, 2, 1): 1501, (27, 2, 2): 910, (27, 2, 4): 625, (27, 2, 8): 385,
                  (28, 1, 1): 3669, (28, 1, 2): 2223, (28, 1, 4): 1528, (28, 1, 8): 940, (28, 0, 1): 2857,
                  (28, 0, 2): 1732, (28, 0, 4): 1190, (28, 0, 8): 732, (28, 3, 1): 2085, (28, 3, 2): 1263,
                  (28, 3, 4): 868, (28, 3, 8): 534, (28, 2, 1): 1581, (28, 2, 2): 958, (28, 2, 4): 658, (28, 2, 8): 405,
                  (29, 1, 1): 3909, (29, 1, 2): 2369, (29, 1, 4): 1628, (29, 1, 8): 1002, (29, 0, 1): 3035,
                  (29, 0, 2): 1839, (29, 0, 4): 1264, (29, 0, 8): 778, (29, 3, 1): 2181, (29, 3, 2): 1322,
                  (29, 3, 4): 908, (29, 3, 8): 559, (29, 2, 1): 1677, (29, 2, 2): 1016, (29, 2, 4): 698,
                  (29, 2, 8): 430, (30, 1, 1): 4158, (30, 1, 2): 2520, (30, 1, 4): 1732, (30, 1, 8): 1066,
                  (30, 0, 1): 3289, (30, 0, 2): 1994, (30, 0, 4): 1370, (30, 0, 8): 843, (30, 3, 1): 2358,
                  (30, 3, 2): 1429, (30, 3, 4): 982, (30, 3, 8): 604, (30, 2, 1): 1782, (30, 2, 2): 1080,
                  (30, 2, 4): 742, (30, 2, 8): 457, (31, 1, 1): 4417, (31, 1, 2): 2677, (31, 1, 4): 1840,
                  (31, 1, 8): 1132, (31, 0, 1): 3486, (31, 0, 2): 2113, (31, 0, 4): 1452, (31, 0, 8): 894,
                  (31, 3, 1): 2473, (31, 3, 2): 1499, (31, 3, 4): 1030, (31, 3, 8): 634, (31, 2, 1): 1897,
                  (31, 2, 2): 1150, (31, 2, 4): 790, (31, 2, 8): 486, (32, 1, 1): 4686, (32, 1, 2): 2840,
                  (32, 1, 4): 1952, (32, 1, 8): 1201, (32, 0, 1): 3693, (32, 0, 2): 2238, (32, 0, 4): 1538,
                  (32, 0, 8): 947, (32, 3, 1): 2670, (32, 3, 2): 1618, (32, 3, 4): 1112, (32, 3, 8): 684,
                  (32, 2, 1): 2022, (32, 2, 2): 1226, (32, 2, 4): 842, (32, 2, 8): 518, (33, 1, 1): 4965,
                  (33, 1, 2): 3009, (33, 1, 4): 2068, (33, 1, 8): 1273, (33, 0, 1): 3909, (33, 0, 2): 2369,
                  (33, 0, 4): 1628, (33, 0, 8): 1002, (33, 3, 1): 2805, (33, 3, 2): 1700, (33, 3, 4): 1168,
                  (33, 3, 8): 719, (33, 2, 1): 2157, (33, 2, 2): 1307, (33, 2, 4): 898, (33, 2, 8): 553,
                  (34, 1, 1): 5253, (34, 1, 2): 3183, (34, 1, 4): 2188, (34, 1, 8): 1347, (34, 0, 1): 4134,
                  (34, 0, 2): 2506, (34, 0, 4): 1722, (34, 0, 8): 1060, (34, 3, 1): 2949, (34, 3, 2): 1787,
                  (34, 3, 4): 1228, (34, 3, 8): 756, (34, 2, 1): 2301, (34, 2, 2): 1394, (34, 2, 4): 958,
                  (34, 2, 8): 590, (35, 1, 1): 5529, (35, 1, 2): 3351, (35, 1, 4): 2303, (35, 1, 8): 1417,
                  (35, 0, 1): 4343, (35, 0, 2): 2632, (35, 0, 4): 1809, (35, 0, 8): 1113, (35, 3, 1): 3081,
                  (35, 3, 2): 1867, (35, 3, 4): 1283, (35, 3, 8): 790, (35, 2, 1): 2361, (35, 2, 2): 1431,
                  (35, 2, 4): 983, (35, 2, 8): 605, (36, 1, 1): 5836, (36, 1, 2): 3537, (36, 1, 4): 2431,
                  (36, 1, 8): 1496, (36, 0, 1): 4588, (36, 0, 2): 2780, (36, 0, 4): 1911, (36, 0, 8): 1176,
                  (36, 3, 1): 3244, (36, 3, 2): 1966, (36, 3, 4): 1351, (36, 3, 8): 832, (36, 2, 1): 2524,
                  (36, 2, 2): 1530, (36, 2, 4): 1051, (36, 2, 8): 647, (37, 1, 1): 6153, (37, 1, 2): 3729,
                  (37, 1, 4): 2563, (37, 1, 8): 1577, (37, 0, 1): 4775, (37, 0, 2): 2894, (37, 0, 4): 1989,
                  (37, 0, 8): 1224, (37, 3, 1): 3417, (37, 3, 2): 2071, (37, 3, 4): 1423, (37, 3, 8): 876,
                  (37, 2, 1): 2625, (37, 2, 2): 1591, (37, 2, 4): 1093, (37, 2, 8): 673, (38, 1, 1): 6479,
                  (38, 1, 2): 3927, (38, 1, 4): 2699, (38, 1, 8): 1661, (38, 0, 1): 5039, (38, 0, 2): 3054,
                  (38, 0, 4): 2099, (38, 0, 8): 1292, (38, 3, 1): 3599, (38, 3, 2): 2181, (38, 3, 4): 1499,
                  (38, 3, 8): 923, (38, 2, 1): 2735, (38, 2, 2): 1658, (38, 2, 4): 1139, (38, 2, 8): 701,
                  (39, 1, 1): 6743, (39, 1, 2): 4087, (39, 1, 4): 2809, (39, 1, 8): 1729, (39, 0, 1): 5313,
                  (39, 0, 2): 3220, (39, 0, 4): 2213, (39, 0, 8): 1362, (39, 3, 1): 3791, (39, 3, 2): 2298,
                  (39, 3, 4): 1579, (39, 3, 8): 972, (39, 2, 1): 2927, (39, 2, 2): 1774, (39, 2, 4): 1219,
                  (39, 2, 8): 750, (40, 1, 1): 7089, (40, 1, 2): 4296, (40, 1, 4): 2953, (40, 1, 8): 1817,
                  (40, 0, 1): 5596, (40, 0, 2): 3391, (40, 0, 4): 2331, (40, 0, 8): 1435, (40, 3, 1): 3993,
                  (40, 3, 2): 2420, (40, 3, 4): 1663, (40, 3, 8): 1024, (40, 2, 1): 3057, (40, 2, 2): 1852,
                  (40, 2, 4): 1273, (40, 2, 8): 784}
    # Total number of codewords for each (version, error_correction_level).
    TOTAL_CODEWORDS: TupleDict[int, int] = {(1, 1): 19, (1, 0): 16, (1, 3): 13, (1, 2): 9, (2, 1): 34, (2, 0): 28, (2, 3): 22, (2, 2): 16,
                       (3, 1): 55, (3, 0): 44, (3, 3): 34, (3, 2): 26, (4, 1): 80, (4, 0): 64, (4, 3): 48, (4, 2): 36,
                       (5, 1): 108, (5, 0): 86, (5, 3): 62, (5, 2): 46, (6, 1): 136, (6, 0): 108, (6, 3): 76,
                       (6, 2): 60,
                       (7, 1): 156, (7, 0): 124, (7, 3): 88, (7, 2): 66, (8, 1): 194, (8, 0): 154, (8, 3): 110,
                       (8, 2): 86,
                       (9, 1): 232, (9, 0): 182, (9, 3): 132, (9, 2): 100, (10, 1): 274, (10, 0): 216, (10, 3): 154,
                       (10, 2): 122, (11, 1): 324, (11, 0): 254, (11, 3): 180, (11, 2): 140, (12, 1): 370, (12, 0): 290,
                       (12, 3): 206, (12, 2): 158, (13, 1): 428, (13, 0): 334, (13, 3): 244, (13, 2): 180, (14, 1): 461,
                       (14, 0): 365, (14, 3): 261, (14, 2): 197, (15, 1): 523, (15, 0): 415, (15, 3): 295, (15, 2): 223,
                       (16, 1): 589, (16, 0): 453, (16, 3): 325, (16, 2): 253, (17, 1): 647, (17, 0): 507, (17, 3): 367,
                       (17, 2): 283, (18, 1): 721, (18, 0): 563, (18, 3): 397, (18, 2): 313, (19, 1): 795, (19, 0): 627,
                       (19, 3): 445, (19, 2): 341, (20, 1): 861, (20, 0): 669, (20, 3): 485, (20, 2): 385, (21, 1): 932,
                       (21, 0): 714, (21, 3): 512, (21, 2): 406, (22, 1): 1006, (22, 0): 782, (22, 3): 568,
                       (22, 2): 442,
                       (23, 1): 1094, (23, 0): 860, (23, 3): 614, (23, 2): 464, (24, 1): 1174, (24, 0): 914,
                       (24, 3): 664,
                       (24, 2): 514, (25, 1): 1276, (25, 0): 1000, (25, 3): 718, (25, 2): 538, (26, 1): 1370,
                       (26, 0): 1062,
                       (26, 3): 754, (26, 2): 596, (27, 1): 1468, (27, 0): 1128, (27, 3): 808, (27, 2): 628,
                       (28, 1): 1531,
                       (28, 0): 1193, (28, 3): 871, (28, 2): 661, (29, 1): 1631, (29, 0): 1267, (29, 3): 911,
                       (29, 2): 701,
                       (30, 1): 1735, (30, 0): 1373, (30, 3): 985, (30, 2): 745, (31, 1): 1843, (31, 0): 1455,
                       (31, 3): 1033,
                       (31, 2): 793, (32, 1): 1955, (32, 0): 1541, (32, 3): 1115, (32, 2): 845, (33, 1): 2071,
                       (33, 0): 1631,
                       (33, 3): 1171, (33, 2): 901, (34, 1): 2191, (34, 0): 1725, (34, 3): 1231, (34, 2): 961,
                       (35, 1): 2306,
                       (35, 0): 1812, (35, 3): 1286, (35, 2): 986, (36, 1): 2434, (36, 0): 1914, (36, 3): 1354,
                       (36, 2): 1054,
                       (37, 1): 2566, (37, 0): 1992, (37, 3): 1426, (37, 2): 1096, (38, 1): 2702, (38, 0): 2102,
                       (38, 3): 1502, (38, 2): 1142, (39, 1): 2812, (39, 0): 2216, (39, 3): 1582, (39, 2): 1222,
                       (40, 1): 2956, (40, 0): 2334, (40, 3): 1666, (40, 2): 1276}
    # Distribution of codewords into blocks for each (version, error_correction_level).
    CODEWORD_BLOCK_GROUP_DISTRIBUTIONS: TupleDict[int, List[int]] = {(1, 1): [1, 19, 0, 0], (1, 0): [1, 16, 0, 0], (1, 3): [1, 13, 0, 0],
                                          (1, 2): [1, 9, 0, 0],
                                          (2, 1): [1, 34, 0, 0], (2, 0): [1, 28, 0, 0], (2, 3): [1, 22, 0, 0],
                                          (2, 2): [1, 16, 0, 0],
                                          (3, 1): [1, 55, 0, 0], (3, 0): [1, 44, 0, 0], (3, 3): [2, 17, 0, 0],
                                          (3, 2): [2, 13, 0, 0],
                                          (4, 1): [1, 80, 0, 0], (4, 0): [2, 32, 0, 0], (4, 3): [2, 24, 0, 0],
                                          (4, 2): [4, 9, 0, 0],
                                          (5, 1): [1, 108, 0, 0], (5, 0): [2, 43, 0, 0], (5, 3): [2, 15, 2, 16],
                                          (5, 2): [2, 11, 2, 12],
                                          (6, 1): [2, 68, 0, 0], (6, 0): [4, 27, 0, 0], (6, 3): [4, 19, 0, 0],
                                          (6, 2): [4, 15, 0, 0],
                                          (7, 1): [2, 78, 0, 0], (7, 0): [4, 31, 0, 0], (7, 3): [2, 14, 4, 15],
                                          (7, 2): [4, 13, 1, 14],
                                          (8, 1): [2, 97, 0, 0], (8, 0): [2, 38, 2, 39], (8, 3): [4, 18, 2, 19],
                                          (8, 2): [4, 14, 2, 15],
                                          (9, 1): [2, 116, 0, 0], (9, 0): [3, 36, 2, 37], (9, 3): [4, 16, 4, 17],
                                          (9, 2): [4, 12, 4, 13],
                                          (10, 1): [2, 68, 2, 69], (10, 0): [4, 43, 1, 44], (10, 3): [6, 19, 2, 20],
                                          (10, 2): [6, 15, 2, 16], (11, 1): [4, 81, 0, 0], (11, 0): [1, 50, 4, 51],
                                          (11, 3): [4, 22, 4, 23], (11, 2): [3, 12, 8, 13], (12, 1): [2, 92, 2, 93],
                                          (12, 0): [6, 36, 2, 37], (12, 3): [4, 20, 6, 21], (12, 2): [7, 14, 4, 15],
                                          (13, 1): [4, 107, 0, 0], (13, 0): [8, 37, 1, 38], (13, 3): [8, 20, 4, 21],
                                          (13, 2): [12, 11, 4, 12], (14, 1): [3, 115, 1, 116], (14, 0): [4, 40, 5, 41],
                                          (14, 3): [11, 16, 5, 17], (14, 2): [11, 12, 5, 13], (15, 1): [5, 87, 1, 88],
                                          (15, 0): [5, 41, 5, 42], (15, 3): [5, 24, 7, 25], (15, 2): [11, 12, 7, 13],
                                          (16, 1): [5, 98, 1, 99], (16, 0): [7, 45, 3, 46], (16, 3): [15, 19, 2, 20],
                                          (16, 2): [3, 15, 13, 16], (17, 1): [1, 107, 5, 108], (17, 0): [10, 46, 1, 47],
                                          (17, 3): [1, 22, 15, 23], (17, 2): [2, 14, 17, 15], (18, 1): [5, 120, 1, 121],
                                          (18, 0): [9, 43, 4, 44], (18, 3): [17, 22, 1, 23], (18, 2): [2, 14, 19, 15],
                                          (19, 1): [3, 113, 4, 114], (19, 0): [3, 44, 11, 45], (19, 3): [17, 21, 4, 22],
                                          (19, 2): [9, 13, 16, 14], (20, 1): [3, 107, 5, 108], (20, 0): [3, 41, 13, 42],
                                          (20, 3): [15, 24, 5, 25], (20, 2): [15, 15, 10, 16],
                                          (21, 1): [4, 116, 4, 117],
                                          (21, 0): [17, 42, 0, 0], (21, 3): [17, 22, 6, 23], (21, 2): [19, 16, 6, 17],
                                          (22, 1): [2, 111, 7, 112], (22, 0): [17, 46, 0, 0], (22, 3): [7, 24, 16, 25],
                                          (22, 2): [34, 13, 0, 0], (23, 1): [4, 121, 5, 122], (23, 0): [4, 47, 14, 48],
                                          (23, 3): [11, 24, 14, 25], (23, 2): [16, 15, 14, 16],
                                          (24, 1): [6, 117, 4, 118],
                                          (24, 0): [6, 45, 14, 46], (24, 3): [11, 24, 16, 25], (24, 2): [30, 16, 2, 17],
                                          (25, 1): [8, 106, 4, 107], (25, 0): [8, 47, 13, 48], (25, 3): [7, 24, 22, 25],
                                          (25, 2): [22, 15, 13, 16], (26, 1): [10, 114, 2, 115],
                                          (26, 0): [19, 46, 4, 47],
                                          (26, 3): [28, 22, 6, 23], (26, 2): [33, 16, 4, 17], (27, 1): [8, 122, 4, 123],
                                          (27, 0): [22, 45, 3, 46], (27, 3): [8, 23, 26, 24], (27, 2): [12, 15, 28, 16],
                                          (28, 1): [3, 117, 10, 118], (28, 0): [3, 45, 23, 46],
                                          (28, 3): [4, 24, 31, 25],
                                          (28, 2): [11, 15, 31, 16], (29, 1): [7, 116, 7, 117],
                                          (29, 0): [21, 45, 7, 46],
                                          (29, 3): [1, 23, 37, 24], (29, 2): [19, 15, 26, 16],
                                          (30, 1): [5, 115, 10, 116],
                                          (30, 0): [19, 47, 10, 48], (30, 3): [15, 24, 25, 25],
                                          (30, 2): [23, 15, 25, 16],
                                          (31, 1): [13, 115, 3, 116], (31, 0): [2, 46, 29, 47],
                                          (31, 3): [42, 24, 1, 25],
                                          (31, 2): [23, 15, 28, 16], (32, 1): [17, 115, 0, 0],
                                          (32, 0): [10, 46, 23, 47],
                                          (32, 3): [10, 24, 35, 25], (32, 2): [19, 15, 35, 16],
                                          (33, 1): [17, 115, 1, 116],
                                          (33, 0): [14, 46, 21, 47], (33, 3): [29, 24, 19, 25],
                                          (33, 2): [11, 15, 46, 16],
                                          (34, 1): [13, 115, 6, 116], (34, 0): [14, 46, 23, 47],
                                          (34, 3): [44, 24, 7, 25],
                                          (34, 2): [59, 16, 1, 17], (35, 1): [12, 121, 7, 122],
                                          (35, 0): [12, 47, 26, 48],
                                          (35, 3): [39, 24, 14, 25], (35, 2): [22, 15, 41, 16],
                                          (36, 1): [6, 121, 14, 122],
                                          (36, 0): [6, 47, 34, 48], (36, 3): [46, 24, 10, 25], (36, 2): [2, 15, 64, 16],
                                          (37, 1): [17, 122, 4, 123], (37, 0): [29, 46, 14, 47],
                                          (37, 3): [49, 24, 10, 25],
                                          (37, 2): [24, 15, 46, 16], (38, 1): [4, 122, 18, 123],
                                          (38, 0): [13, 46, 32, 47],
                                          (38, 3): [48, 24, 14, 25], (38, 2): [42, 15, 32, 16],
                                          (39, 1): [20, 117, 4, 118],
                                          (39, 0): [40, 47, 7, 48], (39, 3): [43, 24, 22, 25],
                                          (39, 2): [10, 15, 67, 16],
                                          (40, 1): [19, 118, 6, 119], (40, 0): [18, 47, 31, 48],
                                          (40, 3): [34, 24, 34, 25],
                                          (40, 2): [20, 15, 61, 16]}
    # Number of error correction codewords for each (version, error_correction_level).
    ERROR_CORRECTION_CODEWORDS: TupleDict[int, int] = {(1, 1): 7, (1, 0): 10, (1, 3): 13, (1, 2): 17, (2, 1): 10, (2, 0): 16, (2, 3): 22,
                                  (2, 2): 28, (3, 1): 15, (3, 0): 26, (3, 3): 18, (3, 2): 22, (4, 1): 20, (4, 0): 18,
                                  (4, 3): 26, (4, 2): 16, (5, 1): 26, (5, 0): 24, (5, 3): 18, (5, 2): 22, (6, 1): 18,
                                  (6, 0): 16, (6, 3): 24, (6, 2): 28, (7, 1): 20, (7, 0): 18, (7, 3): 18, (7, 2): 26,
                                  (8, 1): 24, (8, 0): 22, (8, 3): 22, (8, 2): 26, (9, 1): 30, (9, 0): 22, (9, 3): 20,
                                  (9, 2): 24, (10, 1): 18, (10, 0): 26, (10, 3): 24, (10, 2): 28, (11, 1): 20,
                                  (11, 0): 30, (11, 3): 28, (11, 2): 24, (12, 1): 24, (12, 0): 22, (12, 3): 26,
                                  (12, 2): 28, (13, 1): 26, (13, 0): 22, (13, 3): 24, (13, 2): 22, (14, 1): 30,
                                  (14, 0): 24, (14, 3): 20, (14, 2): 24, (15, 1): 22, (15, 0): 24, (15, 3): 30,
                                  (15, 2): 24, (16, 1): 24, (16, 0): 28, (16, 3): 24, (16, 2): 30, (17, 1): 28,
                                  (17, 0): 28, (17, 3): 28, (17, 2): 28, (18, 1): 30, (18, 0): 26, (18, 3): 28,
                                  (18, 2): 28, (19, 1): 28, (19, 0): 26, (19, 3): 26, (19, 2): 26, (20, 1): 28,
                                  (20, 0): 26, (20, 3): 30, (20, 2): 28, (21, 1): 28, (21, 0): 26, (21, 3): 28,
                                  (21, 2): 30, (22, 1): 28, (22, 0): 28, (22, 3): 30, (22, 2): 24, (23, 1): 30,
                                  (23, 0): 28, (23, 3): 30, (23, 2): 30, (24, 1): 30, (24, 0): 28, (24, 3): 30,
                                  (24, 2): 30, (25, 1): 26, (25, 0): 28, (25, 3): 30, (25, 2): 30, (26, 1): 28,
                                  (26, 0): 28, (26, 3): 28, (26, 2): 30, (27, 1): 30, (27, 0): 28, (27, 3): 30,
                                  (27, 2): 30, (28, 1): 30, (28, 0): 28, (28, 3): 30, (28, 2): 30, (29, 1): 30,
                                  (29, 0): 28, (29, 3): 30, (29, 2): 30, (30, 1): 30, (30, 0): 28, (30, 3): 30,
                                  (30, 2): 30, (31, 1): 30, (31, 0): 28, (31, 3): 30, (31, 2): 30, (32, 1): 30,
                                  (32, 0): 28, (32, 3): 30, (32, 2): 30, (33, 1): 30, (33, 0): 28, (33, 3): 30,
                                  (33, 2): 30, (34, 1): 30, (34, 0): 28, (34, 3): 30, (34, 2): 30, (35, 1): 30,
                                  (35, 0): 28, (35, 3): 30, (35, 2): 30, (36, 1): 30, (36, 0): 28, (36, 3): 30,
                                  (36, 2): 30, (37, 1): 30, (37, 0): 28, (37, 3): 30, (37, 2): 30, (38, 1): 30,
                                  (38, 0): 28, (38, 3): 30, (38, 2): 30, (39, 1): 30, (39, 0): 28, (39, 3): 30,
                                  (39, 2): 30, (40, 1): 30, (40, 0): 28, (40, 3): 30, (40, 2): 30}
    # Character count indicator bit lengths for each mode and version range.
    CHARACTER_COUNT_INDICATORS: List[Tuple[int, int, List[int]]] = [
        (1, 9, [10, 9, 8, 8]),
        (10, 26, [12, 11, 16, 10]),
        (27, 40, [14, 13, 16, 12]),
    ]
    # Number of remainder bits for each version.
    REMAINDER_BITS: List[int] = [
        0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0,
        3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4,
        4, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0
    ]
    # Patterns for finder and alignment patterns.
    FINDER_PATTERN: Matrix[int] = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    # 5x5 Alignment pattern
    ALIGNMENT_PATTERN: Matrix[int] = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    # Mask pattern functions.
    MASK_PATTERNS: List[MaskFunction] = [
        lambda x, row, column: x if (row + column) % 2 else int(not x), # (row + column) mod 2 == 0
        lambda x, row, column: x if row % 2 else int(not x), # row mod 2 == 0
        lambda x, row, column: x if column % 3 else int(not x), # column mod 3 == 0
        lambda x, row, column: x if (row + column) % 3 else int(not x), # (row + column) mod 3 == 0
        lambda x, row, column: x if (math.floor(row / 2) + math.floor(column / 3)) % 2 else int(not x), # (floor(row/2) + floor(column/3)) mod 2 == 0
        lambda x, row, column: x if ((row * column) % 2) + ((row * column) % 3) else int(not x), # (row * column) mod 2 + (row * column) mod 3 == 0
        lambda x, row, column: x if (((row * column) % 2) + ((row * column) % 3)) % 2 else int(not x), # ((row * column) mod 2 + (row * column) mod 3) mod 2 == 0
        lambda x, row, column: x if (((row + column) % 2) + ((row * column) % 3)) % 2 else int(not x), # ((row + column) mod 2 + (row * column) mod 3) mod 2 == 0
    ]
    # Tag colour codes.
    TAG_COLOUR_CODES: List[str] = ["darkgray", "dimgray", "gold", "goldenrod", "blue", "mediumblue", "red", "darkred"]

    @staticmethod
    def toBinary(data: Any, length: int) -> str:
        """
            Convert data to binary string of specified length.

            Args:
                data: The data to convert.
                length: The length of the resulting binary string.
            
            Returns:
                A binary string representation of the data, padded with leading zeros to the specified length.
        """
        # Convert data to binary and remove the '0b' prefix, then pad with leading zeros.
        return str(bin(data))[2:].zfill(length)

    def __init__(self, data: str, error_correction: QRCode.ERROR_CORRECTIONS | str = None,
                 file: str = None, show_debug: bool = None):
        """
            Initialise and create a QRCode object with the provided data, error correction level, and version.

            Args:
                data (str): The data to encode in the QR code.
                error_correction (QRCode.ERROR_CORRECTIONS | str): The error correction level to use.
                file (str): The name of the output SVG file.
                show_debug (bool): Whether to generate a tag SVG for debugging.
            
            Raises:
                ValueError: If no data is provided.
        """
        self.show_tags = show_debug is not None # Store the show_tags flag.

        assert data != "", ValueError("Data must be provided") # Cannot create a QR code without data.
        self.data: str = data # Store the provided data.

        if file is None: file = "qr.svg"
        elif type(file) is str and not file.endswith(".svg"): file += ".svg" # Add .svg file extension.

        self.mode = self._determine_encoding_mode() # Determine the encoding mode based on the data.

        if type(error_correction) is str: error_correction = QRCode.ERROR_CORRECTIONS[error_correction] # Ensure Enum type.
        if error_correction is None: error_correction = QRCode.ERROR_CORRECTIONS.M
        self.error_correction: QRCode.ERROR_CORRECTIONS = error_correction # Store the error correction level.

        self.data_length = self._get_data_length() # Get the length of the data.

        self.version = self._determine_version() # Determine the version if not provided.

        self.alignment_positions = self._get_alignment_positions() # Get alignment pattern positions.

        # Calculate required codewords and bits.
        self.required_codewords = QRCode.TOTAL_CODEWORDS[(self.version, self.error_correction.value)]
        self.required_bit_count = self.required_codewords * 8 # Each codeword is 8 bits.

        self.bit_string = self._generate_bit_string() # Generate the bit string from the data.
        self.codewords = self._convert_bit_string_to_codewords() # Convert the bit string to codewords.

        self.codeword_block_distribution = QRCode.CODEWORD_BLOCK_GROUP_DISTRIBUTIONS[
            (self.version, self.error_correction.value)] # Get codeword block distribution.
        # Get number of error correction codewords.
        self.error_correction_codewords = QRCode.ERROR_CORRECTION_CODEWORDS[(self.version, self.error_correction.value)]

        self.codeword_blocks = self._generate_codeword_blocks(self.codewords) # Generate codeword blocks.

        self.prime = 0x11D # Primitive polynomial for GF(2^8).
        self.galois_field_size = 0x100 # Size of the Galois Field GF(2^8).
        self.galois_field = GaloisField(self.prime, self.galois_field_size) # Initialise Galois Field.

        self.generator_polynomial = self._create_generator_polynomial() # Create generator polynomial.
        self.ecc_blocks = self._create_ecc_blocks() # Create error correction codeword blocks.

        self.codewords_interleaved = self._interleave_blocks(self.codeword_blocks) # Interleave data codeword blocks.
        self.ecc_interleaved = self._interleave_blocks(self.ecc_blocks) # Interleave ECC codeword blocks.

        self.interleaved_data = self.codewords_interleaved + self.ecc_interleaved # Combine interleaved data and ECC.
        self.processed_binary = self._convert_data_to_binary(self.interleaved_data) # Convert interleaved data to binary.
        # Add remainder bits to the processed binary data.
        self.filled_binary = [int(bit) for bit in list(self._add_remainder_bits(self.processed_binary))]

        self.qr_size = (((self.version - 1) * 4) + 21) # Calculate the size of the QR code matrix.
        self.qr_matrix: Matrix[int] = [[-1] * self.qr_size for _ in range(self.qr_size)] # Initialise the QR code matrix with -1 (unassigned).
        self.tag_matrix: Matrix[QRCode.TAGS] = [[QRCode.TAGS.UNASSIGNED] * self.qr_size for _ in range(self.qr_size)] # Initialise the tag matrix.
        self.debug_matrix: List[Tuple[Matrix[int], Matrix[QRCode.TAGS]]] = [] # Initialise debug matrix.

        self._add_finder_patterns() # Add finder patterns to the matrix.
        self._add_alignment_patterns() # Add alignment patterns to the matrix.
        self._add_timing_patterns() # Add timing patterns to the matrix.
        self._add_dark_module() # Add the dark module to the matrix.
        if self.show_tags: self._add_snapshot_to_debug() # Snapshot the current qr and tag.

        self._reserve_format_area() # Reserve space for format information.
        self._reserve_version_area() # Reserve space for version information.
        if self.show_tags: self._add_snapshot_to_debug() # Snapshot the current qr and tag.

        self._fill_with_data() # Fill the matrix with data bits.
        self._determine_best_mask() # Determine & apply the best mask pattern.
        self._add_format_info() # Add format information to the matrix.
        self._add_version_info() # Add version information to the matrix.

        self._export_svg(file) # Export the QR code to an SVG file.
        if self.show_tags:
            self._add_snapshot_to_debug() # Snapshot the current qr and tag.
            self._export_debug("debug.svg") # Export the tag matrix to an SVG file for debugging.

    def _export_svg(self, file: str = "qr-code.svg", module_size: int = 20, quiet_zone: int = 4, background: str = "white", foreground: str = "black"):
        """
            Export the QR code matrix to an SVG file.

            Args:
                file (str): The name of the output SVG file.
                module_size (int): The size of each module (square) in the QR code.
                quiet_zone (int): The width of the quiet zone (margin) around the QR code, in modules.
                background (str): The background color of the QR code.
                foreground (str): The foreground color of the QR code.
        """
        total_size = (self.qr_size + (quiet_zone * 2)) * module_size # Calculate total size including quiet zone.
        svg = [
            f'<svg shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg" width="{total_size}" height="{total_size}" viewBox="0 0 {total_size} {total_size}">',
            f'<rect width="100%" height="100%" fill="{background}"/>'
        ] # SVG header and background.
        for row in range(self.qr_size): # Iterate through the QR code matrix.
            for column in range(self.qr_size): # Iterate through each column in the row.
                if self.qr_matrix[row][column] == 1: # If the module is black.
                    # Add a black rectangle to the svg.
                    svg.append(f'<rect x="{(column + quiet_zone) * module_size}" y="{(row + quiet_zone) * module_size}" width="{module_size}" height="{module_size}" fill="{foreground}"/>')
        with open(file, 'w') as file: # Write the SVG content to the specified file.
            svg.append('</svg>') # SVG footer.
            file.writelines(svg) # Write all SVG lines to the file.

    def _add_snapshot_to_debug(self):
        """
            Save a snapshot of the current QR code matrix to the debug file.
        """
        self.debug_matrix.append(copy.deepcopy((self.qr_matrix, self.tag_matrix)))

    def _export_debug(self, file: str = "tag.svg", module_size: int = 20, background: str = "white", foreground: str = "black"):
        """
            Export the tag matrix to an SVG file for debugging purposes.

            Args:
                file (str): The name of the output SVG file.
                module_size (int): The size of each module (square) in the QR code.
        """
        debugs = len(self.debug_matrix) + 1
        column_count = int(math.sqrt(debugs))
        row_count = debugs // column_count
        total_size = (self.qr_size * column_count) * module_size # Calculate total size including quiet zone.
        svg: List[str] = [
            f'<svg shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg" width="{total_size}" height="{total_size}" viewBox="0 0 {total_size} {total_size}">',
            f'<rect width="100%" height="100%" fill="{background}"/>'
        ]  # SVG header and background.
        for debug_row in range(row_count):
            for debug_column in range(column_count):
                index = (debug_row * column_count) + debug_column
                qr_matrix, tag_matrix = self.debug_matrix[index if index < (debugs - 1) else -1]
                for row_index, row in enumerate(qr_matrix):  # Iterate through the QR code matrix.
                    for column_index, column in enumerate(row):  # Iterate through each column in the row.
                        # Add a colour-coded rectangle.
                        # If someone figures out why this error is happening then you are amazing.
                        # I DO NOT UNDERSTAND WHY I'M GETTING "Type alias is not generic or already specialized"!!!
                        # It's really doing my head in...
                        # noinspection PyTypeHints
                        svg.append(
                            f'<rect x="{((debug_column * self.qr_size) + column_index) * module_size}" y="{((debug_row * self.qr_size) + row_index) * module_size}" width="{module_size}" height="{module_size}" fill="{
                                QRCode.TAG_COLOUR_CODES[
                                    (tag_matrix[row_index][column_index].value * 2) +
                                    (1 if column == 1 else 0)
                                ] if index < (debugs - 1) else (foreground if column == 1 else background)
                            }"/>')
        with open(file, 'w') as file: # Write the SVG content to the specified file.
            svg.append('</svg>') # SVG footer.
            file.writelines(svg) # Write all SVG lines to the file.

    def _apply_mask(self, matrix: Matrix[int] | None = None, mask_function: MaskFunction | None = None) -> Matrix[int]:
        """
            Apply the selected mask pattern to the QR code matrix.

            Args:
                matrix (Matrix[int] | None): The QR code matrix to apply the mask to. If None, use self.qr_matrix.
                mask_function (MaskFunction | None): The mask function to use. If None, use the selected mask pattern.

            Returns:
                Matrix[int]: The masked QR code matrix.
        """
        if matrix is None:
            matrix = self.qr_matrix # Use the provided matrix.
        if mask_function is None:
            mask_function = QRCode.MASK_PATTERNS[self.mask] # Use the provided mask function.
        for row_index, row in enumerate(matrix): # Iterate through each row in the QR code matrix.
            for column, bit in enumerate(row): # Iterate through each column in the row.
                if self.tag_matrix[row_index][column] == QRCode.TAGS.DATA: # If the module is data (not reserved).
                    matrix[row_index][column] = mask_function(bit, row_index, column) # Apply the mask pattern to the module.
        return matrix # Return masked matrix.

    def _add_finder_patterns(self):
        """
            Add finder patterns to the QR code matrix.
        """
        positions = [
                [0, 0],
                [0, self.qr_size - 7],
                [self.qr_size - 7, 0],
            ] # Top-left, top-right, bottom-left positions.
        for position in positions: # Iterate through each finder pattern position.
            lower_bound_row, upper_bound_row = position[0] - 1, position[0] # Define row bounds.
            lower_bound_col, upper_bound_col = position[1] - 1, position[1] # Define column bounds.
            for row_index, row in enumerate(QRCode.FINDER_PATTERN): # Iterate through each row of the finder pattern.
                if lower_bound_row + row_index >= 0 and upper_bound_row + row_index <= self.qr_size: # Check row bounds.
                    for column, bit in enumerate(row): # Iterate through each column in the row.
                        if lower_bound_col + column >= 0 and upper_bound_col + column <= self.qr_size: # Check column bounds.
                            self.qr_matrix[lower_bound_row + row_index][lower_bound_col + column] = bit # Set the module in the QR matrix.
                            self.tag_matrix[lower_bound_row + row_index][lower_bound_col + column] = QRCode.TAGS.FINDER_PATTERN # Mark as part of the finder pattern.

    def _add_alignment_patterns(self):
        """
            Add alignment patterns to the QR code matrix.
        """
        for row in QRCode.ALIGNMENT_POSITIONS[self.version]: # Iterate through each alignment position row.
            for column in QRCode.ALIGNMENT_POSITIONS[self.version]: # Iterate through each alignment position column.
                row_start, column_start = row - 2, column - 2 # Calculate starting positions.
                if not ((row <= 6 and column <= 6) or
                        (row <= 6 and column >= self.qr_size - 7) or
                        (row >= self.qr_size - 7 and column <= 6)): # Skip if overlapping with finder patterns.
                    for alignment_row, pattern_row in enumerate(QRCode.ALIGNMENT_PATTERN): # Iterate through each row of the alignment pattern.
                        for alignment_column, bit in enumerate(pattern_row): # Iterate through each column in the row.
                            self.qr_matrix[row_start + alignment_row][column_start + alignment_column] = bit # Set the module in the QR matrix.
                            self.tag_matrix[row_start + alignment_row][column_start + alignment_column] = QRCode.TAGS.ALIGNMENT_PATTERN # Mark as part of the alignment pattern.

    def _add_timing_patterns(self):
        """
            Add timing patterns to the QR code matrix.
        """
        for column in range(8, self.qr_size - 8): # Iterate through columns for timing patterns.
            self.qr_matrix[6][column] = int(not(column % 2)) # Set timing pattern in row 6.
            self.qr_matrix[column][6] = int(not(column % 2)) # Set timing pattern in column 6.
            self.tag_matrix[6][column] = QRCode.TAGS.TIMING_PATTERN # Mark as part of the timing pattern.
            self.tag_matrix[column][6] = QRCode.TAGS.TIMING_PATTERN # Mark as part of the timing pattern.

    def _add_dark_module(self):
        """
            Add the dark module to the QR code matrix.
        """
        self.qr_matrix[(4 * self.version) + 9][8] = 1 # Set the dark module.
        self.tag_matrix[(4 * self.version) + 9][8] = QRCode.TAGS.DARK_MODULE # Mark as part of the dark module.

    def _reserve_format_area(self):
        """
            Reserve the format information area in the QR code matrix.
        """
        for column in range(0, 9): # Iterate through columns for format information.
            # Reserve format information area in the top-left.
            if self.tag_matrix[8][column].value < 1: # Check if the module is unassigned.
                self.tag_matrix[8][column] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
            if self.tag_matrix[column][8].value < 1: # Check if the module is unassigned.
                self.tag_matrix[column][8] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
            # Reserve format information area in the bottom-left and top-right.
            if column < 8: # Check if column is less than 8 as we don't need a corner module here.
                start = self.qr_size - 8 + column  # Calculate the position at start of the format info area.
                if self.tag_matrix[8][start].value < 1: # Check if the module is unassigned.
                    self.tag_matrix[8][start] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
                if self.tag_matrix[start][8].value < 1: # Check if the module is unassigned.
                    self.tag_matrix[start][8] = QRCode.TAGS.FORMAT_INFO # Mark as format information.

    def _reserve_version_area(self):
        """
            Reserve the version information area in the QR code matrix for versions 7 and above.
        """
        if self.version >= 7: # Check if version is 7 or above.
            for row in range(self.qr_size - 11, self.qr_size - 8): # Iterate through rows for version information.
                for column in range(0, 6): # Iterate through columns for version information.
                    if self.tag_matrix[row][column].value < 1: # Check if the module is unassigned.
                        self.tag_matrix[row][column] = QRCode.TAGS.VERSION_INFO # Mark as version information.
                    if self.tag_matrix[column][row].value < 1: # Check if the module is unassigned.
                        self.tag_matrix[column][row] = QRCode.TAGS.VERSION_INFO # Mark as version information.

    def _fill_with_data(self):
        """
            Fill the QR code matrix with data bits in a zigzag pattern.
        """
        upward = True # Direction flag for zigzag pattern.
        data_copy = copy.deepcopy(self.filled_binary) # Create a copy of the filled binary data.
        for column in range(self.qr_size - 1, -1, -2): # Iterate through columns from right to left in pairs.
            if column == 6: continue # Skip the timing pattern column.
            for row in range(self.qr_size - 1, -1, -1) if upward else range(0, self.qr_size): # Iterate through rows in the current direction.
                if column != 6 and data_copy and self.tag_matrix[row][column].value < 1: # Check if the module is unassigned and data is available.
                    self.qr_matrix[row][column] = data_copy.pop(0) # Fill the module with data bit.
                    self.tag_matrix[row][column] = QRCode.TAGS.DATA # Mark as data.
                if column != 0 and data_copy and self.tag_matrix[row][column - 1].value < 1: # Check the adjacent column.
                    self.qr_matrix[row][column - 1] = data_copy.pop(0) # Fill the adjacent module with data bit.
                    self.tag_matrix[row][column - 1] = QRCode.TAGS.DATA # Mark as data.
            upward = not upward # Change direction for next column pair.
        # Fill any remaining unassigned modules with 0.
        for row in range(self.qr_size): # Iterate through all rows.
            for column in range(self.qr_size): # Iterate through all columns.
                if self.tag_matrix[row][column] == QRCode.TAGS.UNASSIGNED: # Check for any unassigned modules.
                    self.qr_matrix[row][column] = 0 # Set unassigned modules to 0.
                    self.tag_matrix[row][column] = QRCode.TAGS.DATA # Mark as data.

    @staticmethod
    def _mask_score_1(matrix: Matrix[int]) -> int:
        """
            Calculate the test one penalty score for consecutive modules in rows and columns.

            Args:
                matrix (Matrix[int]): The QR code matrix to evaluate.

            Returns:
                int: The penalty score for consecutive modules in rows and columns.
        """
        score = 0 # Initialise score at 0.
        for index, row in enumerate(matrix): # Iterate through each row.
            column = [matrix[row_index][index] for row_index in range(len(matrix))] # Put the current column into a list.
            # Count consecutive duplicates of numbers.
            for count in ([sum(1 for _ in group) for _, group in itertools.groupby(row)] + [sum(1 for _ in group) for _, group in itertools.groupby(column)]):
                if count >= 5: score += count - 2 # If there's more than 5, add 3 and then another 1 for each duplicate.
        return score # Return the total pentalty score.

    @staticmethod
    def _mask_score_2(matrix: Matrix[int]) -> int:
        """
            Calculate the test two penalty score for 2x2 blocks of modules.

            Args:
                matrix (Matrix[int]): The QR code matrix to evaluate.

            Returns:
                int: The penalty score for 2x2 blocks of modules.
        """
        score = 0 # Initialise score at 0.
        for row_index, row in enumerate(matrix[:-1]): # Iterate through each row except the last.
            for column_index, bit in enumerate(row[:-1]): # Iterate through each column except the last.
                next_row = matrix[row_index + 1] # Get the next row.
                bit_sum = bit + row[column_index + 1] + next_row[column_index] + next_row[column_index + 1] # Sum the 2x2 block.
                if bit_sum == 0 or bit_sum == 4: score += 3 # Check if all modules are the same colour, and add to score if true.
        return score # Return the total penalty score.

    @staticmethod
    def _mask_score_3(matrix: Matrix[int]) -> int:
        """
            Calculate the test three penalty score for finder-like patterns in rows and columns.

            Args:
                matrix (Matrix[int]): The QR code matrix to evaluate.

            Returns:
                int: The penalty score for finder-like patterns in rows and columns.
        """
        score = 0 # Initialise score at 0.
        for index, row in enumerate(matrix): # Iterate through each row in the QR code matrix.
            # Combine row and column so we can check at the same time.
            string = ''.join([str(bit) for bit in row]) + ''.join([str(drow[index]) for drow in matrix])
            search = True # Initialise search flag.
            while search: # Continue searching for patterns.
                if "000010111010000" in string: # Check for pattern in string.
                    score += 40 # Add to score if pattern found.
                    string = string.replace("000010111010000", "", 1) # Remove pattern from string to avoid double counting.
                elif "111101000101111" in string: # Check for inverse pattern in string.
                    score += 40 # Add to score if inverse pattern found.
                    string = string.replace("111101000101111", "", 1) # Remove inverse pattern from string to avoid double counting.
                else: search = False # No more patterns found, stop searching.
        return score # Return the total penalty score.

    @staticmethod
    def _mask_score_4(matrix: Matrix[int]) -> int:
        """
            Calculate the test four penalty score for the balance of dark and light modules.

            Args:
                matrix (Matrix[int]): The QR code matrix to evaluate.
            
            Returns:
                int: The penalty score for the balance of dark and light modules.
        """
        base_value = (
            (20 * sum(bit for row in matrix for bit in row if bit == 1)) // (len(matrix) ** 2)
        ) # Count the number of dark modules in the matrix and find the base value from this.
        return ( # Calculate and return the penalty score based on the base value.
            10 * min(
                abs(base_value - 10),
                abs(base_value - 9)
            )
        )

    def _score_mask(self, mask_function: MaskFunction) -> Tuple[int, Matrix[int]]:
        """
            Test a mask pattern on the QR code matrix and return its penalty score.

            Args:
                mask_function (MaskFunction): The mask pattern function to apply.

            Returns:
                Tuple[int, Matrix[int]]: The penalty score for the masked QR code matrix.
        """
        qr_matrix_copy = copy.deepcopy(self.qr_matrix) # Create a copy of the QR code matrix.
        masked_matrix = self._apply_mask(qr_matrix_copy, mask_function) # Apply the mask pattern to the copied matrix.
        return ( # Calculate and return the total penalty score for the masked matrix.
            self._mask_score_1(masked_matrix) +
            self._mask_score_2(masked_matrix) +
            self._mask_score_3(masked_matrix) +
            self._mask_score_4(masked_matrix)
        ), masked_matrix # Return the total penalty score and the masked matrix.

    def _determine_best_mask(self):
        """
            Determine the best mask pattern for the QR code matrix based on penalty scores.
        """
        best_score = math.inf # Initialise list to store scores.
        best_mask_and_matrix = (0, self.qr_matrix) # Initialise variable to store the best masked matrix.
        for mask, mask_function in enumerate(QRCode.MASK_PATTERNS): # Iterate through each mask pattern.
            mask_score, masked_matrix = self._score_mask(mask_function) # Get the penalty score for the mask pattern.
            if mask_score < best_score: # Check if the score is better than the previous best score.
                best_score = mask_score # Add the score and mask index to the list.
                best_mask_and_matrix = (mask, masked_matrix) # Update the best masked matrix.
        self.mask, self.qr_matrix = best_mask_and_matrix # Set the best mask and masked matrix.

    def _generate_format_string(self) -> str:
        """
            Generate the format string for the QR code.

            Returns:
                str: The format string for the QR code.
        """
        format_string = ( # Generate the initial format string without error correction.
                QRCode.toBinary(self.error_correction.value, 2) +
                QRCode.toBinary(self.mask, 3)
            )
        data = int(format_string, 2) << 10 # Shift left by 10 bits for error correction.
        remainder = data # Initialise remainder.
        while remainder.bit_length() > 10: # Perform polynomial division to get the remainder.
            remainder ^= 0b10100110111 << (remainder.bit_length() - 11) # XOR with the generator polynomial.
        return QRCode.toBinary((data | remainder) ^ 0b101010000010010, 15) # Combine data and remainder, apply mask, and return as binary string.

    def _add_format_info(self):
        """
            Add the format information to the QR code matrix.
        """
        # Generate the format string as a list of integers.
        self.format_string = [int(value) for value in list(self._generate_format_string())]
        index_horizontal, index_vertical = 0, 0 # Initialise indices for horizontal and vertical placement.
        for index in range(0, 8): # Iterate through the first 8 modules for format information.
            if self.tag_matrix[8][index] == QRCode.TAGS.FORMAT_INFO: # Check if the module is reserved for format information.
                self.qr_matrix[8][index] = self.format_string[index_horizontal] # Set the format information bit.
                self.tag_matrix[8][index] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
                index_horizontal += 1 # Increment horizontal index.
            if self.tag_matrix[self.qr_size - index - 1][8] == QRCode.TAGS.FORMAT_INFO: # Check if the module is reserved for format information.
                self.qr_matrix[self.qr_size - index - 1][8] = self.format_string[index_vertical] # Set the format information bit.
                self.tag_matrix[self.qr_size - index - 1][8] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
                index_vertical += 1 # Increment vertical index.
        for index in range(0, 8): # Iterate through the last 7 modules for format information.
            if self.tag_matrix[8 - index][8] == QRCode.TAGS.FORMAT_INFO: # Check if the module is reserved for format information.
                self.qr_matrix[8 - index][8] = self.format_string[index_horizontal] # Set the format information bit.
                self.tag_matrix[8 - index][8] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
                index_horizontal += 1 # Increment horizontal index.
            if self.tag_matrix[8][self.qr_size - 9 + index] == QRCode.TAGS.FORMAT_INFO: # Check if the module is reserved for format information.
                self.qr_matrix[8][self.qr_size - 9 + index] = self.format_string[index_vertical] # Set the format information bit.
                self.tag_matrix[8][self.qr_size - 9 + index] = QRCode.TAGS.FORMAT_INFO # Mark as format information.
                index_vertical += 1 # Increment vertical index.

    def _generate_version_string(self) -> str:
        """
            Generate the version string for the QR code.

            Returns:
                str: The version string for the QR code.
        """
        version_string = QRCode.toBinary(self.version, 6) # Generate the initial version string without error correction.
        data = int(version_string, 2) << 12 # Shift left by 12 bits for error correction.
        remainder = data # Initialise remainder.
        while remainder.bit_length() > 12: # Perform polynomial division to get the remainder.
            remainder ^= 0b1111100100101 << (remainder.bit_length() - 13) # XOR with the generator polynomial.
        return QRCode.toBinary((data | remainder), 18) # Combine data and remainder, and return as binary string.

    def _add_version_info(self):
        """
            Add the version information to the QR code matrix.
        """
        if self.version >= 7: # Check if version is 7 or above.
            self.version_string = [int(value) for value in self._generate_version_string()][::-1] # Generate the version string as a list of integers.
            index_horizontal, index_vertical = 0, 0 # Initialise indices for horizontal and vertical placement.
            for column in range(0, 6): # Iterate through columns for version information.
                for row in range(self.qr_size - 11, self.qr_size - 8): # Iterate through rows for version information.
                    if self.tag_matrix[row][column] == QRCode.TAGS.VERSION_INFO: # Check if the module is reserved for version information.
                        self.qr_matrix[row][column] = self.version_string[index_horizontal] # Set the version information bit.
                        self.tag_matrix[row][column] = QRCode.TAGS.VERSION_INFO # Mark as version information.
                        index_horizontal += 1 # Increment horizontal index.
                    if self.tag_matrix[column][row] == QRCode.TAGS.VERSION_INFO: # Check if the module is reserved for version information.
                        self.qr_matrix[column][row] = self.version_string[index_vertical] # Set the version information bit.
                        self.tag_matrix[column][row] = QRCode.TAGS.VERSION_INFO # Mark as version information.
                        index_vertical += 1 # Increment vertical index.

    def _generate_bit_string(self) -> str:
        """
            Generate the bit string for the QR code.

            Returns:
                str: The bit string for the QR code.
        """
        self.mode_indicator = QRCode.toBinary(self.mode.value, 4) # Mode indicator is always 4 bits.
        self.character_count_indicator_length = self._determine_character_count_indicator_length() # Determine the length of the character count indicator.
        self.character_count_indicator = QRCode.toBinary(self.data_length, self.character_count_indicator_length) # Generate the character count indicator.

        self.encoded_data = self._encode_data() # Encode the data.

        bit_string = (self.mode_indicator # Combine all parts to form the complete bit string.
                      + self.character_count_indicator
                      + self.encoded_data)

        # Add terminator bits.
        if len(bit_string) < self.required_bit_count: bit_string += "0" * min((self.required_bit_count - len(bit_string)), 4)
        # Add padding to make the bit string a multiple of 8 bits.
        if (len(bit_string) % 8) != 0: bit_string += "0" * (8 - (len(bit_string) % 8))

        bits_left = self.required_bit_count - len(bit_string) # Calculate remaining bits needed.
        bytes_left = bits_left // 8 # Calculate remaining bytes needed.

        bit_string += "1110110000010001" * (bytes_left // 2) # Add padding bytes.
        if bytes_left % 2 != 0: bit_string += "11101100" # Add final padding byte if needed.

        return bit_string # Return the complete bit string.

    def _convert_bit_string_to_codewords(self) -> Codewords:
        """
            Convert the bit string to a list of codewords.

            Returns:
                Codewords: A list of codewords.
        """
        # Convert each 8 bits of the bit string to an integer codeword.
        return list(map(lambda x: int(''.join(x), 2), zip(*[iter(self.bit_string)] * 8)))

    def _generate_codeword_blocks(self, codewords: Codewords) -> CodewordGroups:
        """
            Generate codeword blocks based on the codeword block distribution.

            Args:
                codewords (Codewords): The list of codewords to be divided into blocks.

            Returns:
                CodewordGroups: A list of codeword blocks.
        """
        blocks = [] # Initialise list to store codeword blocks.
        codewords_copy = copy.deepcopy(codewords) # Create a copy of the codewords to manipulate.
        for block_index in range(0, len(self.codeword_block_distribution), 2): # Iterate through the codeword block distribution in pairs.
            block = [] # Initialise list to store the current block.
            for _ in range(self.codeword_block_distribution[block_index]): # Iterate for the number of blocks of this size.
                group = [] # Initialise list to store the current group.
                for _ in range(self.codeword_block_distribution[block_index + 1]): # Iterate for the number of codewords in this block.
                    if len(codewords_copy) > 0: group.append(codewords_copy.pop(0)) # Check if there are remaining codewords and add the next codeword to the group.
                if group: block.append(group) # Add the group to the block if it is not empty.
            if block: blocks.append(block) # Add the block to the list of blocks if it is not empty.
        return blocks # Return the list of codeword blocks.

    def _read_codeword_groups(self):
        """
            Read and print the codeword groups for debugging purposes.
        """
        _blocks = [] # Initialise list to store codeword block sizes.
        for block in self.codeword_blocks: # Iterate through each codeword block.
            _block = [] # Initialise list to store the current block sizes.
            # Iterate through each group in the block and add the size of the group to the current block sizes.
            for group in block: _block.append(len(group))
            _blocks.append(_block) # Add the current block sizes to the list of codeword block sizes.

    def _create_generator_polynomial(self) -> Polynomial:
        """
            Create the generator polynomial for error correction.

            Returns:
                Polynomial: The generator polynomial.
        """
        current = Polynomial([
            self.galois_field.from_alpha(0),
        ]) # Initialise the generator polynomial.
        for power in range(self.error_correction_codewords): # Iterate through the number of error correction codewords.
            next_term = Polynomial([ # Create the next term in the generator polynomial.
                self.galois_field.from_alpha(power), # x term.
                self.galois_field.from_alpha(0), # constant term.
            ])
            current = current * next_term # Multiply the current polynomial by the next term.
        return current # Return the generator polynomial.

    def _divide_polynomials(self, message_polynomial: Polynomial) -> Polynomial:
        """
            Divide the message polynomial by the generator polynomial to get the remainder.

            Args:
                message_polynomial (Polynomial): The message polynomial to be divided.

            Returns:
                Polynomial: The remainder polynomial.
        """
        remainder = message_polynomial.shift(self.error_correction_codewords) # Shift the message polynomial by the number of error correction codewords.
        generator = self.generator_polynomial.copy() # Create a copy of the generator polynomial.
        degree_generator = generator.degree - 1 # Get the degree of the generator polynomial.
        # Perform polynomial long division with XOR operations.
        while remainder.degree - 1 >= degree_generator: remainder ^= generator.shift(remainder.degree - 1 - degree_generator) * remainder.coefficients[-1]
        return remainder # Return the remainder polynomial.

    def _create_ecc_blocks(self) -> CodewordGroups:
        """
            Create error correction codeword blocks.

            Returns:
                CodewordGroups: A list of error correction codeword blocks.
        """
        ecc_groups = [] # Initialise list to store error correction codeword blocks.
        for group in self.codeword_blocks: # Iterate through each codeword block group.
            ecc_blocks = [] # Initialise list to store the current group's error correction codeword blocks.
            for block in group: # Iterate through each block in the group.
                remainder = self._divide_polynomials( # Calculate the remainder polynomial for the block.
                    Polynomial([self.galois_field[byte] for byte in block][::-1]))
                # Generate error correction coefficients
                ecc = [coefficient.value for coefficient in remainder.coefficients[::-1]]
                # Pad error correction coefficients to the correct length.
                if len(ecc) < self.error_correction_codewords: ecc = [0] * (self.error_correction_codewords - len(ecc)) + ecc
                # Add the error correction codewords to the current group's blocks.
                ecc_blocks.append(ecc)
            ecc_groups.append(ecc_blocks) # Add the current group's error correction codeword blocks to the list.
        return ecc_groups # Return the list of error correction codeword blocks.

    @staticmethod
    def _interleave_blocks(groups: CodewordGroups) -> Codewords:
        """
            Interleave codeword blocks.

            Args:
                groups (CodewordGroups): The list of codeword blocks to be interleaved.

            Returns:
                Codewords: The interleaved codeword blocks.
        """
        blocks = [block for group in groups for block in group] # Flatten the list of groups into a single list of blocks.
        # Interleave the blocks by taking one codeword from each block in sequence.
        return [block[index] for index in range(max(len(block) for block in blocks)) for block in blocks if index < len(block)]

    @staticmethod
    def _convert_data_to_binary(data: Codewords) -> str:
        """
            Convert a list of integers to a binary string.

            Args:
                data (Codewords): The list of integers to be converted.

            Returns:
                str: The binary string representation of the data.
        """
        return ''.join([QRCode.toBinary(value, 8) for value in data]) # Convert each integer to an 8-bit binary string and concatenate.

    def _add_remainder_bits(self, binary: str) -> str:
        """
            Add remainder bits to the binary string.

            Args:
                binary (str): The binary string to which remainder bits will be added.

            Returns:
                str: The binary string with remainder bits added.
        """
        return binary + ("0" * QRCode.REMAINDER_BITS[self.version - 1]) # Add the required number of remainder bits.

    def _encode_data(self) -> str:
        """
            Encode the data based on the determined mode.

            Returns:
                str: The encoded data in binary format.
        """
        encoded_data = "" # Initialise variable to store the encoded data.
        match self.mode: # Determine the encoding method based on the mode.
            case QRCode.MODES.NUMERIC:
                encoded_data = self._encode_numeric() # Encode numeric data.
            case QRCode.MODES.ALPHANUMERIC:
                encoded_data = self._encode_alphanumeric() # Encode alphanumeric data.
            case QRCode.MODES.BYTE:
                encoded_data = self._encode_byte() # Encode byte data.
            case QRCode.MODES.KANJI:
                encoded_data = self._encode_kanji() # Encode Kanji data.
        return encoded_data # Return the encoded data.

    def _encode_numeric(self) -> str:
        """
            Encode numeric data into binary string.
            Splits into chunks of 3 digits, then encodes each chunk into binary.

            Returns:
                str: The encoded data in binary format.
        """
        encoded_data = "" # Initialise variable to store the encoded data.
        for i in range(0, len(self.data), 3): # Iterate through the data in chunks of 3 digits.
            chunk = self.data[i:i + 3] # Get the current chunk.
            encoded_data += QRCode.toBinary(int(chunk), (1 + (3 * len(chunk)))) # Encode the chunk into binary and add to the encoded data.
        return encoded_data # Return the encoded data.

    def _encode_alphanumeric(self) -> str:
        """
            Encode alphanumeric data into binary string.
            Pairs characters together, encodes each pair into binary.

            Returns:
                str: The encoded data in binary format.
        """
        encoded_data = "" # Initialise variable to store the encoded data.
        for i in range(0, len(self.data), 2): # Iterate through the data in pairs of characters.
            if i + 1 < len(self.data): # Check if there is a second character in the pair.
                first_char = QRCode.ALPHANUMERIC_CHARACTERS.index(self.data[i]) # Get the index of the first character.
                second_char = QRCode.ALPHANUMERIC_CHARACTERS.index(self.data[i + 1]) # Get the index of the second character.
                value = first_char * 45 + second_char # Calculate the combined value for the pair.
                encoded_data += QRCode.toBinary(value, 11) # Encode the combined value into binary and add to the encoded data.
            else: # Single character remaining.
                value = QRCode.ALPHANUMERIC_CHARACTERS.index(self.data[i]) # Get the index of the single character.
                encoded_data += QRCode.toBinary(value, 6) # Encode the single character into binary and add to the encoded data.
        return encoded_data # Return the encoded data.

    def _encode_byte(self) -> str:
        """
            Encode byte data into binary string.

            Returns:
                str: The encoded data in binary format.
        """
        # Encode each byte of the data into an 8-bit binary string and concatenate.
        return ''.join(QRCode.toBinary(byte, 8) for byte in self.data.encode('utf-8'))

    def _encode_kanji(self) -> str:
        """
            Encode Kanji data into binary string.

            Returns:
                str: The encoded data in binary format.
        """
        encoded_data = "" # Initialise variable to store the encoded data.
        shift_jis_bytes = self.data.encode('shift-jis') # Encode the data into Shift JIS bytes.
        for i in range(0, len(shift_jis_bytes), 2): # Iterate through the Shift JIS bytes in pairs.
            byte_pair = shift_jis_bytes[i:i + 2] # Get the current pair of bytes.
            value = byte_pair[0] << 8 | byte_pair[1] # Combine the two bytes into a single value.
            # Adjust the value based on the Shift JIS encoding ranges.
            if 0x8140 <= value <= 0x9FFC:
                value -= 0x8140 # Adjust for first range.
            elif 0xE040 <= value <= 0xEBBF:
                value -= 0xC140 # Adjust for second range.
            msb = value >> 8 # Get the most significant byte.
            lsb = value & 0xFF # Get the least significant byte.
            value = msb * 0xC0 + lsb # Calculate the final value for encoding.
            encoded_data += QRCode.toBinary(value, 13) # Encode the value into binary and add to the encoded data.
        return encoded_data # Return the encoded data.

    def _determine_character_count_indicator_length(self) -> int:
        """
            Determine the length of the character count indicator based on the version and mode.

            Returns:
                int: The length of the character count indicator.
        """
        for indicator in QRCode.CHARACTER_COUNT_INDICATORS: # Iterate through the character count indicator ranges.
            if indicator[0] <= self.version <= indicator[1]: # Check if the version is within the current range.
                return indicator[2][int(math.log(self.mode.value, 2))] # Return the corresponding length for the mode.
        raise ValueError("Data length is out of range") # Raise an error if the version is out of range.

    def _determine_encoding_mode(self) -> QRCode.MODES:
        """
            Determine the encoding mode based on the data content.

            Returns:
                MODES: The determined encoding mode.
        """
        if self.data.isascii(): return self._get_ascii_mode() # ASCII data.
        return self._get_non_ascii_mode() # Non-ASCII data.

    def _is_alphanumeric(self) -> bool:
        """
            Check if the data is alphanumeric.

            Returns:
                bool: True if the data is alphanumeric, False otherwise.
        """
        # Check if all characters in the data are in the alphanumeric character set.
        return all(char in QRCode.ALPHANUMERIC_CHARACTERS for char in self.data)

    def _get_ascii_mode(self) -> QRCode.MODES:
        """
            Determine mode for ASCII characters.

            Returns:
                MODES: Numeric, alphanumeric, or byte mode.
        """
        if self.data.isnumeric(): return QRCode.MODES.NUMERIC # Numeric data.
        elif self._is_alphanumeric(): return QRCode.MODES.ALPHANUMERIC # Alphanumeric data.
        return QRCode.MODES.BYTE # Byte data.

    def _get_non_ascii_mode(self) -> QRCode.MODES:
        """
            Determine mode for non-ASCII characters.

            Returns:
                MODES: Kanji or byte mode.
        """
        try:
            self.data.encode('shift-jis').decode('shift-jis') # Try to encode and decode the data in Shift JIS.
            return QRCode.MODES.KANJI # Kanji data.
        except UnicodeError: # If encoding/decoding fails, it's not Kanji.
            return QRCode.MODES.BYTE # Byte data.

    def _get_data_length(self) -> int:
        """
            Get the length of the data based on the encoding mode.

            Returns:
                int: The length of the data.
        """
        if self.mode == QRCode.MODES.BYTE: return len(self.data.encode('utf-8')) # Byte mode length.
        return len(self.data) # Numeric, alphanumeric, or Kanji mode length.

    def _determine_version(self) -> int:
        """
            Determine the minimum QR code version required to encode the data.

            Returns:
                int: The determined QR code version.
        """
        for version in range(1, 41): # Iterate through versions 1 to 40.
            # Get the capacity for the current version, error correction level, and mode.
            versionCapacity = QRCode.CAPACITIES[(version, self.error_correction.value, self.mode.value)]
            if versionCapacity >= self.data_length: return version # Return the version if it can accommodate the data.
        raise ValueError("Data too large for QR code") # Raise an error if data is too large for any version.

    def _get_alignment_positions(self) -> List[int]:
        """
            Get the alignment pattern positions for the current version.

            Returns:
                List[int]: The alignment pattern positions.
        """
        return QRCode.ALIGNMENT_POSITIONS[self.version] # Return the alignment pattern positions for the current version.
