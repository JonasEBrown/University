from ..Types import *


class MNISTDataset:

    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = self.get_dataset_download_path()

        self.training_images_filepath: str = os.path.join(base_path, 'train-images-idx3-ubyte/train-images-idx3-ubyte')
        self.training_labels_filepath: str = os.path.join(base_path, 'train-labels-idx1-ubyte/train-labels-idx1-ubyte')
        self.test_images_filepath: str = os.path.join(base_path, 't10k-images-idx3-ubyte/t10k-images-idx3-ubyte')
        self.test_labels_filepath: str = os.path.join(base_path, 't10k-labels-idx1-ubyte/t10k-labels-idx1-ubyte')

        self.test_data: NpVector
        self.training_data: NpVector
        self.training_data, self.test_data = self.load_data()

    @staticmethod
    def get_dataset_download_path() -> str:
        """
        Either returns the path where the MNIST dataset is stored or downloads it and returns its destination.
        """
        return kagglehub.dataset_download("hojjatk/mnist-dataset")

    @staticmethod
    def read_images_labels(images_filepath: str, labels_filepath: str) -> Tuple[NpVector, NpVector]:
        """
        Reads images and labels from the MNIST dataset into numpy arrays.
        """
        return (
            idx2numpy.convert_from_file(images_filepath).astype(np.float32),
            idx2numpy.convert_from_file(labels_filepath).astype(np.float32)
        )

    def load_data(self) -> Tuple[Tuple[NpVector, NpVector], Tuple[NpVector, NpVector]]:
        """
        Returns the image and label training and test data from the MNIST dataset.
        """
        x_train: NpVector
        y_train: NpVector
        x_train, y_train = self.read_images_labels(self.training_images_filepath, self.training_labels_filepath)

        x_test: NpVector
        y_test: NpVector
        x_test, y_test = self.read_images_labels(self.test_images_filepath, self.test_labels_filepath)

        return (
            (
                x_train.reshape(x_train.shape[0], -1).T,
                y_train.reshape(y_train.shape[0], -1)
            ),
            (
                x_test.reshape(x_test.shape[0], -1).T,
                y_test.reshape(y_test.shape[0], -1)
            )
        )
