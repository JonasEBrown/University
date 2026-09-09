from ..Types import *

from .MNISTDataset import *
from ..WilsonCowan import *


class MNISTNeuralField(MNISTDataset):

    def __init__(self, layers: List[WCNeuralField] | None = None, scales: List[int] = (2, 4)):
        super().__init__()

        self.image_size: int = self.training_data[0].shape[0]
        self.image_width: int = int(math.sqrt(self.image_size))
        self.training_data_size: int = self.training_data[0].shape[1]
        self.test_data_size: int = self.test_data[0].shape[1]

        self.scales: List[int] = scales
        self.scale_factor: int = 3

        self.saved: bool = False

        self.layers: List[WCNeuralField] = [
                                               WCNeuralField(
                                                   grid_size=(self.image_width, self.image_width),
                                               )
                                           ] or layers

    def analyse(self, data: NpVector) -> NpVector:
        """
        Breaks data into smaller images and converts the image data into usable "features"
        (essentially a vectorised format of the statistical data of the image).
        Features of each block include the mean, variance, maximum, and minimum.
        """
        vmin: float = data.min()
        vmax: float = data.max()
        normalised_data: NpVector = (data - vmin) / (vmax - vmin + 1e-12)

        image: NpVector = normalised_data.reshape(self.image_width, self.image_width).astype(np.float32)

        gradient_x: NpVector = np.zeros_like(image)
        gradient_y: NpVector = np.zeros_like(image)

        gradient_x[:, 1:-1] = (image[:, 2:] - image[:, :-2]) * 0.5
        gradient_y[1:-1, :] = (image[2:, :] - image[:-2, :]) * 0.5

        scale: int
        features: List[NpVector] = []
        for scale in self.scales:
            scaled_width: int = self.image_width // scale
            block: NpVector = (image[:scaled_width * scale, :scaled_width * scale]
                               .reshape(scaled_width, scale, scaled_width, scale)).astype(np.float32)

            local_x: NpVector
            local_y: NpVector
            coords: NpVector = np.linspace(-1, 1, scale).astype(np.float32)
            local_y, local_x = np.meshgrid(coords, coords, indexing="ij")

            local_x = local_x.reshape(1, scale, 1, scale)
            local_y = local_y.reshape(1, scale, 1, scale)

            mean_block: NpVector = block.mean(axis=(1, 3)) + 1e-6

            gradient_x_block: NpVector = (gradient_x[:scaled_width * scale, :scaled_width * scale]
                                          .reshape(scaled_width, scale, scaled_width, scale)).astype(np.float32)
            gradient_y_block: NpVector = (gradient_y[:scaled_width * scale, :scaled_width * scale]
                                          .reshape(scaled_width, scale, scaled_width, scale)).astype(np.float32)

            features.extend([
                # Mean, variance, and maximum (very basic features).
                # Intensity / texture.
                mean_block.ravel(),
                block.var(axis=(1, 3)).ravel(),
                block.max(axis=(1, 3)).ravel(),

                # Positional descriptors of intensity within the block.
                ((block * local_x).mean(axis=(1, 3)) / mean_block).ravel(),
                ((block * local_y).mean(axis=(1, 3)) / mean_block).ravel(),

                # Edge strength.
                np.abs(gradient_x_block).mean(axis=(1, 3)).ravel(),
                np.abs(gradient_y_block).mean(axis=(1, 3)).ravel(),

                # Edge direction.
                gradient_x_block.mean(axis=(1, 3)).ravel(),
                gradient_y_block.mean(axis=(1, 3)).ravel(),

                # Diagonals.
                (gradient_x_block + gradient_y_block).mean(axis=(1, 3)).ravel(),
                (gradient_x_block - gradient_y_block).mean(axis=(1, 3)).ravel(),

                # Curvature to help identify 5's and 9's.
                np.mean(
                    ((gradient_x_block**2) * (gradient_y_block **2))
                        - (gradient_x_block * gradient_y_block)**2
                ).ravel()
            ])
        return np.concatenate(features, axis=0).astype(np.float32)

    # def analyse_batched(self, batch: NpVector) -> NpVector:
    #     vmin = batch.min(axis=1, keepdims=True)
    #     vmax = batch.max(axis=1, keepdims=True)
    #     normalised_data = (batch - vmin) / (vmax - vmin + 1e-12)
    #
    #     batch_size, N = batch.shape
    #     image: NpVector = normalised_data.reshape(batch_size, self.image_width, self.image_width).astype(np.float32)
    #
    #     gradient_x: NpVector = np.zeros_like(image)
    #     gradient_y: NpVector = np.zeros_like(image)
    #
    #     gradient_x[:, :, 1:-1] = (image[:, :, 2:] - image[:, :, :-2]) * 0.5
    #     gradient_y[:, 1:-1, :] = (image[:, 2:, :] - image[:, :-2, :]) * 0.5
    #
    #     scale: int
    #     features: List[NpVector] = []
    #     for scale in self.scales:
    #         scaled_width: int = self.image_width // scale
    #         block: NpVector = (
    #             image[:, :scaled_width * scale, :scaled_width * scale]
    #                 .reshape(batch_size, scaled_width, scale, scaled_width, scale)
    #         ).astype(np.float32)
    #
    #         local_x: NpVector
    #         local_y: NpVector
    #         coords: NpVector = np.linspace(-1, 1, scale).astype(np.float32)
    #         local_y, local_x = np.meshgrid(coords, coords, indexing="ij")
    #
    #         local_x = local_x.reshape(1, 1, scale, 1, scale)
    #         local_y = local_y.reshape(1, 1, scale, 1, scale)
    #
    #         mean_block: NpVector = block.mean(axis=(2, 4)) + 1e-6
    #
    #         gradient_x_block: NpVector = (gradient_x[:, :scaled_width * scale, :scaled_width * scale]
    #                                       .reshape(batch_size, scaled_width, scale, scaled_width, scale)).astype(np.float32)
    #         gradient_y_block: NpVector = (gradient_y[:, :scaled_width * scale, :scaled_width * scale]
    #                                       .reshape(batch_size, scaled_width, scale, scaled_width, scale)).astype(np.float32)
    #
    #         features.append(
    #             np.concatenate(
    #                 [
    #                     # Mean, variance, and maximum (very basic features).
    #                     # Intensity / texture.
    #                     mean_block.reshape(batch_size, -1),
    #                     block.var(axis=(2, 4)).reshape(batch_size, -1),
    #                     block.max(axis=(2, 4)).reshape(batch_size, -1),
    #
    #                     # Positional descriptors of intensity within the block.
    #                     ((block * local_x).mean(axis=(2, 4)) / mean_block).reshape(batch_size, -1),
    #                     ((block * local_y).mean(axis=(2, 4)) / mean_block).reshape(batch_size, -1),
    #
    #                     # Edge strength.
    #                     np.abs(gradient_x_block).mean(axis=(2, 4)).reshape(batch_size, -1),
    #                     np.abs(gradient_y_block).mean(axis=(2, 4)).reshape(batch_size, -1),
    #
    #                     # Edge direction.
    #                     gradient_x_block.mean(axis=(2, 4)).reshape(batch_size, -1),
    #                     gradient_y_block.mean(axis=(2, 4)).reshape(batch_size, -1),
    #
    #                     # Diagonals.
    #                     (gradient_x_block + gradient_y_block).mean(axis=(2, 4)).reshape(batch_size, -1),
    #                     (gradient_x_block - gradient_y_block).mean(axis=(2, 4)).reshape(batch_size, -1),
    #
    #                     # Curvature to help identify 5's and 9's.
    #                     np.mean(
    #                         ((gradient_x_block ** 2) * (gradient_y_block ** 2))
    #                         - (gradient_x_block * gradient_y_block) ** 2,
    #                         axis=(2, 4),
    #                     ).reshape(batch_size, -1)
    #                 ],
    #             ).astype(np.float32)
    #         )
    #     return np.concatenate(features, axis=1).astype(np.float32)


    def run_simulation(self, images: NpVector) -> NpVector:
        """
        Takes an array of images and runs them through the Wilson-Cowan neural field and then returns the analysed
        features from them.
        """
        P_batch: NpVector = (images.reshape(images.shape[0], -1) * self.scale_factor).astype(np.float32)

        layer: WCNeuralField
        layer_features: List[NpVector] = []
        for layer in self.layers:
            layer.P = P_batch

            batch_results: Tuple[NpVector, NpVector] = layer.simulate_with_no_snapshots()
            E_batch, I_batch = batch_results

            P_batch = 0.5 * (E_batch + I_batch)

        # An attempt to implement batched analysis, but running out of time so have to leave it here.

        #     features_E: NpVector = self.analyse_batched(E_batch)
        #     features_I: NpVector = self.analyse_batched(I_batch)
        #
        #     print("E_batch shape:", E_batch.shape)
        #     print("features_E shape:", features_E.shape)
        #     print("features_I shape:", features_I.shape)
        #
        #     layer_features.append(
        #         np.concatenate(
        #             [
        #                 features_E,
        #                 features_I,
        #             ],
        #             axis=1,
        #         ).astype(np.float32)
        #     )
        # return np.concatenate(layer_features, axis=1).astype(np.float32)

            E: NpVector
            index: int
            batch_features: List[NpVector] = []
            for index, E in enumerate(E_batch):
                features_E = self.analyse(E)
                features_I = self.analyse(I_batch[index])
                batch_features.append(
                    np.concatenate([features_E, features_I]).astype(np.float32)
                )
            layer_features.append(
                np.array(batch_features).astype(np.float32)
            )
        return np.concatenate(layer_features, axis=1).astype(np.float32)

    def run_analysis(
            self,
            data_range: Tuple[int, int] = (0, 60000),
            fname: str = "feature_analysis.npz",
            batch_size: int = 100,
            debugger: Tuple[str | None, Any | None] = (None, None)
    ) -> Tuple[NpVector, NpVector]:
        """
        Runs the images indexed between the data_range variable in batches through a simulation and saves all the features
        to a file.
        """
        node_id: str
        node_id, progess_actor = debugger

        print_function: Callable[[...], ...] = (lambda _: None) if node_id is not None else print

        features: NpVector = np.array([]).astype(np.float32)
        labels: NpVector = np.array([]).astype(np.float32)

        new_fname: str = f"(layers-{len(self.layers)}&scales-{'-'.join([str(scale) for scale in self.scales])}){fname}"
        if os.path.isfile(new_fname): print_function(f"Loading previous analysis file {new_fname}...")

        data: dict | None = self.load(new_fname)
        if data is not None:
            features = data["features"]
            labels = data["labels"]

        min_images, max_images = data_range
        total_images: int = max_images - min_images

        currentIndex: int = features.shape[0]
        if max_images <= (min_images + currentIndex):
            print_function(f"Analysis already completed.")
            return features.astype(np.float32), labels.astype(np.int64)

        print_function(f"\nLayers: {len(self.layers)}\nScales: {'-'.join([str(scale) for scale in self.scales])}\n")
        print_function(
            f"Starting analysis... {
                f"(Resuming from {min_images + currentIndex})" if (min_images + currentIndex) > 0 else ""
            }")

        self.saved = False

        def save(_, __):
            if not self.saved:
                print_function("Saving... (DO NOT QUIT!)")
                self.save(new_fname, features=features, labels=labels)
                print_function(f"Saved to {fname}\n")
                self.saved = True

        save = lambda _, __: None if self.saved else self.save(new_fname, features=features, labels=labels)
        signal.signal(signal.SIGINT, save)
        signal.signal(signal.SIGTERM, save)

        try:
            lastTime: float = time.time()
            times: List[float] = [0] * 10

            index: int
            for index in range(min_images + currentIndex, max_images, batch_size):
                if self.saved: raise SystemExit("File saved, quitting program now...")

                end: int = min(index + batch_size, max_images)

                feature_rows: NpVector = self.run_simulation(
                    images=self.training_data[0][:, index:end]
                    .T.reshape(-1, self.image_width, self.image_width)
                )
                labels: NpVector = np.concatenate([
                    labels,
                    self.training_data[1][index:end, 0]
                ]).astype(np.int64)

                features = feature_rows if features.size == 0 else np.concatenate([features, feature_rows],
                                                                                  axis=0).astype(np.float32)

                current_image: int = index - min_images

                if node_id is None:
                    if self.saved: raise SystemExit("File saved, quitting program now...")

                    nowTime: float = time.time()
                    timeElapsed: float = (nowTime - lastTime)
                    lastTime = nowTime

                    del times[0]
                    times.append(timeElapsed)
                    averageTimeLeft: int = int(((total_images - current_image) / batch_size) * (sum(times) / len(times)))

                    print_function(
                        f"Processing... {
                        current_image * 100 / total_images:0.2f}% ({
                            current_image
                        }/{
                            total_images
                        }) time remaining: {
                            datetime.timedelta(0, averageTimeLeft)
                        }")
                else:
                    progess_actor.add.remote(node_id, current_image)
            print_function("Completed analysis.")
            if node_id is not None:
                progess_actor.set.remote(node_id, max_images)
        finally:
            if max_images > (min_images + currentIndex) and not self.saved:
                save(None, None)
        return features.astype(np.float32), labels.astype(np.int64)

    @staticmethod
    def save(fname: str, meta: dict | None = None, compressed: bool = True, **kargs):
        """
        Saves the passed kwargs to a file (so save(W=[...]) will save [...] as W in the file).
        """
        meta = {} if meta is None else dict(meta)
        saver = np.savez_compressed if compressed else np.savez
        saver(fname, **kargs, **{f"meta_{k}": v for k, v in meta.items()})

    @staticmethod
    def load(fname: str) -> dict | None:
        """
        Loads a file or returns None if it doesn't exist.
        """
        if not os.path.isfile(fname):
            return None
        return np.load(fname, allow_pickle=False)
