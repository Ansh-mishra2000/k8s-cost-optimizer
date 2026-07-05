class Analyzer:

    MIN_MEMORY_MIB = 64
    MEMORY_BUFFER_PERCENT = 20

    @staticmethod
    def calculate_cpu_waste(
        requested_cpu,
        actual_cpu
    ):
        """
        Calculate CPU waste percentage.

        Formula:
        ((requested_cpu - actual_cpu) /
         requested_cpu) * 100
        """

        if requested_cpu <= 0:

            return 0

        waste = (

            (
                requested_cpu
                -
                actual_cpu
            )

            /

            requested_cpu

        ) * 100

        return round(
            waste,
            2
        )

    @staticmethod
    def calculate_memory_waste(
        requested_memory,
        actual_memory
    ):
        """
        Calculate memory waste percentage.
        """

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
    def recommend_cpu(
        requested_cpu,
        actual_cpu
    ):
        """
        Recommend CPU based on actual usage.

        Adds a 20% safety buffer.
        """

        recommended = (

            actual_cpu
            *
            1.2
        )

        return round(
            recommended,
            2
        )

    @staticmethod
    def recommend_memory(requested_memory, actual_memory):

        calculated_memory = round(actual_memory * 1.2, 2)

        explanation = None

        if calculated_memory < Analyzer.MIN_MEMORY_MIB:

            recommended_memory = Analyzer.MIN_MEMORY_MIB

            explanation = {
                "memory_buffer_percent": Analyzer.MEMORY_BUFFER_PERCENT,
                "calculated_memory_mib": calculated_memory,
                "minimum_memory_policy_mib": Analyzer.MIN_MEMORY_MIB,
                "recommendation_reason": (
                    f"Calculated requirement ({calculated_memory} MiB) "
                    "is below the minimum allocation policy of "
                    f"{Analyzer.MIN_MEMORY_MIB} MiB."
                )
            }

        else:

            recommended_memory = calculated_memory

        return recommended_memory, explanation