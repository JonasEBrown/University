from ..Types import *

import ray

from ray.util.state import list_nodes
from ray.util.state.common import NodeState
from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy

type NodeData = Tuple[str, str, float, bool]
type NodeQuota = Tuple[str, str, float, int, bool]
