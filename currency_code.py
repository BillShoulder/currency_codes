"""
Show the ISO 4217 currency code and currency for the given country.

Usage:
    currency_code [Options] <country>

[Options]
    --iso:  Interpret <country> as an ISO currency code and show the corresponding country and currency.
"""

###############################################################################################################################################################
#
#       Import
#
###############################################################################################################################################################

import argparse
import typing

from currency_codes import FX_CODES
from country_codes import COUNTRY_CODES


###############################################################################################################################################################
#
#       country_from_currency_iso
#
###############################################################################################################################################################

def country_from_currency_iso(iso: str) -> int:
    if (country := FX_CODES.country_from_currency_iso(iso)) is None:
        print(f"Unknown currency ISO: {iso}")
        return -1
    if country in COUNTRY_CODES.codes:
        country = COUNTRY_CODES[country]
    print(f"{iso}: {country} ({FX_CODES.currency_from_currency_iso(iso)})")
    return 0


###############################################################################################################################################################
#
#       currency_iso_from_country
#
###############################################################################################################################################################

def currency_iso_from_country(country: str) -> int:
    """  """
    # First see if we have been given a valid country code.
    country_code = country
    if COUNTRY_CODES.country_from_iso(country) is None:
        # If not, see if we have a country name from which a code can be obtained.
        if (country_match := COUNTRY_CODES.match_country(country)) is not None:
            country_code = COUNTRY_CODES.iso_from_country(country_match)
        # Else assume we have been given a special currency holding entity (like the IMF).
    if (iso := FX_CODES.currency_iso_from_country(country_code)) is None:
        print(f"Unknown country or organization: {country}")
        return -1
    print(f"{country}: {iso} ({FX_CODES.currency_from_currency_iso(iso)})")
    return 0


###############################################################################################################################################################
#
#       __main__
#
###############################################################################################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso", action="store_true", help="Interpret the argument as a currency ISO and show the corresponding currency.")
    parser.add_argument("query", type=str, help="The ISO currency code or name of the currency to convert.")
    args = parser.parse_args()   
    exit(country_from_currency_iso(args.query) if args.iso else currency_iso_from_country(args.query))
