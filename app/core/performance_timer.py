from time import perf_counter


class PerformanceTimer:
    """
    Lightweight elapsed-time timer for
    operational performance measurements.
    """

    def __init__(self):
        self._start = None
        self.elapsed_seconds = None

    def start(self):
        self._start = perf_counter()
        return self

    def stop(self):
        if self._start is None:
            raise RuntimeError(
                "Timer was stopped before it was started."
            )

        self.elapsed_seconds = (
            perf_counter() - self._start
        )

        return self.elapsed_seconds