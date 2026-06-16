import boto3
import json

class AWSService:

    def __init__(self):

        self.ec2 = boto3.client(
            "ec2",
            region_name="ap-south-1"
        )

        self.pricing = boto3.client(
            "pricing",
            region_name="us-east-1"
        )

    def get_instance_type(
        self,
        instance_id
    ):

        response = self.ec2.describe_instances(

            InstanceIds=[
                instance_id
            ]
        )

        return response[
            "Reservations"
        ][0][
            "Instances"
        ][0][
            "InstanceType"
        ]
    def get_hourly_price(
        self,
        instance_type
    ):

        response = self.pricing.get_products(

            ServiceCode="AmazonEC2",

            Filters=[

                {
                    "Type": "TERM_MATCH",
                    "Field": "instanceType",
                    "Value": instance_type
                },

                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": "Asia Pacific (Mumbai)"
                },

                {
                    "Type": "TERM_MATCH",
                    "Field": "operatingSystem",
                    "Value": "Linux"
                },

                {
                    "Type": "TERM_MATCH",
                    "Field": "tenancy",
                    "Value": "Shared"
                },

                {
                    "Type": "TERM_MATCH",
                    "Field": "capacitystatus",
                    "Value": "Used"
                }

            ],

            MaxResults=1
        )

        price_item = json.loads(

            response[
                "PriceList"
            ][0]
        )

        terms = price_item[
            "terms"
        ][
            "OnDemand"
        ]

        term = next(
            iter(
                terms.values()
            )
        )

        dimension = next(
            iter(
                term[
                    "priceDimensions"
                ].values()
            )
        )

        return float(

            dimension[
                "pricePerUnit"
            ][
                "USD"
            ]
        )    