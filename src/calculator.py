class Calculator:
    def __init__(self, history=None):
        self.history = history or []

    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(("add", a, b, result))
        return result

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("cannot divide by zero")
        result = a / b
        self.history.append(("divide", a, b, result))
        return result


def format_result(value: float) -> str:
    return f"{value:.2f}"
