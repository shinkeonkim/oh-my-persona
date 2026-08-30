"""
Stock Info KRX Client

Client for fetching detailed stock information from KRX API
"""

import logging
import time
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class StockInfoKRXClient:
  """KRX Stock Info Client

    Fetches detailed stock information from KRX API.
    """

  def __init__(self):
    self.url = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    self.session = requests.Session()
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-Requested-With": "XMLHttpRequest",
      "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader",
      "Origin": "https://data.krx.co.kr",
    }
    self.timeout = 30
    self.max_retries = 3
    self.backoff_seconds = 2

  def fetch_stock_info(
    self,
    market_id: str = "ALL",
    share: str = "1",
  ) -> List[Dict]:
    """Fetch stock information

        Args:
            market_id: Market ID (ALL, STK=KOSPI, KSQ=KOSDAQ)
            share: Include shares (1=include, 0=exclude)

        Returns:
            List[Dict]: Stock information list
                - ISU_CD: Stock code (12-digit standard code)
                - ISU_SRT_CD: Short code (6-digit)
                - ISU_NM: Stock name
                - ISU_ABBRV: Stock name abbreviation
                - ISU_ENG_NM: English stock name
                - LIST_DD: Listing date
                - MKT_TP_NM: Market type name
                - SECUGRP_NM: Securities group name
                - SECT_TP_NM: Sector name
                - KIND_STKCERT_TP_NM: Stock certificate type name
                - PARVAL: Par value
                - LIST_SHRS: Listed shares

        Raises:
            requests.RequestException: Request failed
        """
    # Split markets for ALL option
    if market_id == "ALL":
      markets = ["STK", "KSQ", "KNX"]
    else:
      markets = [market_id]

    all_results = []
    for mkt in markets:
      payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT01901",
        "locale": "ko_KR",
        "mktId": mkt,
        "share": share,
        "csvxls_isNo": "false",
      }

      for attempt in range(1, self.max_retries + 1):
        try:
          logger.info(f"Fetching stock info (attempt {attempt}/{self.max_retries}): market={mkt}")

          response = self.session.post(
            self.url,
            data=payload,
            headers=self.headers,
            timeout=self.timeout,
          )
          response.raise_for_status()

          data = response.json()

          # Validate response data
          if not isinstance(data, dict):
            raise ValueError(f"Unexpected response type: {type(data)}")

          output = data.get("OutBlock_1", [])
          logger.info(f"Fetched {len(output)} stock info entries (market={mkt})")

          all_results.extend(output)
          break  # Success, exit retry loop

        except requests.RequestException as e:
          logger.warning(f"Stock info fetch failed (attempt {attempt}/{self.max_retries}): {e}")
          if attempt < self.max_retries:
            time.sleep(self.backoff_seconds)
          else:
            logger.error(f"Stock info fetch final failure (market={mkt}): {e}")
            raise

        except (ValueError, KeyError) as e:
          logger.error(f"Stock info response parsing failed (market={mkt}): {e}")
          raise

      # Sleep between markets
      time.sleep(1)

    logger.info(f"Total stock info collected: {len(all_results)} entries")
    return all_results

  def close(self):
    """Close session"""
    if self.session:
      self.session.close()

  def __enter__(self):
    """Context manager entry"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit"""
    self.close()
