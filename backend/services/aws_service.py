import json
import time
import logging
import boto3

logger = logging.getLogger(__name__)

# Fallback on-demand hourly pricing (USD) for ap-south-1 (Mumbai)
# Ensures resilience if AWS Pricing API is slow, throttled, or unreachable
FALLBACK_HOURLY_PRICES = {
    "t3.nano": 0.0052,
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "t3.xlarge": 0.1664,
    "t3.2xlarge": 0.3328,
    "t2.nano": 0.0058,
    "t2.micro": 0.0116,
    "t2.small": 0.0230,
    "t2.medium": 0.0460,
    "t2.large": 0.0920,
    "t4g.nano": 0.0042,
    "t4g.micro": 0.0084,
    "t4g.small": 0.0168,
    "t4g.medium": 0.0336,
    "t4g.large": 0.0672,
    "m5.large": 0.0960,
    "m5.xlarge": 0.1920,
    "c5.large": 0.0850,
    "c5.xlarge": 0.1700,
}

# In-memory pricing cache: { (instance_type, region): (price, expire_timestamp) }
_PRICING_CACHE = {}
_PRICING_CACHE_TTL_SECONDS = 86400  # 24 hours

# In-memory instance metadata cache: { instance_id: (instance_type, expire_timestamp) }
_INSTANCE_TYPE_CACHE = {}
_INSTANCE_CACHE_TTL_SECONDS = 300  # 5 minutes


class AWSService:

    def __init__(self, region_name="ap-south-1"):
        self.region_name = region_name

        self.ec2 = boto3.client(
            "ec2",
            region_name=self.region_name
        )

        # AWS Pricing API is hosted in us-east-1
        self.pricing = boto3.client(
            "pricing",
            region_name="us-east-1"
        )

    def get_instance_type(self, instance_id: str) -> str:
        """Fetch EC2 instance type with in-memory caching."""
        now = time.time()
        
        # Check cache
        if instance_id in _INSTANCE_TYPE_CACHE:
            cached_type, expire_at = _INSTANCE_TYPE_CACHE[instance_id]
            if now < expire_at:
                return cached_type

        try:
            response = self.ec2.describe_instances(
                InstanceIds=[instance_id]
            )
            instance_type = response["Reservations"][0]["Instances"][0]["InstanceType"]
            
            # Store in cache (5 minutes TTL)
            _INSTANCE_TYPE_CACHE[instance_id] = (instance_type, now + _INSTANCE_CACHE_TTL_SECONDS)
            return instance_type
            
        except Exception as e:
            logger.warning("Failed to describe instance %s: %s", instance_id, e)
            return "t3.small"

    def get_hourly_price(self, instance_type: str, location: str = "Asia Pacific (Mumbai)") -> float:
        """
        Fetch hourly price for an EC2 instance type with 24-hour TTL caching 
        and resilient offline fallback.
        """
        cache_key = (instance_type, location)
        now = time.time()

        # 1. Check in-memory cache
        if cache_key in _PRICING_CACHE:
            cached_price, expire_at = _PRICING_CACHE[cache_key]
            if now < expire_at:
                return cached_price

        # 2. Query AWS Pricing API
        try:
            response = self.pricing.get_products(
                ServiceCode="AmazonEC2",
                Filters=[
                    {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                    {"Type": "TERM_MATCH", "Field": "location", "Value": location},
                    {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                    {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                    {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"}
                ],
                MaxResults=1
            )

            if response.get("PriceList"):
                price_item = json.loads(response["PriceList"][0])
                terms = price_item["terms"]["OnDemand"]
                term = next(iter(terms.values()))
                dimension = next(iter(term["priceDimensions"].values()))
                price = float(dimension["pricePerUnit"]["USD"])

                # Store in cache (24 hours TTL)
                _PRICING_CACHE[cache_key] = (price, now + _PRICING_CACHE_TTL_SECONDS)
                return price

        except Exception as e:
            logger.warning("AWS Pricing API call failed for %s (%s): %s. Using fallback price.", instance_type, location, e)

        # 3. Resilient Fallback
        fallback_price = FALLBACK_HOURLY_PRICES.get(instance_type, 0.0208)
        _PRICING_CACHE[cache_key] = (fallback_price, now + 3600)  # cache fallback for 1 hour
        return fallback_price