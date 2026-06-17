class CostAnalyzer:

    HOURS_PER_MONTH = 730

    @staticmethod
    def calculate_monthly_cpu_cost(

        cpu_allocation,

        node_cpu_capacity,

        node_hourly_price
    ):

        if (

            node_cpu_capacity <= 0

            or

            node_hourly_price <= 0
        ):

            return 0

        monthly_cost = (

            cpu_allocation

            /

            node_cpu_capacity

        ) * (

            node_hourly_price

        ) * (

            CostAnalyzer.HOURS_PER_MONTH
        )

        return round(

            monthly_cost,

            2
        )

    @staticmethod
    def calculate_monthly_memory_cost(

        memory_allocation_mib,

        node_memory_capacity_mib,

        node_hourly_price
    ):

        if (

            node_memory_capacity_mib <= 0

            or

            node_hourly_price <= 0
        ):

            return 0

        monthly_cost = (

            memory_allocation_mib

            /

            node_memory_capacity_mib

        ) * (

            node_hourly_price

        ) * (

            CostAnalyzer.HOURS_PER_MONTH
        )

        return round(

            monthly_cost,

            2
        )

    @staticmethod
    def calculate_total_monthly_cost(

        cpu_cost,

        memory_cost
    ):

        total_cost = (

            cpu_cost

            +

            memory_cost
        )

        return round(

            total_cost,

            2
        )

    @staticmethod
    def calculate_monthly_savings(

        current_cost,

        optimized_cost
    ):

        savings = (

            current_cost

            -

            optimized_cost
        )

        return round(

            savings,

            2
        )