class Analyzer:

    @staticmethod
    def calculate_cpu_waste(requested_cpu, actual_cpu):
        """
        Calculate CPU waste percentage.

        Formula:
        ((requested_cpu - actual_cpu) / requested_cpu) * 100

        Example:
        requested_cpu = 2
        actual_cpu = 0.2

        Result:
        90%
        """

        if requested_cpu <= 0:
            return 0

        waste = (
            (requested_cpu - actual_cpu)
            / requested_cpu
        ) * 100

        return round(waste, 2)

    @staticmethod
    def calculate_memory_waste(
        requested_memory,
        actual_memory
    ):

        if requested_memory <= 0:

            return 0

        waste = (
            (
                requested_memory
                -
                actual_memory
            )

            /

            requested_memory

        ) * 100

        return round(
            waste,
            2
        )

    @staticmethod
    def recommend_cpu(requested_cpu, actual_cpu):
        """
        Recommend CPU based on actual usage.

        Adds 20% buffer.
        """

        recommended = actual_cpu * 1.2

        return round(recommended, 4)

    @staticmethod
    def recommend_memory(
        requested_memory,
        actual_memory
    ):

        recommended = round(
            actual_memory * 1.2,
            2
        )

        return max(
            recommended,
            64
        )