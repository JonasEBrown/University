from .UITypes import *

from ..Classifiers import *


class DigitClassifierUI:

    root: tkinter.Tk
    image_size: int
    classifier: SoftmaxClassifier
    colour_map: plt.Colormap | None


class SnapshotViewer:

    def __init__(self, app: DigitClassifierUI, snapshots: List[List[List[NpVector]]]):
        self.app = app
        self.snapshots: List[List[List[NpVector]]] = snapshots

        self.font: str = "Segoe UI"
        self.gif_padding: int = 5
        self.current_layer: int = 0
        self.current_snapshot: int = 0
        self.total_layers: int = len(self.snapshots)
        self.snapshots_per_layer: int = len(self.snapshots[0][0])

        self.window: tkinter.Toplevel = tkinter.Toplevel(self.app.root)
        self.window.title("Simulation snapshots")

        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)

        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_columnconfigure(3, weight=1)
        self.window.grid_columnconfigure(4, weight=1)

        self.preview_E: ttk.Label = ttk.Label(self.window)
        self.preview_E.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
        )

        self.preview_I: ttk.Label = ttk.Label(self.window)
        self.preview_I.grid(
            row=0,
            column=4,
            columnspan=3,
            padx=6,
            pady=6,
        )

        self.update_preview_images()

        self.layer_variable: tkinter.StringVar = tkinter.StringVar(value=f"L: {self.current_layer + 1}/{self.total_layers}")
        self.snapshot_variable: tkinter.StringVar = tkinter.StringVar(value=f"S: {self.current_snapshot + 1}/{self.snapshots_per_layer}")

        self.layer_label: ttk.Label = ttk.Label(
            self.window,
            textvariable=self.layer_variable,
            font=(self.font, 12, "bold"),
            anchor="center",
        )
        self.layer_label.grid(
            row=1,
            column=2,
            columnspan=3,
            padx=6,
            sticky="nesw",
        )

        self.snapshot_label: ttk.Label = ttk.Label(
            self.window,
            textvariable=self.snapshot_variable,
            font=(self.font, 12, "bold"),
            anchor="center",
        )
        self.snapshot_label.grid(
            row=2,
            column=2,
            columnspan=3,
            padx=6,
            sticky="nesw",
        )

        self.previous_snapshot_button: ttk.Button = ttk.Button(
            self.window,
            text="<",
            command=self.previous_snapshot,
        )
        self.previous_snapshot_button.grid(
            row=1,
            column=1,
            rowspan=2,
            padx=6,
            pady=(0, 6),
        )

        self.next_snapshot_button: ttk.Button = ttk.Button(
            self.window,
            text=">",
            command=self.next_snapshot,
        )
        self.next_snapshot_button.grid(
            row=1,
            column=5,
            rowspan=2,
            padx=6,
            pady=(0, 6),
        )

        self.previous_layer_button: ttk.Button = ttk.Button(
            self.window,
            text="<<",
            command=self.previous_layer,
        )
        self.previous_layer_button.grid(
            row=1,
            column=0,
            rowspan=2,
            padx=6,
            pady=(0, 6),
        )

        self.next_layer_button: ttk.Button = ttk.Button(
            self.window,
            text=">>",
            command=self.next_layer,
        )
        self.next_layer_button.grid(
            row=1,
            column=6,
            rowspan=2,
            padx=6,
            pady=(0, 6),
        )

        self.menu: tkinter.Menu = tkinter.Menu(self.window)

        self.file_menu: tkinter.Menu = tkinter.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(
            label="Export to GIF",
            command=self.export_to_gif
        )
        self.file_menu.add_command(
            label="Export to MP4",
            command=self.export_to_mp4
        )

        self.menu.add_cascade(
            label="File",
            menu=self.file_menu
        )

        self.window.config(
            menu=self.menu,
        )

        # self.file_menu.entryconfig("Export to GIF", state="disabled")

    def get_current_images(self, layer: int | None = None, snapshot: int | None = None) -> Tuple[NpVector, NpVector]:
        E_batch: NpVector = self.snapshots[layer or self.current_layer][0][snapshot or self.current_snapshot]
        I_batch: NpVector = self.snapshots[layer or self.current_layer][1][snapshot or self.current_snapshot]

        if E_batch.ndim == 2: E_batch = E_batch[0]
        if I_batch.ndim == 2: I_batch = I_batch[0]

        return (
            (
                E_batch.reshape(
                    (
                        self.app.classifier.mnist_field.image_width,
                        self.app.classifier.mnist_field.image_width,
                    )
                ) * 255
            ).astype(np.uint8),
            (
                I_batch.reshape(
                    (
                        self.app.classifier.mnist_field.image_width,
                        self.app.classifier.mnist_field.image_width,
                    )
                ) * 255
            ).astype(np.uint8)
        )

    def update_text_values(self):
        self.layer_variable.set(f"L: {self.current_layer + 1}/{self.total_layers}")
        self.snapshot_variable.set(f"S: {self.current_snapshot + 1}/{self.snapshots_per_layer}")

    def apply_colour_map(self, image: NpVector) -> PILImage.Image:
        if self.app.colour_map is None:
            return PILImage.fromarray(
                image,
                mode='L',
            )
        return PILImage.fromarray(
            (
                self.app.colour_map(image)[:, :, :3] * 255
            ).astype(np.uint8),
            mode="RGB",
        )

    def update_preview_images(self):
        E_preview: NpVector
        I_preview: NpVector
        E_preview, I_preview = self.get_current_images()

        E_preview_image: PILImageTk.PhotoImage = PILImageTk.PhotoImage(
            self.apply_colour_map(E_preview).resize(
                (self.app.image_size, self.app.image_size),
                PILImage.Resampling.NEAREST,
            )
        )

        I_preview_image: PILImageTk.PhotoImage = PILImageTk.PhotoImage(
            self.apply_colour_map(I_preview).resize(
                (self.app.image_size, self.app.image_size),
                PILImage.Resampling.NEAREST,
            )
        )

        self.preview_E.image = E_preview_image
        self.preview_I.image = I_preview_image

        self.preview_E.configure(image=E_preview_image)
        self.preview_I.configure(image=I_preview_image)

    def previous_snapshot(self):
        self.current_snapshot -= 1
        if self.current_snapshot < 0:
            self.current_snapshot = self.snapshots_per_layer - 1 if self.current_layer > 0 else 0
            self.current_layer = max(
                self.current_layer - 1,
                0
            )
        self.update_text_values()
        self.update_preview_images()

    def next_snapshot(self):
        self.current_snapshot += 1
        if self.current_snapshot >= self.snapshots_per_layer:
            self.current_snapshot = 0 if self.current_layer < self.total_layers - 1 else self.snapshots_per_layer - 1
            self.current_layer = min(
                self.current_layer + 1,
                self.total_layers - 1
            )
        self.update_text_values()
        self.update_preview_images()

    def previous_layer(self):
        if self.current_layer == 0:
            self.current_snapshot = 0
        self.current_layer = max(
            0,
            self.current_layer - 1
        )
        self.update_text_values()
        self.update_preview_images()

    def next_layer(self):
        if self.current_layer == self.total_layers - 1:
            self.current_snapshot = self.snapshots_per_layer - 1
        self.current_layer = min(
            self.current_layer + 1,
            self.total_layers - 1,
        )
        self.update_text_values()
        self.update_preview_images()

    def process_snapshots_into_frames(self) -> List[PILImage.Image]:
        layer: int
        snapshot: int
        frames: List[PILImage.Image] = []
        for layer in range(self.total_layers):
            for snapshot in range(self.snapshots_per_layer):
                if layer > 0 and snapshot == 0: continue

                E_preview: NpVector
                I_preview: NpVector
                E_preview, I_preview = self.get_current_images(
                    layer=layer,
                    snapshot=snapshot
                )

                combined_image: PILImage.Image = PILImage.new(
                    size=(
                        (self.app.image_size * 2) + self.gif_padding,
                        self.app.image_size
                    ),
                    mode="RGB"
                )

                combined_image.paste(
                    im=self.apply_colour_map(E_preview).resize(
                        (self.app.image_size, self.app.image_size),
                        PILImage.Resampling.NEAREST,
                    ),
                    box=(0, 0)
                )
                combined_image.paste(
                    im=self.apply_colour_map(I_preview).resize(
                        (self.app.image_size, self.app.image_size),
                        PILImage.Resampling.NEAREST,
                    ),
                    box=(
                        self.app.image_size + self.gif_padding,
                        0,
                    )
                )

                frames.append(combined_image)

        change_scores: NpVector = np.array(
            [1.0] + [
                np.mean(
                    np.abs(
                        np.array(
                            frame
                        ).astype(np.float32) - np.array(
                            frames[index - 1]
                        ).astype(np.float32)
                    )
                )
                for index, frame in enumerate(frames)
                if index != 0
            ]
        ).astype(np.float32)

        processed_frames: List[PILImage.Image] = [
            frame
            for frame, weight in zip(
                frames,
                (
                    1 + (
                        (
                            change_scores / change_scores.max()
                        ) * 5
                    )
                ).astype(int),
            )
            for _ in range(weight)
        ]

        return processed_frames

    def export_to_gif(self):
        filepath: str = filedialog.asksaveasfilename(
            title="Export to GIF",
            defaultextension=".gif",
            filetypes=[
                (
                    "GIF Files",
                    "*.gif",
                ),
            ]
        )

        if not filepath: return

        gif_frames: List[PILImage.Image] = self.process_snapshots_into_frames()

        gif_frames[0].save(
            filepath,
            save_all=True,
            append_images=gif_frames[1:],
            duration=int(
                1000 / max(
                    1,
                    int(
                        len(gif_frames)
                        / (
                            self.app.classifier.mnist_field.layers[0].total_time * self.total_layers
                        )
                    )
                )
            ),
            loop=0,
            optimize=False,
        )

        print(f"Saved as GIF to {filepath}")

    def export_to_mp4(self):
        filepath: str = filedialog.asksaveasfilename(
            title="Export to MP4",
            defaultextension=".mp4",
            filetypes=[
                (
                    "MP4 Files",
                    "*.mp4",
                ),
            ]
        )

        if not filepath: return

        mp4_frames: List[PILImage.Image] = self.process_snapshots_into_frames()

        writer = imageio.get_writer(
            filepath,
            fps=max(
                1,
                int(
                    len(mp4_frames)
                    / (
                        self.app.classifier.mnist_field.layers[0].total_time * self.total_layers
                    )
                )
            ),
            codec="libx264",
            quality=9,
            macro_block_size=None,
        )

        for frame in mp4_frames:
            width: int
            height: int
            width, height = frame.size
            if width % 2 != 0 or height % 2 != 0:
                frame = frame.resize(
                    (
                        width + (width % 2),
                        height + (height % 2)
                    )
                )
            writer.append_data(
                np.array(frame)
            )
        writer.close()

        print(f"Saved as MP4 to {filepath}")