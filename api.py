"""
This module contains logic to extract data from Adzuna API
"""
import json
import logging
import time
from typing import List, Optional, Union

from httpx import Client
from rich import print
from tqdm import tqdm

from data_models import AdzunaAd, model_adzuna_ad_data
from logger_config import setup_logging
from utils import configure, create_client, get_date, timer


# Instanciating logger
setup_logging()
logger = logging.getLogger("rich")


def dump_adzuna_ads(ads: List[AdzunaAd]) -> None:
    """Dump data selected from Adzuna API response in a JSON file in data folder"""
    today = get_date()
    dump_path = f"adzuna_ads_{today}.json"
    # Converting AdzunaAd objects to dumpable dicts with pydantic method
    dumpable_ads = [ad.model_dump() for ad in ads]
    with open(dump_path, "w", encoding="utf-8") as dump_file:
        # `ensure_ascii=False` to force display of non-ascii characters in JSON
        json.dump(dumpable_ads, dump_file, indent=4, ensure_ascii=False)
    logger.info(f"{dump_path} dumped!")


def get_adzuna_ads_page(
    client: Client,
    page: int,
    what: str = "data",
    where: str = "Lille",
    distance: int = 10,
    cat_tag: Optional[str] = None,
    get_count: bool = False,
) -> Union[int, List[dict]]:
    """
    Helper function in the process to get ads.
    Will either:
    - Get the 50 results of one page from Adzuna API if get_count is False (default).
    - Get the count of ads corresponding to the current search if get_count is True.
    """
    url = f"{conf['api_url']}/jobs/fr/search/{page}"
    custom_params = {
        "app_id": conf["api_id"],
        "app_key": conf["api_key"],
        "what": what,
        "where": where,
        "distance": distance,
        "results_per_page": 50,
        "category": cat_tag if cat_tag else None,
    }

    resp = client.get(url, params=custom_params)
    resp.raise_for_status()

    return resp.json()["count"] if get_count else resp.json()["results"]


@timer
def get_adzuna_ads(
    what: str = "data",
    where: str = "Lille",
    distance: int = 10,
    cat_tag: str = "it-jobs",
) -> List[AdzunaAd]:
    """
    Requesting Adzuna API to get as much as possible relevant daily ads.
    Experience showed that only 100 pertinent pages were generated.
    Parameters
    ----------
        - what: a topic to explore, default: 'data'
        - where: the location around which the search will be centered, default: 'Lille'
        - distance: the radius of the disk within the search will be performed, default: 10
        - cat_tag: a custom category tag from Adzuna (read the docs), default: 'it-jobs'
    Returns
    -------
        A 2-tuple with:
        - A list of AdzunaAd objects
        - The number of remaining daily calls
    """
    # Logging arguments to file
    logger.warning(f"{what=}, {where=}, {distance=}, {cat_tag=}")

    cli = create_client(conf["ua"])
    adzuna_ads = []
    errors = 0

    # Getting the ads count
    n_ads = get_adzuna_ads_page(cli, 1, what, where, distance, cat_tag, get_count=True)
    logger.warning(f"Number of ads to get: {n_ads}")
    n_pages = n_ads // 50 + 1
    logger.warning(f"Number of pages to proceed: {n_pages}")

    for page in range(1, n_pages + 1):
        if page != 1 and page % 25 == 1:
            logger.info("*** WAITING FOR 60 S ***")
            # Going around minute rate limit
            for _ in tqdm(range(60), desc="Waiting...", ascii=False):
                time.sleep(1)
        try:
            # Requesting
            new_ads = get_adzuna_ads_page(cli, page, what, where, distance, cat_tag)
            logger.info(f"Page {page} PROCESSED")
        except BaseException as e:
            logger.error(f"{type(e)}: Exception {e} occured! on page {page}")
            errors += 1
        else:
            adzuna_ads.extend(new_ads)

    # FULL PROCESS SUM-UP
    logger.warning(f"{n_pages - errors} pages succesfully processed.")

    return model_adzuna_ad_data(adzuna_ads)


if __name__ == "__main__":
    conf = configure()
    ads = get_adzuna_ads()
    # Get dump
    dump_adzuna_ads(ads)
    # cli = create_client(conf['ua'])
    # res = get_adzuna_ads_page(cli, 1, cat_tag='it-jobs', get_count=True)

    print("Done!")
