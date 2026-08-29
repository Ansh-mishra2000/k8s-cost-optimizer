import os
import time
import logging
from datetime import datetime, timezone

import requests

# -------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Backend URL
# -------------------------------------------------------

BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://k8s-cost-optimizer-service:9000"
)

# -------------------------------------------------------
# Retry Configuration
# -------------------------------------------------------

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():

    overall_start = time.perf_counter()

    success = 0
    failed = 0

    logger.info("=" * 70)
    logger.info("Recommendation Collector Started")
    logger.info("Started At : %s", datetime.now(timezone.utc))
    logger.info("=" * 70)

    # -------------------------------------------------------
    # Fetch Deployments (with Retry)
    # -------------------------------------------------------

    logger.info("Fetching deployments...")

    deployments = None

    for attempt in range(1, MAX_RETRIES + 1):

        logger.info("Fetch Deployment Attempt %d/%d", attempt, MAX_RETRIES)

        try:

            response = requests.get(
                f"{BASE_URL}/deployments",
                timeout=30
            )

            response.raise_for_status()

            deployments = response.json()

            logger.info(
                "Successfully fetched %d deployment(s)",
                len(deployments)
            )

            break

        except Exception as e:

            logger.warning(
                "Unable to fetch deployments : %s",
                str(e)
            )

            if attempt < MAX_RETRIES:

                logger.info(
                    "Retrying in %d seconds...",
                    RETRY_DELAY
                )

                time.sleep(RETRY_DELAY)

    if deployments is None:

        logger.error(
            "Failed to fetch deployments after %d attempts.",
            MAX_RETRIES
        )

        return

    logger.info("Deployments Found : %d", len(deployments))

    # -------------------------------------------------------
    # Process Each Deployment
    # -------------------------------------------------------

    for deployment in deployments:

        deployment_start = time.perf_counter()

        namespace = deployment["namespace"]
        deployment_name = deployment["name"]

        logger.info("-" * 70)
        logger.info("Deployment : %s", deployment_name)
        logger.info("Namespace  : %s", namespace)
        logger.info("Collecting recommendation...")

        request_successful = False

        for attempt in range(1, MAX_RETRIES + 1):

            logger.info("Attempt %d/%d", attempt, MAX_RETRIES)

            try:

                response = requests.post(
                    f"{BASE_URL}/collect/{namespace}/{deployment_name}",
                    timeout=30
                )

                duration = time.perf_counter() - deployment_start

                if response.status_code == 200:

                    success += 1
                    request_successful = True

                    logger.info(
                        "HTTP Status : %d OK",
                        response.status_code
                    )

                    logger.info("Status      : SUCCESS")
                    logger.info("Duration    : %.2f sec", duration)

                    break

                else:

                    logger.warning(
                        "HTTP Status : %d",
                        response.status_code
                    )

                    logger.warning(
                        "Response : %s",
                        response.text
                    )

            except Exception as e:

                logger.warning(
                    "Request failed : %s",
                    str(e)
                )

            if attempt < MAX_RETRIES:

                logger.info(
                    "Retrying in %d seconds...",
                    RETRY_DELAY
                )

                time.sleep(RETRY_DELAY)

        if not request_successful:

            failed += 1

            duration = time.perf_counter() - deployment_start

            logger.error("Status      : FAILED")
            logger.error(
                "All %d retry attempts failed.",
                MAX_RETRIES
            )
            logger.error("Duration    : %.2f sec", duration)

    # -------------------------------------------------------
    # Summary
    # -------------------------------------------------------

    total_time = time.perf_counter() - overall_start

    logger.info("=" * 70)
    logger.info("Summary")
    logger.info("=" * 70)
    logger.info("Deployments Processed : %d", len(deployments))
    logger.info("Successful            : %d", success)
    logger.info("Failed                : %d", failed)
    logger.info("Total Execution Time  : %.2f sec", total_time)
    logger.info("")
    logger.info("Recommendation Collector Finished")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()