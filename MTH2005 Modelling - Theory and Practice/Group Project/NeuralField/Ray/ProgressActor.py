import ray

from .RayTypes import *


@ray.remote
class ProgressActor:
    """
    Allows the RayOrchestrator to monitor the progress of its cluster by passing a ProgressActor class to each remote
    and providing getter and setter functions.
    """

    def __init__(self, quotas: List[Tuple[str, Any, Any, int, ...]]):
        self.totals: dict[str, int] = {node_info[0]: node_info[3] for node_info in quotas}
        self.progress: dict[str, int] = {node_info[0]: 0 for node_info in quotas}

    def set(self, node_id: str, progress: int):
        self.progress[node_id] = progress

    def add(self, node_id: str, count: int):
        self.progress[node_id] += count

    def get(self) -> Tuple[dict[str, int], dict[str, int]]:
        return self.progress, self.totals
