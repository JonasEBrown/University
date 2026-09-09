from .RayTypes import *

from ..MNIST import *
from .ProgressActor import *
from ..Classifiers import *


class RayOrchestrator:

    def __init__(self, mnist_field: MNISTNeuralField, max_image_range: int = 60000, percentage_limitation: float = 1):
        self.softmax: SoftmaxClassifier | None = None
        self.mnist_field: MNISTNeuralField = mnist_field

        self.max_image_range: int = max_image_range
        self.percentage_limitation: float = percentage_limitation

        self.nodes: List[NodeState] = []
        self.node_data: List[NodeData] = []

        self.total_cpus: float = 0.0

        self.quotas: List[NodeQuota] = []
        self.progress_actor: ProgressActor | None = None

    @staticmethod
    @ray.remote
    def process_range(
            node_id: str,
            mnist_field: MNISTNeuralField,
            data_range: Tuple[int, int],
            progress_actor: ProgressActor
    ) -> Tuple[Tuple[int, int], Tuple[NpVector, NpVector]]:
        """
        The process to run on each remote individually (so a different range of data is processed by each remote).
        """
        return (
            data_range,
            mnist_field.run_analysis(
                data_range=data_range,
                debugger=(node_id, progress_actor)
            )
        )

    def print_mnist_neural_field_data(self):
        """
        Output the stats of the MNIST neural field.
        """
        print(
            f"""Analysis
        Scales: {', '.join([str(scale) for scale in self.mnist_field.scales])}
        Layers: {len(self.mnist_field.layers)}
        {'\n\n\t'.join([
                f"""    Layer {index + 1}:
                strength_EE: {layer.strength_EE:0.2f} strength_EE: {layer.strength_EI:0.2f} strength_IE: {layer.strength_IE:0.2f} strength_II: {layer.strength_II:0.2f}
                sigma_EE: {layer.sigma_EE:0.2f} sigma_EI: {layer.sigma_EI:0.2f} sigma_IE: {layer.sigma_IE:0.2f} sigma_II: {layer.sigma_II:0.2f}
                beta: {layer.beta:0.2f} theta: {layer.theta:0.2f} dt: {layer.dt:0.03f} total_time: {layer.total_time:0.03f}"""
                for index, layer in enumerate(self.mnist_field.layers)
            ])} 
        Total images: {self.max_image_range}
            """
        )

    def print_cluster_info(self):
        """
        Outputs the cluster info.
        """
        [print(
            f"""Node {node_id[:6]}:
        IP: {ip} {"(host)" if is_host else ""}
        CPUS: {cpus} cores
        Allocated images: {allocated_amount}/{self.max_image_range} {allocated_amount * 100 / self.max_image_range:0.2f}%
            """
        ) for (node_id, ip, cpus, allocated_amount, is_host) in self.quotas]

    def run(self):
        """
        Uses the ray library to orchestrate remote machines (in my case my friend's servers), allowing for faster
        analysis of the dataset by breaking data into shards (ranges for each machine). Finally, concatenating all
        the collected data into one big file of features that can be used to train a classifier.
        """
        ray.init(
            address="auto",
            runtime_env={
                "working_dir": ".",
                "excludes": [
                    "prometheus-3.10.0.linux-amd64.tar.gz",
                    "prometheus-3.10.0.linux-amd64/",
                    "*.npz",
                ],
            },
        )

        # Split the shards depending on the CPU count on the machine.

        self.nodes: List[NodeState] = list_nodes()
        self.node_data: List[NodeData] = []

        node: NodeState
        for node in self.nodes:
            if node.get("state", "DEAD").upper() == "ALIVE":
                node_resources = (node.get("resources_total") or node.get("resources") or {})
                self.node_data.append((
                    node["node_id"],
                    node["node_ip"],
                    round(float(node_resources.get("CPU", 0.0)) * self.percentage_limitation, 2),
                    "node:__internal_head__" in node_resources,
                ))

        self.total_cpus: float = sum(node_info[2] for node_info in self.node_data)

        self.quotas: List[NodeQuota] = [
            (
                node_id,
                ip,
                int(
                    math.ceil(cpus)
                ),
                int(
                    math.ceil(
                        (cpus / self.total_cpus) * self.max_image_range
                    )
                ),
                is_host
            ) for (node_id, ip, cpus, is_host) in self.node_data
        ]
        self.progress_actor = ProgressActor.remote(quotas=self.quotas)

        print("\n" + "=" * 100 + "\n")
        self.print_mnist_neural_field_data()
        print("\n" + "=" * 100 + "\n")
        self.print_cluster_info()
        print("=" * 100 + "\n")

        # Submit a task per shard.

        index: int = 0
        futures: List[Any] = []
        for (node_id, _, cpus, allocated_amount, _) in self.quotas:
            task_amount: int = int(
                math.ceil(allocated_amount / cpus)
            )
            for _ in range(cpus):
                futures.append(
                    self.process_range.options(
                        scheduling_strategy=NodeAffinitySchedulingStrategy(node_id=node_id, soft=True),
                        num_cpus=1,
                    ).remote(
                        node_id=node_id,
                        data_range=(
                            index,
                            min(
                                index + task_amount,
                                self.max_image_range,
                            ),
                        ),
                        mnist_field=self.mnist_field,
                        progress_actor=self.progress_actor,
                    )
                )
                index += task_amount

        node_bars: dict[str, tqdm] = {}
        node_last_values: dict[str, int] = {}

        total_complete: int = 0
        while total_complete < self.max_image_range:
            total_complete = 0

            totals: dict[str, int]
            progress: dict[str, int]
            progress, totals = ray.get(
                self.progress_actor.get.remote()
            )

            index: int
            node_id: str
            node_progress: int
            for index, (node_id, node_progress) in enumerate(progress.items()):
                if node_id not in node_bars:
                    node_bars[node_id] = tqdm(
                        total=totals[node_id],
                        position=index,
                        desc=f"Node {node_id[:6]}"
                    )
                    node_last_values[node_id] = 0

                node_bars[node_id].update(
                    node_progress - node_last_values[node_id]
                )
                node_last_values[node_id] = node_progress

                total_complete += node_progress

            time.sleep(0.5)

        totals: dict[str, int]
        _, totals = ray.get(self.progress_actor.get.remote())

        for (node_id, bar) in node_bars.items():
            bar.update(
                totals[node_id] - node_last_values[node_id]
            )
            bar.close()

        time.sleep(1)
        print("\n" + "=" * 100 + "\n")

        # Gather all results.

        results: List[
            Tuple[Tuple[int, int], Tuple[NpVector, NpVector]]
        ] = ray.get(futures)
        results.sort(key=lambda result: result[0])  # Sort by batch's data range -> [(0..30000),(30000,60000)]

        print(f"Received {len(futures)} results.")

        dimension: int = int(results[0][1][0].shape[1])

        merged_features: NpVector = np.zeros((self.max_image_range, dimension)).astype(np.float32)
        merged_labels: NpVector = np.zeros((self.max_image_range,)).astype(np.float32)

        position: int = 0
        for (start, end), (features, labels) in results:
            size: int = end - start
            merged_features[position:position + size] = features
            merged_labels[position:position + size] = labels
            position += size

        fname: str = f"(layers-{len(self.mnist_field.layers)}&scales-{'-'.join([str(scale) for scale in self.mnist_field.scales])})feature_analysis.npz"
        self.mnist_field.save(fname, features=merged_features, labels=merged_labels)

        del results
        del merged_features
        del merged_labels
        ray.shutdown()

        # Softmax Classifier.

        print("\n" + "=" * 100 + "\n")

        self.softmax: SoftmaxClassifier = SoftmaxClassifier(
            self.mnist_field,
            max_images=self.max_image_range,
        )

        self.softmax.train()
