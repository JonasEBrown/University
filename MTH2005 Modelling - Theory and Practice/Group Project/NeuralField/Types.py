import os
import sys
import math
import json
import time
import signal
import datetime
import idx2numpy
import kagglehub
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from tqdm import tqdm
from typing import cast, Any, Dict, List, Tuple, Callable, TypeVar

T = TypeVar('T')

type NpVector = np.ndarray[np.float32]

type Scheme = Callable[[NpVector, NpVector, NpVector], Tuple[NpVector, NpVector]]

type ConnectivityMatrix = {
    "EE": NpVector,
    "EI": NpVector,
    "IE": NpVector,
    "II": NpVector,
}

type SimulationSnapshots = {
    "snapshots_E": List[NpVector],
    "snapshots_I": List[NpVector],
    "snapshot_times": List[float],
    "E_final": NpVector,
    "I_final": NpVector,
}
