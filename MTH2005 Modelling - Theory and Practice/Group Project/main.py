import sys

import NeuralField
from NeuralField.Types import *

def create_mnist_neural_field(
        scales: List[int] = (1, 2, 4),
        parameters: List[Dict[str, float]] | None = None,
        tau_E: float = 1.0,
        tau_I: float = 2.0,
        beta: float = 4.5,
        theta: float = 0.25,
        dt: float = 0.02,
        total_time: float = 6.0,
) -> NeuralField.MNISTNeuralField:
    mnist_field: NeuralField.MNISTNeuralField = NeuralField.MNISTNeuralField(scales=scales)

    parameters: List[Dict[str, float]] = parameters or [
        {
            "strength_EE": 12.0,
            "strength_EI": 14.0,
            "strength_IE": 10.0,
            "strength_II": 6.0,
            "sigma_EE": 1.0,
            "sigma_EI": 3.0,
            "sigma_IE": 1.0,
            "sigma_II": 3.0,
        },
        {
            "strength_EE": 11.0,
            "strength_EI": 13.0,
            "strength_IE": 10.0,
            "strength_II": 6.0,
            "sigma_EE": 2.0,
            "sigma_EI": 4.0,
            "sigma_IE": 2.0,
            "sigma_II": 4.0,
        },
        {
            "strength_EE": 10.0,
            "strength_EI": 12.0,
            "strength_IE": 10.0,
            "strength_II": 6.0,
            "sigma_EE": 3.0,
            "sigma_EI": 5.0,
            "sigma_IE": 3.0,
            "sigma_II": 5.0,
        }
    ]

    mnist_field.layers = [
        NeuralField.WCNeuralField(
            grid_size=(mnist_field.image_width, mnist_field.image_width),
            tau_E=tau_E,
            tau_I=tau_I,
            beta=beta,
            theta=theta,
            dt=dt,
            total_time=total_time,
            **kwargs
        )
        for kwargs in parameters
    ]

    return mnist_field

def run_mnist_digit_classifier_ui(
        train: bool = False,
        colour_map: str = "magma",
        **kwargs,
    ):
    mnist_field: NeuralField.MNISTNeuralField = create_mnist_neural_field(**kwargs)

    softmax = NeuralField.SoftmaxClassifier(mnist_field)
    if train: softmax.train()

    DigitClassifierUI(softmax, colour_map=colour_map)

def run_batch_prediction(
        max_image_range: int | None = 60000,
        **kwargs,
    ):
    mnist_field: NeuralField.MNISTNeuralField = create_mnist_neural_field(**kwargs)

    softmax = NeuralField.SoftmaxClassifier(mnist_field)
    softmax.show_batch(**kwargs)

def run_analysis_and_training(
        max_image_range: int | None = 60000,
        **kwargs,
    ):
    mnist_field: NeuralField.MNISTNeuralField = create_mnist_neural_field(**kwargs)
    mnist_field.run_analysis(data_range=(0, max_image_range))

    softmax = NeuralField.SoftmaxClassifier(mnist_field)
    softmax.train()

def run_ray_cluster(
        max_image_range: int | None = 60000,
        **kwargs,
    ):
    mnist_field: NeuralField.MNISTNeuralField = create_mnist_neural_field(**kwargs)

    rayOrchestrator: RayOrchestrator = RayOrchestrator(mnist_field, max_image_range=max_image_range)
    rayOrchestrator.run()

def run_parameter_test(
        size: int = 28,
        E0: float = None,
        I0: float = None,
        sigmas: List[float] = (0.8, 1.2, 1.8, 2.5),
        n_snapshots: int = 4,
        **kwargs,
    ):
    NeuralField.WCNeuralField(
        grid_size=(size, size),
        E0=np.full(size**2, E0 or 0.9).astype(np.float32),
        I0=np.full(size**2, I0 or 0.1).astype(np.float32),
        **kwargs,
    ).test(
        sigmas=sigmas,
        n_snapshots=n_snapshots,
    )

if __name__ == "__main__":
    args: List[str] = sys.argv.copy()
    program: str  = args[1] if len(args) > 1 else None
    if program is None:
        args = [""] + input("""Please type "mnist", "plots", or "batch": """).split(' ')
        program = args[1]

    arg: str
    kwargs: Dict[str, Any] = {}
    for arg in args[2:]:
        if arg.find("=") != -1:
            split: List[str] = arg.split("=")

            key: str = split[0]
            value: str = split[1]
            try:
                value = eval(value)
                kwargs[key] = value
            except:
                raise SystemExit(f"Unknow value \"{value}\"")

    match program:
        case "mnist":
            from NeuralField.UI import *
            run_mnist_digit_classifier_ui(**kwargs)

        case "plots":
            run_parameter_test(**kwargs)

        case "batch":
            run_batch_prediction(**kwargs)

        case "ray":
            from NeuralField.Ray import *
            run_ray_cluster(**kwargs)

        case "analysis":
            run_analysis_and_training(**kwargs)

        case _:
            raise SystemExit("No valid option selected.")