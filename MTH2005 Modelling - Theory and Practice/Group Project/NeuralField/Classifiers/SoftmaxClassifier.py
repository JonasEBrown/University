from ..Types import *

from ..MNIST import *
from ..WilsonCowan import *


class SoftmaxClassifier:

    def __init__(
            self,
            mnist_field: MNISTNeuralField,
            classifications: int = 10,
            weight_scale: float = 0.01,
            regularisation: float = 1e-3,
            max_images: int = 60000,
    ):
        self.mnist_field: MNISTNeuralField = mnist_field

        self.weight_scale: float = weight_scale
        self.regularisation: float = regularisation
        self.classifications: int = classifications

        self.W: NpVector = np.zeros((1, self.classifications)).astype(np.float32)
        self.b: NpVector = np.zeros((self.classifications,)).astype(np.float32)

        wbData: dict | None = self.load(
            f"(layers-{len(self.mnist_field.layers)}&scales-{
            '-'.join([str(scale) for scale in self.mnist_field.scales])
            })softmax_classifier_trained_data.npz")
        if wbData is not None: # Load W and b values from file.
            for key, value in wbData.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        else: # Run analysis (or load file) and then initialise W and b based on the feature dimensions.
            self.X: NpVector
            self.y: NpVector
            features_and_labels: Tuple[NpVector, NpVector] = self.mnist_field.run_analysis(
                data_range=(0, max_images),
            )
            self.X, self.y = features_and_labels

            if self.X.ndim == 1 and self.X.size > 0:
                self.X = self.X[None, :]  # Resize to be an array of vectors for batch processing.

            self.feature_dim: int = self.X.shape[1] if self.X.size > 0 else self.feature_dimension_from_scales()

            self.W: NpVector = np.random.randn(
                self.feature_dim,
                self.classifications
            ).astype(np.float32) / np.sqrt(self.feature_dim)

    @staticmethod
    def softmax(z: NpVector) -> NpVector:
        """
        Softmax function - removes chance of overflow error and normalises the exponentials of each entry in vector z.
        """
        soft = (z - np.max(z.astype(np.float32), axis=1, keepdims=True)).astype(
            np.float32)  # Reduce entries in vector to decrease chance of overflow.
        exp_soft = np.exp(soft).astype(np.float32)  # Find the exponential of each item in the vector.
        return (exp_soft / (np.sum(exp_soft, axis=1, keepdims=True) + 1e-12)).astype(
            np.float32)  # Normalise the exponential vector across rows (add 1e-12 to stop division by zero errors).

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

    def feature_dimension_from_scales(self) -> int:
        """
        Get the dimension of the feature from its scale and image size. As 28x28 grid + 14x14 grid = 980 features.
        """
        return int(
            sum(
                (self.mnist_field.image_width // scale) ** 2
                for scale in self.mnist_field.scales
            )
        )

    def loss_and_gradients(self, X: NpVector, y: NpVector) -> Tuple[float, NpVector, NpVector]:
        """
        Find the loss and gradients for each entry in a vector.
        """
        batch_size: int = X.shape[0]

        logits: NpVector = X @ self.W + self.b  # Raw scores for each class.
        probabilties: NpVector = self.softmax(logits)  # Converts logits into row-wise probabilities.

        one_hot: NpVector = np.zeros_like(probabilties)
        one_hot[np.arange(batch_size), y] = 1.0  # One-hot algorithm (ensures each row sums to 1).

        data_loss: float = -1 * np.sum(
            one_hot * np.log(probabilties + 1e-12)) / batch_size  # Entropy loss across batch.
        regularisation_loss: float = 0.5 * self.regularisation * np.sum(
            self.W * self.W)  # L2 regularisation on W to reduce overfitting.
        total_loss: float = data_loss + regularisation_loss  # Total loss.

        dlogits: NpVector = (probabilties - one_hot) / batch_size
        dW: NpVector = X.T @ dlogits + self.regularisation * self.W  # d/dW(X @ self.W + self.b)
        db: NpVector = np.sum(dlogits, axis=0)

        return total_loss, dW, db

    def predict(self, X: NpVector) -> Tuple[List[int], NpVector]:
        """
        Return the probabilities of each classification for the passed image.
        """
        logits = X @ self.W + self.b
        probabilities = self.softmax(logits)
        return np.argmax(probabilities, axis=1).astype(np.int64), probabilities

    def score(self, X: NpVector, y: NpVector) -> float:
        """
        Score the accuracy of the predictions for images against the labels given.
        """
        return float(
            np.mean(self.predict(X)[0] == y)
        )

    def fit(
            self,
            X: NpVector,
            y: NpVector,
            X_values: NpVector = None,
            y_values: NpVector = None,
            learning_rate: float = 0.1,
            epochs: int = 25,
            batch_size: int = 128,
            momentum: float = 0.8,
    ):
        """
        For x amount of epochs, select some random permutation of data and (in batches) fit the data to it,
        adjusting W and b each iteration.
        """
        N: int
        D: int
        N, D = X.shape

        if self.W is None or self.W.shape[0] != D:
            self.W = np.random.normal(0.0, self.weight_scale, size=(D, self.classifications)).astype(np.float32)
            self.b = np.zeros((self.classifications,)).astype(np.float32)

        velocityW: NpVector = np.zeros_like(self.W).astype(np.float32)
        velocityb: NpVector = np.zeros_like(self.b).astype(np.float32)

        best_W: NpVector = self.W.copy()
        best_b: NpVector = self.b.copy()
        best_accuracy: float = -np.inf

        epoch: int
        for epoch in range(0, epochs):
            permutation: NpVector = np.random.permutation(N).astype(
                np.int64)  # Randomise data each epoch to help avoid cycles.

            Xs: NpVector
            ys: NpVector
            Xs, ys = X[permutation], y[permutation]  # Split the dataset into the permutated blocks.

            start: int
            losses: List[float] = []
            for start in range(0, N, batch_size):  # Break data into batches to decrease computational expense.
                end = min(start + batch_size, N)  # Find the end of the batch.

                Xb: NpVector
                yb: NpVector
                Xb, yb = Xs[start:end], ys[start:end]  # Break the permutation into the current batch.

                loss: float
                dW: NpVector
                db: NpVector
                loss, dW, db = self.loss_and_gradients(Xb, yb)  # Calculate loss and gradients on the batch.
                losses.append(loss)

                # Momentum SGD - this is used to accelerate training in directions of consistent descent.
                # This also dampens noisy or curved regions.
                velocityW = (momentum * velocityW - learning_rate * dW).astype(np.float32)
                velocityb = (momentum * velocityb - learning_rate * db).astype(np.float32)
                self.W += velocityW
                self.b += velocityb

            new_accuracy: float = self.score(X_values, y_values)
            if new_accuracy > best_accuracy + 1e-2:
                best_accuracy = new_accuracy
                best_W = self.W.copy()
                best_b = self.b.copy()

            print(f"Epoch {epoch + 1}/{epochs} loss={np.mean(losses):0.3f} accuracy={new_accuracy * 100:0.2f}%")

        print(f"Applying best accuracy of {best_accuracy * 100:0.2f}% to model.")
        self.W = best_W
        self.b = best_b

    def train(self, value_split: float = 0.2) -> float:
        """
        Train the model data with the MNIST dataset, splitting it into train/test data using value_split as a ratio.
        """
        N: int = len(self.X)
        indices: NpVector = np.arange(N).astype(np.int64)

        split_index: int = int(N * (1.0 - value_split))  # This splits the data into training and value data.

        train_index: int
        value_index: int
        train_index, value_index = indices[:split_index], indices[split_index:]

        X_train: NpVector
        y_train: NpVector
        X_train, y_train = self.X[train_index], self.y[train_index]

        X_values: NpVector
        y_values: NpVector
        X_values, y_values = self.X[value_index], self.y[value_index]

        self.fit(
            X_train, y_train,
            X_values, y_values,
        )

        accuracy: float = self.score(X_values, y_values)

        self.save(
            f"(layers-{len(self.mnist_field.layers)}&scales-{
            '-'.join([str(scale) for scale in self.mnist_field.scales])
            })softmax_classifier_trained_data.npz",
            meta={
                "classifications": int(self.classifications),
                "regularisation": float(self.regularisation),
                "weight_scale": float(self.weight_scale),
                "accuracy": float(accuracy),
            },
            W=self.W,
            b=self.b
        )

        return accuracy

    def predict_image(self, index: int = None, image: NpVector = None) -> Tuple[int, NpVector, int]:
        """
        Use the classifier to find the most probable classification for the entered data (image at specified index).
        """
        classification: int = -1
        if image is None:
            index = np.random.randint(0, self.mnist_field.test_data.shape[0]) if index is None else index

            image = (self.mnist_field.test_data[0][:, index]
                     .reshape(self.mnist_field.image_width, self.mnist_field.image_width)).astype(np.float32)
            classification = int(self.mnist_field.test_data[1][index][0])
            print(f"Expected classification: {classification}")

        feature_row: NpVector = self.mnist_field.run_simulation(
            images=image[None, ...].astype(np.float32)
        )[0]

        probabilities: NpVector
        prediction_array: NpVector
        prediction_array, probabilities = self.predict(feature_row[None, :])

        prediction: int = int(prediction_array.item())

        return prediction, probabilities, classification

    def predict_image_with_snapshots(self, index: int = None, image: NpVector = None) -> Tuple[int, NpVector, int]:
        """
        Use the classifier to find the most probable classification for the entered data (image at specified index)
        returning snapshots too.
        """
        classification: int = -1
        if image is None:
            index = np.random.randint(0, self.mnist_field.test_data.shape[0]) if index is None else index

            image = (self.mnist_field.test_data[0][:, index]
                     .reshape(self.mnist_field.image_width, self.mnist_field.image_width)).astype(np.float32)
            classification = int(self.mnist_field.test_data[1][index][0])
            print(f"Expected classification: {classification}")

        feature_row: NpVector = self.mnist_field.run_simulation(
            images=image[None, ...].astype(np.float32)
        )[0]

        probabilities: NpVector
        prediction_array: NpVector
        prediction_array, probabilities = self.predict(feature_row[None, :])

        prediction: int = int(prediction_array.item())

        return prediction, probabilities, classification

    def predict_batch(self,
                      indices: NpVector = None,
                      images: List[NpVector] = None
                      ) -> Tuple[List[int], NpVector, List[int], NpVector]:
        """
        Find the most probable classification for a batch of images.
        """
        true_labels: List[int] = []
        if images is not None:
            images = np.asarray(images).astype(np.float32)
        else:
            images = np.stack([
                self.mnist_field.test_data[0][:, index].reshape(self.mnist_field.image_width,
                                                                self.mnist_field.image_width)
                for index in indices
            ], axis=0).astype(np.float32)
            true_labels = [
                int(self.mnist_field.test_data[1][index][0])
                for index in indices
            ]

        feature_rows: NpVector = self.mnist_field.run_simulation(images=images)

        predictions: List[int]
        probabilities: NpVector
        predictions, probabilities = self.predict(feature_rows)

        correct: int = sum(
            prediction == true_labels[index]
            for index, prediction in enumerate(predictions)
        )
        print(f"{correct * 100 / len(true_labels):0.2f}% recognised correctly")

        return predictions, probabilities, true_labels, images

    def show_batch(self,
                   fname: str | None = "batch_predictions.png",
                   batch_size: int = 36
                   ):
        """
        Display a batch of size x, showing whether the classifier predicted the correct values or not.
        """
        images: NpVector
        true_labels: List[int]
        predictions: List[int]
        probabilities: NpVector
        predictions, probabilities, true_labels, images = self.predict_batch(
            indices=np.asarray(
                np.random.randint(0, self.mnist_field.test_data_size, batch_size)
            ).astype(np.int64)
        )

        columns: int = math.ceil(math.sqrt(batch_size))
        rows: int = math.ceil(batch_size / columns)

        figure: plt.Figure
        axes: np.ndarray
        figure, axes = plt.subplots(rows, columns, figsize=(columns * 3, rows * 3.3))
        [[axis.axis("off") for axis in row] for row in axes]
        axes = np.atleast_2d(axes)

        index: int
        image: NpVector
        for index, image in enumerate(images):
            axis: plt.Axes = axes[index // columns, index % columns]
            axis.imshow(image, cmap="gray")

            prediction: int = predictions[index]
            correct: bool = (prediction == true_labels[index])
            axis.set_title(f"Pred: {prediction} {"✓" if correct else "✗"}", color="green" if correct else "red",
                           fontsize=30, pad=2)

        plt.suptitle(f"Random batch from MNIST dataset", fontsize=30)
        plt.savefig(fname, dpi=150)
        plt.close(figure)
