from case_study import *

if __name__ == "__main__":
    x_0: number = 6
    iterations: int = 10

    f: MathFunc = LambdaMathFunc(lambda x: ((x + 5) ** (1/3)) - x + 3)
    g_1: MathFunc = LambdaMathFunc(lambda x: ((x + 5) ** (1/3)) + 3)
    g_2: MathFunc = LambdaMathFunc(lambda x: ((x - 3) ** 3) - 5)

    x_space = np.linspace(0, iterations, 100)

    method = FixedPointMethod(
        func=f,
        identities=[
            g_1,
            g_2,
        ]
    )

    method.plot(
        x=x_space,
        x_0=x_0,
    )

    print(method.root)
    print(method.error)

