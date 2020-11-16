"""
Mapping ISO 4217 currency symbols to countries and currencies.
"""

###############################################################################################################################################################
#
#       Import
#
###############################################################################################################################################################

from collections import defaultdict
from pathlib import Path
from functools import cached_property
import json
import typing

from requests.structures import CaseInsensitiveDict


###############################################################################################################################################################
#
#       Global
#
###############################################################################################################################################################

SCRIPT_DIR = Path(__file__).resolve().parent


###############################################################################################################################################################
#
#       FxCodes
#
###############################################################################################################################################################

class FxCodesException(Exception): pass


class FxCodes:
    """ Map country names to ISO 4217 currency symbols and currencies. """

    # Indexes into the raw json data.
    JSON_CURRENCY_ISO   = "AlphabeticCode"
    JSON_CURRENCY       = "Currency"
    JSON_COUNTRY        = "Entity"
    JSON_CURRENCY_OWNER = "Owner"
    JSON_CURRENCY_MAIN  = "Primary"

    @cached_property
    def data_file(self) -> Path:
        """ The path to the file containg the primary ISO 4217 currency code data. """
        return SCRIPT_DIR/"iso_4217_currency_codes.json"

    @cached_property
    def json_data(self) -> json:
        """ The contents of the json datafile as a list of maps. """
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        return tuple(entry for entry in data if entry.get(self.JSON_CURRENCY_ISO) is not None)

    @cached_property
    def currencies(self) -> set[str]:
        """ A set containing all known currency names. """
        return set(entry[self.JSON_CURRENCY] for entry in self.json_data)

    @cached_property
    def currency_iso_codes(self) -> set[str]:
        """ A set containing all known ISO currency codes. """
        return set(entity[self.JSON_CURRENCY_ISO] for entity in self.json_data)

    @cached_property
    def countries(self) -> set[str]:
        """ A set containing all known ISO country codes or country names. """
        return set(entry[self.JSON_COUNTRY] for entry in self.json_data)

    @cached_property
    def currency_to_currency_iso_map(self) -> CaseInsensitiveDict:
        """ A case insensitive map of currency names to currency ISOs. """
        return {entry[self.JSON_CURRENCY].upper(): entry[self.JSON_CURRENCY_ISO] for entry in self.json_data}

    @cached_property
    def currency_iso_to_currency_map(self) -> dict[str, str]:
        """ A map of currency ISOs to currency names. """
        return {entry[self.JSON_CURRENCY_ISO]: entry[self.JSON_CURRENCY] for entry in self.json_data}

    @cached_property
    def country_to_currency_isos_map(self):
        country_to_currency_isos_map = defaultdict(set)
        for entry in self.json_data:
            country_to_currency_isos_map[entry[self.JSON_COUNTRY].upper()].add(entry[self.JSON_CURRENCY_ISO])
        return country_to_currency_isos_map

    @cached_property
    def currency_iso_to_countries_map(self):
        currency_iso_to_countries_map = defaultdict(set)
        for entry in self.json_data:
            currency_iso_to_countries_map[entry[self.JSON_CURRENCY_ISO]].add(entry[self.JSON_COUNTRY])
        return currency_iso_to_countries_map

    @cached_property
    def currency_iso_to_owner_country_map(self):
        return {entry[self.JSON_CURRENCY_ISO]: entry[self.JSON_COUNTRY] for entry in self.json_data if entry.get(self.JSON_CURRENCY_OWNER)}

    @cached_property
    def country_to_primary_currency_iso_map(self):
        return {entry[self.JSON_COUNTRY].upper(): entry[self.JSON_CURRENCY_ISO] for entry in self.json_data if entry.get(self.JSON_CURRENCY_MAIN)}

    def currency_iso_from_currency(self, currency: str) -> str:
        """ Return the ISO currency code for the named currency. """
        return self.currency_to_currency_iso_map.get(currency.upper())

    def currency_from_currency_iso(self, iso: str) -> str:
        """ Return the name of the currency corresponding to the ISO currency code. """
        return self.currency_iso_to_currency_map.get(iso.upper())

    def currency_isos_from_country(self, country: str) -> set[str]:
        """ Return all ISO currency codes for the currencies used by country. """
        isos = self.country_to_currency_isos_map.get(country.upper())
        return set() if isos is None else isos

    def currency_iso_from_country(self, country: str) -> str:
        """ Return the primary ISO currency code for the currency used by country. """
        currency_isos = self.currency_isos_from_country(country)
        if (count := len(currency_isos)) == 0:
            return None
        elif count == 1:
            return next(iter(currency_isos))
        elif (primary := self.country_to_primary_currency_iso_map.get(country.upper())) is not None:
            return primary
        raise FxCodesException(f"No unique currency ISO for country ISO '{country}' possibilities: {currency_isos}")
        
    def countries_from_currency_iso(self, currency_iso: str) -> list[str]:
        """ Return all countries using an ISO currency code. """
        countries = self.currency_iso_to_countries_map.get(currency_iso.upper())
        return set() if countries is None else countries

    def country_from_currency_iso(self, currency_iso: str) -> str:
        """ Return the primary country or collective owning an ISO currency code. """
        countries = self.countries_from_currency_iso(currency_iso)
        if (count := len(countries)) == 0:
            return None
        elif count == 1:
            return next(iter(countries))
        elif (owner := self.currency_iso_to_owner_country_map.get(currency_iso.upper())):
            return owner
        raise FxCodesException(f"No unique ownership for ISO '{currency_iso}' used by: {countries}")

    def __getitem__(self, currency_iso: str) -> str:
        """ Return the primary owner of an ISO currency code. """
        return self.country_from_currency_iso(currency_iso)


###############################################################################################################################################################
#
#       FxCodes
#
###############################################################################################################################################################

FX_CODES = FxCodes()
