import matplotlib.pyplot as plt

from ..Types import *

from .WCParameters import *


class WCNeuralField(WCParamaters):

    def __init__(
            self,
            grid_size: Tuple[int, int] = (28, 28),
            P: NpVector = None,
            Q: NpVector = None,
            E0: NpVector = None,
            I0: NpVector = None,
            scheme: Scheme | str = "euler",
            **kwargs
    ):
        self.grid_size: Tuple[int, int] = grid_size

        self.grid_coordinates: Tuple[NpVector, ...] = tuple(
            axis.reshape(-1).astype(np.float32)
            for axis in np.meshgrid(
                np.arange(self.grid_size[0]),
                np.arange(self.grid_size[1]),
                indexing="ij",
            )
        )

        self.N: int = self.grid_size[0] * self.grid_size[1]

        self.P: NpVector = (np.full(self.N, self.P0) if P is None else P).astype(np.float32)
        self.Q: NpVector = (np.full(self.N, self.Q0) if Q is None else Q).astype(np.float32)

        self.E0: NpVector = (np.zeros(self.N) if E0 is None else E0).astype(np.float32)
        self.I0: NpVector = (np.zeros(self.N) if I0 is None else I0).astype(np.float32)

        self.W: ConnectivityMatrix = {
            "EE": self.kernel_weight_matrix(self.sigma_EE, self.strength_EE),
            "EI": self.kernel_weight_matrix(self.sigma_EI, self.strength_EI),
            "IE": self.kernel_weight_matrix(self.sigma_IE, self.strength_IE),
            "II": self.kernel_weight_matrix(self.sigma_II, self.strength_II),
        }

        self.scheme: Scheme = scheme or self.runge_kutta4
        if type(scheme) is str:
            self.scheme: Scheme = getattr(self, scheme) if hasattr(self, scheme) else self.runge_kutta4

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def gaussian_kernel(distances_squared: NpVector, sigma: float) -> NpVector:
        """
        The base gaussian kernel - controls how quickly the local connectivity between neurons drops off.
        """
        return np.exp(-distances_squared / (2.0 * (sigma ** 2))).astype(np.float32)

    @staticmethod
    def mexican_hat_kernel(distances_squared: NpVector, sigma: float) -> NpVector:
        """
        The Mexican hat kernel - implements local excitation with a surrounding inhibitory area.
        """
        return (1 - (distances_squared / (sigma ** 2))).astype(np.float32)

    def plot_kernel(self, fname: str = "kernel_plot"):
        """
        Display each of kernel in the grid space.
        """
        kernels: List[Tuple[str, NpVector]] = list(self.W.items())
        total_kernels: int = len(kernels)

        rows: int
        columns: int

        square_root: float = math.sqrt(total_kernels)
        if square_root == math.floor(square_root):
            rows = columns = int(square_root)
        else:
            columns = min(3, total_kernels)
            rows = int(np.ceil(total_kernels / columns))

        mid_point: int = (self.grid_size[0] // 2) * self.grid_size[1] + (self.grid_size[1] // 2)

        figure: plt.Figure
        axes: np.ndarray
        figure, axes = plt.subplots(rows, columns, figsize=(4 * columns, 4 * rows), constrained_layout=True)
        axes = np.atleast_2d(axes)

        kernel_index: int
        kernel_name: str
        kernel_values: NpVector
        for kernel_index, (kernel_name, kernel_values) in enumerate(kernels):
            axis: plt.Axes = axes[kernel_index // columns, kernel_index % columns]

            kernel_image: plt.AxesImage = axis.imshow(
                kernel_values[mid_point].reshape(self.grid_size),
                cmap="magma",
                origin="lower",
            )

            axis.set_title(f"Kernal for $W_{{{kernel_name}}}$")
            axis.axis('off')

            figure.colorbar(kernel_image, ax=axis, fraction=0.05, pad=0.04)

        figure.suptitle("Plots of each kernel", fontsize=18)
        figure.savefig(f"{fname}.png", dpi=150)
        plt.close(figure)

    def plot_kernel_3d(self, resolution: int = 4, fname: str = "kernel_plot_3d"):
        """
        Display each of kernel in the grid space with Z representing strength of connection.
        """
        kernels: List[Tuple[str, NpVector]] = list(self.W.items())
        total_kernels: int = len(kernels)

        rows: int
        columns: int

        square_root: float = math.sqrt(total_kernels)
        if square_root == math.floor(square_root):
            rows = columns = int(square_root)
        else:
            columns = min(3, total_kernels)
            rows = int(np.ceil(total_kernels / columns))

        t: NpVector = np.linspace(-10, 10, 200).astype(np.float32)

        X: NpVector
        Y: NpVector
        X, Y = np.meshgrid(t, t)

        distances_squared: NpVector = X ** 2 + Y ** 2

        figure: plt.Figure = plt.figure(figsize=(4 * columns, 4 * rows), constrained_layout=True)

        kernel_index: int
        kernel_name: str
        kernel_values: NpVector
        for kernel_index, (kernel_name, kernel_values) in enumerate(kernels):
            axis = figure.add_subplot(rows, columns, kernel_index + 1, projection="3d")

            sigma: float = getattr(self, f"sigma_{kernel_name}")

            Z: NpVector = (
                self.mexican_hat_kernel(distances_squared, sigma)
                    * self.gaussian_kernel(distances_squared, sigma)
            ).astype(np.float32)
            Z /= np.max(
                np.abs(Z)
            )

            axis.plot_surface(
                X,
                Y,
                Z,
                cmap="magma",
                edgecolor="none",
            )

            axis.set_title(f"Kernal for $W_{{{kernel_name}}}$")
            axis.axis('off')

        figure.suptitle("Plots of each kernel", fontsize=18)
        figure.savefig(f"{fname}.png", dpi=150)
        plt.close(figure)

    def phi(self, u: NpVector) -> NpVector:
        """
        The sigmoid activation function, φ, converts input potential into population firing rate.
        """
        u: NpVector = np.clip(-self.beta * (u - self.theta), -60, 60)
        return (
            1 / (1 + np.exp(u))
        ).astype(np.float32)

    def get_pairwise_periodic_distance_squared(self, x: NpVector, y: NpVector) -> NpVector:
        """
        Compute the squared distance between every pair of coordinates
        (tells you how far each neuron is from every other one).
        """
        dx: NpVector = np.abs(x.reshape(self.N, 1) - x.reshape(1, self.N))
        dy: NpVector = np.abs(y.reshape(self.N, 1) - y.reshape(1, self.N))
        if self.periodic:  # If it is periodic we need to wrap around.
            dx = np.minimum(dx, self.grid_size[0] - dx).astype(np.float32)
            dy = np.minimum(dy, self.grid_size[1] - dy).astype(np.float32)
        return dx ** 2 + dy ** 2

    def kernel_weight_matrix(self, sigma: float, strength: float) -> NpVector:
        """
        Build a connectivity matrix where entries decrease with distance.

        Nearby neurons become strongly connected and far ones less so. sigma
        controls how quickly the connection falls off with distance using a
        "mexican hat" kernel. strength controls the effect inputs have on neurons.
        """
        distances_squared: NpVector = self.get_pairwise_periodic_distance_squared(*self.grid_coordinates)
        return (
                self.mexican_hat_kernel(distances_squared, sigma)
                    * self.gaussian_kernel(distances_squared, sigma)
                        * strength
        ).astype(np.float32)

        # Commented out because this destroys the theoretical WC model kernel
        # and removes its absolute amplitude of the spatial coupling.
        # row_sums: NpVector = gaussian.sum(axis=1, keepdims=True)
        # row_sums[row_sums == 0] = 1.0
        # return ((gaussian / row_sums) * strength).astype(np.float32)

        return (gaussian * strength).astype(np.float32)

    def rhs(self, E: NpVector, I: NpVector, Q: NpVector) -> Tuple[NpVector, NpVector]:
        """
        Evaluates the RHS of the Wilson-Cowan neural-field ODEs by
        computing the net input to the E and I-populations and then
        applies a sigmoid function to both.
        """
        input_E: NpVector = E @ self.W["EE"].T - I @ self.W["EI"].T + self.P  # In this format for batching.
        input_I: NpVector = E @ self.W["IE"].T - I @ self.W["II"].T + Q
        return (-E + self.phi(input_E)) / self.tau_E, (-I + self.phi(input_I)) / self.tau_I

    def runge_kutta4(self, E: NpVector, I: NpVector, Q: NpVector) -> Tuple[NpVector, NpVector]:
        """
        Take one time step using the RK4 scheme.
        """
        k1_E: NpVector
        k1_I: NpVector
        k1_E, k1_I = self.rhs(E, I, Q)

        k2_E: NpVector
        k2_I: NpVector
        k2_E, k2_I = self.rhs(
            (E + 0.5 * self.dt * k1_E).astype(np.float32),
            (I + 0.5 * self.dt * k1_I).astype(np.float32),
            Q
        )

        k3_E: NpVector
        k3_I: NpVector
        k3_E, k3_I = self.rhs(
            (E + 0.5 * self.dt * k2_E).astype(np.float32),
            (I + 0.5 * self.dt * k2_I).astype(np.float32),
            Q
        )

        k4_E: NpVector
        k4_I: NpVector
        k4_E, k4_I = self.rhs(
            (E + self.dt * k3_E).astype(np.float32),
            (I + self.dt * k3_I).astype(np.float32),
            Q
        )

        return (
            (E + (self.dt / 6.0) * (k1_E + 2 * k2_E + 2 * k3_E + k4_E)).astype(np.float32),
            (I + (self.dt / 6.0) * (k1_I + 2 * k2_I + 2 * k3_I + k4_I)).astype(np.float32)
        )

    def euler(self, E: NpVector, I: NpVector, Q: NpVector) -> Tuple[NpVector, NpVector]:
        """
        One time step of the Euler scheme (~5x faster than RK4).
        """
        dE: NpVector
        dI: NpVector
        dE, dI = self.rhs(E, I, Q)

        E += self.dt * dE
        I += self.dt * dI

        return E.astype(np.float32), I.astype(np.float32)

    def simulate(self, n_snapshots: int = 10) -> SimulationSnapshots:
        """
        Integrate from t=0 to t=total_time storing the values of E and I
        throughout, snapshotting their values at time intervals calculated
        from the count of snapshots set.
        """

        steps: int = int(self.total_time / self.dt)

        shape: Tuple[int, Any] = self.P.shape if self.P.ndim >= 2 else (1, 0)
        batch_size, _ = shape

        E: NpVector = np.repeat(self.E0[None, :], batch_size, axis=0).astype(np.float32)
        I: NpVector = np.repeat(self.I0[None, :], batch_size, axis=0).astype(np.float32)

        Q: NpVector = np.repeat(self.Q[None, :], batch_size, axis=0).astype(np.float32)

        snap_indices: List[int] = list(np.linspace(0, steps, n_snapshots, dtype=int))

        snapshots_E: List[NpVector] = [E]
        snapshots_I: List[NpVector] = [I]

        step: int
        for step in range(0, steps):
            E, I = self.scheme(E, I, Q)

            if step in snap_indices and len(snapshots_E) < n_snapshots:
                snapshots_E.append(E)
                snapshots_I.append(I)

        return {
            "snapshots_E": snapshots_E,
            "snapshots_I": snapshots_I,
            "snapshot_times": snap_indices,
            "E_final": E.copy(),
            "I_final": I.copy(),
        }

    def simulate_with_no_snapshots(self) -> Tuple[NpVector, NpVector]:
        """
        Integrate from t=0 to t=total_time returning the final value of E.
        """

        steps: int = int(self.total_time / self.dt)

        shape: Tuple[int, Any] = self.P.shape if self.P.ndim >= 2 else (1, 0)
        batch_size, _ = shape

        E: NpVector = np.repeat(self.E0[None, :], batch_size, axis=0).astype(np.float32)
        I: NpVector = np.repeat(self.I0[None, :], batch_size, axis=0).astype(np.float32)

        Q: NpVector = np.repeat(self.Q[None, :], batch_size, axis=0).astype(np.float32)

        for _ in range(steps):
            E, I = self.scheme(E, I, Q)

        return E.copy(), I.copy()

    def plot_snapshots(self, snapshots: List[NpVector], snap_times: List[float], title_prefix: str, fname: str):
        """
        Plot vectors as heatmaps to visualise neuron activity.
        """

        total_snapshots: int = len(snapshots)

        rows: int
        columns: int

        square_root: float = math.sqrt(total_snapshots)
        if square_root == math.floor(square_root):
            rows = columns = int(square_root)
        else:
            columns = min(3, total_snapshots)
            rows = int(np.ceil(total_snapshots / columns))

        snapshot: NpVector
        miniumum: float = min(
            snapshot.min() for snapshot in snapshots
        )
        maxiumum: float = max(
            snapshot.max() for snapshot in snapshots
        )

        figure: plt.Figure
        axes: np.ndarray
        figure, axes = plt.subplots(rows, columns, figsize=(4 * columns, 4 * rows), constrained_layout=True)
        axes = np.atleast_2d(axes)

        snapshot: int
        for snapshot in range(total_snapshots):
            axis: plt.Axes = axes[snapshot // columns, snapshot % columns]

            image: plt.AxesImage = axis.imshow(
                snapshots[snapshot][::-1, :].reshape(self.grid_size),
                cmap="magma",
                origin="lower",
                vmin=miniumum,
                vmax=maxiumum,
            )

            axis.set_title(f"{title_prefix} at t={snap_times[snapshot]:0.1f}")
            axis.set_xlabel("x (grid)")
            axis.set_ylabel("y (grid)")

            figure.colorbar(image, ax=axis, fraction=0.05, pad=0.04)

        for snapshot in range(total_snapshots, rows * columns):  # Hide empty plots.
            axes[snapshot // columns, snapshot % columns].axis('off')

        figure.suptitle(f"{title_prefix} snapshots", fontsize=18)
        figure.savefig(f"{fname}.png", dpi=150)
        plt.close(figure)

    @staticmethod
    def plot_timeseries(
            E_snapshots: List[NpVector],
            I_snapshots: List[NpVector],
            times: List[float],
            indices: List[int],
            fname: str
    ):
        """
        Plot the activity of selected neurons/nodes (by index) changes over time.
        """

        total_snapshots = len(E_snapshots)
        t: NpVector = np.array(times).astype(np.float32)

        figure: plt.Figure
        axes: Tuple[plt.Axes, plt.Axes]
        figure, axes = plt.subplots(2, 1, sharex=True, constrained_layout=False)

        excitatory_plot: plt.Axes
        inhibitory_plot: plt.Axes
        excitatory_plot, inhibitory_plot = axes

        index: int
        for index in indices:
            excitatory_plot.plot(
                t,
                np.array(
                    [
                        E_snapshots[timestep][0][index] for timestep in range(total_snapshots)
                    ]
                )
            )
            inhibitory_plot.plot(
                t,
                np.array(
                    [
                        I_snapshots[timestep][0][index] for timestep in range(total_snapshots)
                    ]
                )
            )

        excitatory_plot.set_ylabel("E activity")
        inhibitory_plot.set_ylabel("I activity")
        inhibitory_plot.set_xlabel("time")

        figure.suptitle("Activity of neurons", fontsize=18)
        figure.savefig(f"{fname}.png", dpi=150)
        plt.close(figure)

    def parameter_sweep_sigma(self, sigmas: List[float], fname: str):
        """
        Plots heatmaps of the final iteration varying the local connectivity to show its affects on the outcome.
        """

        total_sigmas: int = len(sigmas)

        figures: List[Tuple[str, plt.Figure]] = []
        axes: List[np.ndarray[plt.Axes] | plt.Axes] = []

        axis: np.ndarray[plt.Axes] | plt.Axes
        figure: plt.Figure
        figure_name: str
        for figure_name, figure, axis in [
            (
                    "E",
                    *plt.subplots(
                        4,
                        total_sigmas,
                        figsize=(4 * total_sigmas, 16),
                        constrained_layout=True
                    )
            ),
            (
                    "I",
                    *plt.subplots(
                        4,
                        total_sigmas,
                        figsize=(4 * total_sigmas, 16),
                        constrained_layout=True
                    )
            ),
        ]:
            figures.append((figure_name, figure))
            axes.append(axis)

        modified_neural_field: WCNeuralField = WCNeuralField(self.grid_size)

        weight_index: int
        for weight_index, weighting in enumerate(["EE", "EI", "IE", "II"]):
            index: int
            sigma: float
            for index, sigma in enumerate(sigmas):
                modified_W: ConnectivityMatrix = self.W.copy()
                modified_W[weighting] = self.kernel_weight_matrix(sigma, getattr(self, f'strength_{weighting}'))

                modified_neural_field.W = modified_W

                figure_index: int
                final_image: NpVector
                for figure_index, final_image in enumerate(modified_neural_field.simulate_with_no_snapshots()):
                    axis: plt.Axes = axes[figure_index][weight_index, index]

                    F_normalised: NpVector = (
                            (final_image - final_image.min()) /
                            (final_image.max() - final_image.min() + 1e-12)
                    )
                    image: plt.AxesImage = axis.imshow(
                        F_normalised[::-1, :].reshape(self.grid_size),
                        vmin=0,
                        vmax=1,
                        cmap="magma",
                        origin="lower",
                    )

                    axis.set_title(f"$\\sigma_{{{weighting}}}={sigma}$")
                    axis.set_xlabel("x")
                    axis.set_ylabel("y")

                    figures[figure_index][1].colorbar(image, ax=axis, fraction=0.05, pad=0.04)

        figure: plt.Figure
        figure_name: str
        for (figure_name, figure) in figures:
            figure.suptitle(f"Parameter sweep: effect of $\\sigma$ on {figure_name}", fontsize=18)
            figure.savefig(f"{fname}_{figure_name}.png", dpi=150)
            plt.close(figure)

    def test(self, sigmas: List[float] = (0.8, 1.2, 1.8, 2.5), n_snapshots: int = 4):
        """
        Simple test function to produce snapshots, timeseries, and a parameter sweep of a particular system.
        """

        print("Simulating...")
        output: SimulationSnapshots = self.simulate(
            n_snapshots=n_snapshots,
        )

        print("Plotting kernel...")
        self.plot_kernel()
        self.plot_kernel_3d()

        print("Plotting snapshots...")
        self.plot_snapshots(
            output['snapshots_E'], output['snapshot_times'],
            title_prefix='E', fname='E_snapshots'
        )
        self.plot_snapshots(
            output['snapshots_I'], output['snapshot_times'],
            title_prefix='I', fname='I_snapshots'
        )

        print("Plotting timeseries...")
        all_indicies: List[int] = list(range(0, (self.grid_size[0] * self.grid_size[1]) - 1))
        self.plot_timeseries(
            output['snapshots_E'], output['snapshots_I'],
            output['snapshot_times'],
            indices=all_indicies, fname='timeseries'
        )

        print("Performing parameter sweep...")
        self.parameter_sweep_sigma(
            sigmas=sigmas,
            fname=f"parameter_sweep_sigma"
        )
