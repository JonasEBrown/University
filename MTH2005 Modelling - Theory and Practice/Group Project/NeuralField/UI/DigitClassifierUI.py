"""
                               ================
                               | A QUICK NOTE |
                               ================

    This is not required for the project. I suggest just using the test
    data provided with the MNIST dataset instead. It yields much
    better results from the neural field as I haven't perfected the
    "drawn digit" -> "neural field input" conversion yet.

    It's something about scaling the input, using the correct brush width,
    antialiasing, etc. than an issue with the classifier itself (it's a bit
    of a faff).

"""
from .UITypes import *

from ..Classifiers import *
from .SnapshotViewer import *


class DigitClassifierUI:

    def __init__(self, classifier: SoftmaxClassifier, colour_map: str | None = None):
        self.classifier: SoftmaxClassifier = classifier
        self.colour_map = cm.get_cmap(colour_map) if type(colour_map) is str else colour_map

        self.fast_classifier: SoftmaxClassifier = copy.deepcopy(self.classifier)

        layer: WCNeuralField
        for layer in self.fast_classifier.mnist_field.layers:
            layer.dt = 0.05
            layer.total_time = 0.70

        self.root: tkinter.Tk = tkinter.Tk()
        self.root.title("Draw a digit")

        self.font: str = "Segoe UI"
        self.pen_width: int = 6
        self.pen_colour: str = "white"
        self.mouse_down: bool = False
        self.n_snapshots: int = int(
            math.ceil(
                self.classifier.mnist_field.layers[0].total_time
                    / self.classifier.mnist_field.layers[0].dt
            )
        )
        self.image_size: int = self.classifier.mnist_field.image_width * 10
        self.last_mouse_position: Tuple[int, int] = (0, 0)

        self.canvas: tkinter.Canvas = tkinter.Canvas(
            self.root,
            width=self.image_size,
            height=self.image_size,
            bg="black",
            cursor="cross",
        )
        self.canvas.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
        )
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_button_1_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_button_1_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_button_1_move)

        self.image: PILImage.Image = PILImage.new(
            "L",
            (self.image_size, self.image_size),
            color=0,
        )
        self.drawer: PILImageDraw.ImageDraw = PILImageDraw.Draw(self.image)

        self.preview: ttk.Label = ttk.Label(self.root)
        self.preview.grid(
            row=0,
            column=5,
            columnspan=3,
            padx=6,
            pady=6,
        )
        self.update_preview_image()

        self.prediction_variable: tkinter.StringVar = tkinter.StringVar(value="Prediction: -")
        self.top_predictions_variable: tkinter.StringVar = tkinter.StringVar(value="Top 3: -")

        self.prediction_label: ttk.Label = ttk.Label(
            self.root,
            textvariable=self.prediction_variable,
            font=(self.font, 12, "bold"),
        )
        self.prediction_label.grid(
            row=1,
            column=0,
            sticky='w',
            padx=6,
        )

        self.top_predictions_label: ttk.Label = ttk.Label(
            self.root,
            textvariable=self.top_predictions_variable,
            font=(self.font, 10),
        )
        self.top_predictions_label.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky='w',
            padx=6,
        )

        self.clear_button: ttk.Button = ttk.Button(
            self.root,
            text="Clear",
            command=self.clear,
        )
        self.clear_button.grid(
            row=2,
            column=7,
            sticky="e",
            padx=6,
            pady=(0, 6),
        )

        self.snapshots_button: ttk.Button = ttk.Button(
            self.root,
            text="Snapshots",
            command=self.simulate,
        )
        self.snapshots_button.grid(
            row=1,
            column=7,
            sticky="e",
            padx=6,
        )

        self.root.mainloop()

    # noinspection PyAttributeOutsideInit
    def on_mouse_button_1_down(self, event: tkinter.Event):
        self.mouse_down = True
        self.last_mouse_position = (event.x, event.y)

    # noinspection PyAttributeOutsideInit
    def on_mouse_button_1_up(self, _):
        self.mouse_down = False
        self.predict(fast=False)

    # noinspection PyAttributeOutsideInit
    def on_mouse_button_1_move(self, event: tkinter.Event):
        if self.mouse_down:
            line_positions: Tuple[int, int, int, int] = (
                self.last_mouse_position[0],
                self.last_mouse_position[1],
                event.x,
                event.y,
            )

            self.canvas.create_line(
                line_positions,
                fill=self.pen_colour,
                width=self.pen_width,
                capstyle="round",
                smooth=True,
            )

            self.drawer.line(
                line_positions,
                fill=self.pen_colour,
                width=self.pen_width,
                joint="curve",
            )

            self.last_mouse_position = (event.x, event.y)

            self.update_preview_image()
            self.predict(fast=True)

    def convert_canvas_to_mnist(self) -> NpVector:
        threshold: int = 30
        box_padding: int = 6
        target_size: int = 20
        blur_sigma: float = 0.6

        image: NpVector = np.array(self.image).astype(np.uint8)

        # Filter any pixels that are below threshold (black or close to it).
        y_values: NpVector
        x_values: NpVector
        y_values, x_values = np.where(image > threshold)

        if x_values.size == 0 or y_values.size == 0:
            return np.zeros((self.image_size, self.image_size)).astype(np.uint8)

        # Find the bounds of the filtered pixels and add padding.
        x_min: int = int(
            max(0, x_values.min() - box_padding)
        )
        x_max: int = int(
            min(image.shape[1] - 1, x_values.max() + box_padding)
        )
        y_min: int = int(
            max(0, y_values.min() - box_padding)
        )
        y_max: int = int(
            min(image.shape[0] - 1, y_values.max() + box_padding)
        )

        # Crop original image to the bounds calculated
        # and blur to reduce rough edges and thick-stroke artifacts.
        cropped_image: NpVector = np.array(
            PILImage.fromarray(
                image[y_min:y_max + 1, x_min:x_max + 1],
                mode='L'
            ).filter(
                PILImageFilter.GaussianBlur(blur_sigma)
            )
        ).astype(np.uint8)

        # Scale the cropped image to a target size.
        scale: float = target_size / max(*cropped_image.shape)
        scaled_width: int = int(
            max(
                1,
                round(cropped_image.shape[1] * scale)
            )
        )
        scaled_height: int = int(
            max(
                1,
                round(cropped_image.shape[0] * scale)
            )
        )

        # Paste centered on a 28x28 canvas.
        canvas = PILImage.new(
            'L',
            (28, 28),
            color=0
        )
        canvas.paste(
            PILImage.fromarray(
                cropped_image,
                mode='L'
            ).resize(
                (
                    scaled_width,
                    scaled_height,
                ),
                PILImage.Resampling.LANCZOS
            ),
        (
                (28 - scaled_width) // 2,
                (28 - scaled_height) // 2,
            )
        )

        return (
            (
                np.clip(
                    np.array(canvas),
                    0,
                    255
                    ) > threshold # Filter pixels less than the given threshold.
            ) * 255 # Make remianing pixel white.
        ).astype(np.float32)

    def update_preview_image(self, image: NpVector | None = None):
        preview: NpVector = self.convert_canvas_to_mnist() if image is None else image

        preview_image: PILImageTk.PhotoImage = PILImageTk.PhotoImage(
            PILImage.fromarray(
                preview.astype(np.uint8),
                mode='L',
            ).resize(
                (self.image_size, self.image_size),
                PILImage.Resampling.NEAREST,
            )
        )

        self.preview.image = preview_image
        self.preview.configure(image=preview_image)

    def predict(self, fast: bool = False):
        image: NpVector = self.convert_canvas_to_mnist()

        prediction: int
        probabilities: NpVector
        prediction, probabilities, _ = (self.fast_classifier if fast else self.classifier).predict_image(image=image)

        self.prediction_variable.set(f"Prediction: {prediction}")

        probabilities = probabilities.flatten().astype(np.float32)
        ordered_potentials: NpVector = np.argsort(probabilities)[-3:][::-1].astype(np.int64)
        self.top_predictions_variable.set(
            f"Top 3: {
                " ".join([
                    f"{potential_number}: {probabilities[potential_number]:0.2f}"
                    for potential_number in ordered_potentials
                ])
            }"
        )

    def clear(self):
        self.canvas.delete("all")

        self.image.paste(
            0,
            (
                0,
                0,
                self.image_size,
                self.image_size,
            )
        )

        self.prediction_variable.set("Prediction: -")
        self.top_predictions_variable.set("Top 3: -")

        self.update_preview_image()

    @staticmethod
    def normalise(snapshot: NpVector) -> NpVector:
        snapshot_min: float = snapshot.min()
        snapshot_max: float = snapshot.max()
        difference: float = snapshot_max - snapshot_min
        if difference < 1e-8:
            return np.zeros_like(snapshot)
        return (snapshot - snapshot_min) / difference

    def simulate(self):
        image: NpVector = self.convert_canvas_to_mnist()
        if image.max() == 0: return # Return if nothing is drawn.

        images: NpVector = image[None, :]
        P_batch: NpVector = (images.reshape(images.shape[0], -1) * self.classifier.mnist_field.scale_factor).astype(np.float32)

        layer: WCNeuralField
        snapshots: List[List[List[NpVector]]] = []
        for layer in self.classifier.mnist_field.layers:
            layer.P = P_batch

            simlutation_result: SimulationSnapshots = layer.simulate(
                n_snapshots=self.n_snapshots,
            )

            # Normalise snapshots for visualisation and append to snapshots.

            snapshots.append(
                [
                    [self.normalise(snapshot) for snapshot in simlutation_result["snapshots_E"]],
                    [self.normalise(snapshot) for snapshot in simlutation_result["snapshots_I"]]
                ],
            )

            # P_batch = 0.5 * (simlutation_result["E_final"] + simlutation_result["I_final"])
            P_batch = 0.5 * (simlutation_result["snapshots_E"][2]
                             + simlutation_result["snapshots_I"][2])

        SnapshotViewer(self, snapshots)
