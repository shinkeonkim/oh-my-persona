from dataclasses import dataclass
from typing import Optional


@dataclass
class DartCompanyData:
  corp_code: str
  corp_name: str
  stock_code: str
  corp_eng_name: Optional[str] = None
