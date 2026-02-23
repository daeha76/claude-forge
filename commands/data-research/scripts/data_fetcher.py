"""
Unified Data Fetcher Module

Provides standardized access to multiple economic data sources:
- FRED (Federal Reserve Economic Data)
- ECOS (Bank of Korea Economic Statistics)
- KOSIS (Korean Statistical Information Service)
- World Bank
- OECD

All fetchers return pd.DataFrame with columns: date, value, series_id, source.
"""

import os
from typing import Optional, List

import pandas as pd
import requests


# ============================================================
# Utility Functions
# ============================================================

def standardize_dataframe(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    source_name: str,
    series_id: str,
) -> pd.DataFrame:
    """Create a new standardized DataFrame from source data.

    Returns a new DataFrame with columns: date, value, series_id, source.
    Does not mutate the input DataFrame.
    """
    result = pd.DataFrame({
        "date": pd.to_datetime(df[date_col], errors="coerce"),
        "value": pd.to_numeric(df[value_col], errors="coerce"),
        "series_id": series_id,
        "source": source_name,
    })
    return result.dropna(subset=["date", "value"]).reset_index(drop=True)


def merge_dataframes(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate multiple standardized DataFrames into one.

    Returns a new DataFrame sorted by date.
    """
    if not dfs:
        return pd.DataFrame(columns=["date", "value", "series_id", "source"])
    merged = pd.concat(dfs, ignore_index=True)
    return merged.sort_values("date").reset_index(drop=True)


# ============================================================
# FREDFetcher
# ============================================================

class FREDFetcher:
    """Fetch economic data from the FRED API.

    Requires FRED_API_KEY environment variable.
    """

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("FRED_API_KEY")
        if not self.api_key:
            raise ValueError(
                "FRED API key required. Set FRED_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def fetch(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetch observations for a FRED series.

        Args:
            series_id: FRED series ID (e.g. 'GDP', 'UNRATE', 'FEDFUNDS').
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            Standardized DataFrame with columns: date, value, series_id, source.
        """
        params: dict = {
            "api_key": self.api_key,
            "series_id": series_id,
            "file_type": "json",
        }
        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"FRED API request failed for '{series_id}': {e}") from e

        observations = data.get("observations", [])
        if not observations:
            return pd.DataFrame(columns=["date", "value", "series_id", "source"])

        raw_df = pd.DataFrame(observations)
        return standardize_dataframe(raw_df, "date", "value", "FRED", series_id)


# ============================================================
# ECOSFetcher
# ============================================================

class ECOSFetcher:
    """Fetch economic data from Bank of Korea ECOS API.

    Requires ECOS_API_KEY environment variable.

    Key stat codes:
        722Y001 - Base interest rate (기준금리)
        731Y004 - Exchange rates (환율)
        200Y001 - GDP
        901Y009 - CPI (소비자물가지수)
    """

    BASE_URL = "https://ecos.bok.or.kr/api/StatisticSearch"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("ECOS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ECOS API key required. Set ECOS_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def fetch(
        self,
        stat_code: str,
        period_type: str,
        start_date: str,
        end_date: str,
        item_code1: str = "0000001",
        item_code2: str = "",
    ) -> pd.DataFrame:
        """Fetch data from ECOS.

        Args:
            stat_code: Statistics table code (e.g. '722Y001').
            period_type: Period type - 'A' (annual), 'Q' (quarterly), 'M' (monthly).
            start_date: Start date (format depends on period_type: YYYY, YYYYQQ, YYYYMM).
            end_date: End date.
            item_code1: Item code 1 (default '0000001').
            item_code2: Item code 2 (optional).

        Returns:
            Standardized DataFrame with columns: date, value, series_id, source.
        """
        url_parts = [
            self.BASE_URL,
            self.api_key,
            "json", "kr", "1", "100",
            stat_code, period_type,
            start_date, end_date,
            item_code1,
        ]
        if item_code2:
            url_parts.append(item_code2)

        url = "/".join(url_parts)

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"ECOS API request failed for '{stat_code}': {e}"
            ) from e

        stat_search = data.get("StatisticSearch")
        if not stat_search:
            error_msg = data.get("RESULT", {}).get("MESSAGE", "Unknown error")
            raise ValueError(f"ECOS API error for '{stat_code}': {error_msg}")

        rows = stat_search.get("row", [])
        if not rows:
            return pd.DataFrame(columns=["date", "value", "series_id", "source"])

        raw_df = pd.DataFrame(rows)
        series_label = f"ECOS:{stat_code}"
        return standardize_dataframe(raw_df, "TIME", "DATA_VALUE", "ECOS", series_label)


# ============================================================
# KOSISFetcher
# ============================================================

class KOSISFetcher:
    """Fetch data from KOSIS (Korean Statistical Information Service).

    Requires KOSIS_API_KEY environment variable.

    Key tables:
        DT_1B040A3 - Population (인구)
        DT_1K52A01 - Industry (산업)
    """

    BASE_URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("KOSIS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "KOSIS API key required. Set KOSIS_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def fetch(
        self,
        org_id: str,
        tbl_id: str,
        itm_id: str,
        obj_l1: str,
        obj_l2: str = "",
        start_date: str = "2000",
        end_date: str = "2025",
        prd_se: str = "Y",
    ) -> pd.DataFrame:
        """Fetch data from KOSIS.

        Args:
            org_id: Organization ID (e.g. '101' for 통계청).
            tbl_id: Table ID (e.g. 'DT_1B040A3').
            itm_id: Item ID.
            obj_l1: Object level 1 code.
            obj_l2: Object level 2 code (optional).
            start_date: Start period (e.g. '2000').
            end_date: End period (e.g. '2025').
            prd_se: Period type - 'Y' (yearly), 'M' (monthly), 'Q' (quarterly).

        Returns:
            Standardized DataFrame with columns: date, value, series_id, source.
        """
        params: dict = {
            "method": "getList",
            "apiKey": self.api_key,
            "itmId": itm_id,
            "objL1": obj_l1,
            "format": "json",
            "jsonVD": "Y",
            "prdSe": prd_se,
            "startPrdDe": start_date,
            "endPrdDe": end_date,
            "orgId": org_id,
            "tblId": tbl_id,
        }
        if obj_l2:
            params["objL2"] = obj_l2

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"KOSIS API request failed for '{tbl_id}': {e}"
            ) from e

        if not isinstance(data, list) or not data:
            raise ValueError(f"KOSIS API returned unexpected response for '{tbl_id}'")

        raw_df = pd.DataFrame(data)
        series_label = f"KOSIS:{org_id}/{tbl_id}"
        return standardize_dataframe(raw_df, "PRD_DE", "DT", "KOSIS", series_label)


# ============================================================
# WorldBankFetcher
# ============================================================

class WorldBankFetcher:
    """Fetch data from the World Bank using the wbdata library.

    No API key required.

    Key indicators:
        NY.GDP.MKTP.CD  - GDP (current US$)
        SP.POP.TOTL     - Total population
        NY.GDP.PCAP.CD  - GDP per capita (current US$)
        FP.CPI.TOTL.ZG  - Inflation, consumer prices (annual %)

    Country codes:
        KR (Korea), US, JP (Japan), CN (China), DE (Germany)
    """

    def fetch(
        self,
        indicator: str,
        country: str = "KR",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch World Bank indicator data.

        Args:
            indicator: World Bank indicator code (e.g. 'NY.GDP.MKTP.CD').
            country: ISO country code (e.g. 'KR', 'US').
            start_year: Start year filter.
            end_year: End year filter.

        Returns:
            Standardized DataFrame with columns: date, value, series_id, source.
        """
        try:
            import wbdata
        except ImportError as e:
            raise ImportError(
                "wbdata library required. Install with: pip install wbdata"
            ) from e

        try:
            import datetime

            fetch_kwargs: dict = {
                "indicators": {indicator: "value"},
                "country": country,
            }
            if start_year and end_year:
                fetch_kwargs["date"] = (
                    datetime.datetime(start_year, 1, 1),
                    datetime.datetime(end_year, 12, 31),
                )

            raw_df = wbdata.get_dataframe(**fetch_kwargs)
        except Exception as e:
            raise ConnectionError(
                f"World Bank API request failed for '{indicator}' ({country}): {e}"
            ) from e

        if raw_df.empty:
            return pd.DataFrame(columns=["date", "value", "series_id", "source"])

        # wbdata returns DataFrame with date index; reset for standardization
        working_df = raw_df.reset_index()

        # The index name is 'date' and the value column is 'value'
        date_col = "date" if "date" in working_df.columns else working_df.columns[0]
        value_col = "value" if "value" in working_df.columns else working_df.columns[-1]

        series_label = f"WB:{indicator}:{country}"
        return standardize_dataframe(working_df, date_col, value_col, "WorldBank", series_label)


# ============================================================
# OECDFetcher
# ============================================================

class OECDFetcher:
    """Fetch data from the OECD using the pandasdmx library.

    No API key required.

    Key datasets:
        QNA - Quarterly National Accounts
        MEI - Main Economic Indicators
    """

    def fetch(
        self,
        dataset: str,
        key: str = "",
        params: Optional[dict] = None,
    ) -> pd.DataFrame:
        """Fetch OECD data via SDMX.

        Args:
            dataset: OECD dataset ID (e.g. 'QNA', 'MEI').
            key: Data key/filter string for the dataset.
            params: Additional request parameters (e.g. startPeriod, endPeriod).

        Returns:
            Standardized DataFrame with columns: date, value, series_id, source.
        """
        try:
            import pandasdmx as sdmx
        except ImportError as e:
            raise ImportError(
                "pandasdmx library required. Install with: pip install pandasdmx"
            ) from e

        request_params = params or {}

        try:
            oecd = sdmx.Request("OECD")
            response = oecd.data(dataset, key=key, params=request_params)
            raw_df = response.to_pandas()
        except Exception as e:
            raise ConnectionError(
                f"OECD SDMX request failed for '{dataset}': {e}"
            ) from e

        if isinstance(raw_df, pd.Series):
            raw_df = raw_df.reset_index()
            raw_df.columns = [*raw_df.columns[:-1], "value"]

        if raw_df.empty:
            return pd.DataFrame(columns=["date", "value", "series_id", "source"])

        working_df = raw_df.reset_index() if isinstance(raw_df.index, pd.MultiIndex) else raw_df.copy()

        # Identify the time/period column
        time_col = None
        for candidate in ["TIME_PERIOD", "TIME", "PERIOD", "time_period"]:
            if candidate in working_df.columns:
                time_col = candidate
                break
        if time_col is None:
            time_col = working_df.columns[-2] if len(working_df.columns) >= 2 else working_df.columns[0]

        value_col = "value" if "value" in working_df.columns else working_df.columns[-1]

        series_label = f"OECD:{dataset}"
        if key:
            series_label = f"OECD:{dataset}:{key}"

        return standardize_dataframe(working_df, time_col, value_col, "OECD", series_label)


# ============================================================
# Main - Test with WorldBankFetcher (no API key needed)
# ============================================================

if __name__ == "__main__":
    print("Testing WorldBankFetcher - Korea GDP (NY.GDP.MKTP.CD)...")
    try:
        wb = WorldBankFetcher()
        df = wb.fetch(
            indicator="NY.GDP.MKTP.CD",
            country="KR",
            start_year=2015,
            end_year=2023,
        )
        print(f"\nFetched {len(df)} records:")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")
