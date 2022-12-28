# Company Info, Tools for using the Companies House API, by Martin Keegan
#
# To the extent (if any) permissible by law, Copyright (C) 2022  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify it under
# the terms of the Apache Software Licence v2.0.

from delayed_client import DelayedClient

def valid_rtms(args):
    """Return a stream of tuples representing valid RTM companies.

    The tuples are of the form:
    (registration number, date of incorporation, postcode, company name)
    """

    host = args.host
    client = DelayedClient(args.api_key)
    url = f"https://{host}/advanced-search/companies"
    common_params = {
            "company_name_includes": "RTM COMPANY"
    }
    start_index = args.start_index or 0

    rtm_companies = client.iter_results(url, common_params, start_index)

    for start_index, company in rtm_companies:
        status = company["company_status"]
        company_name = company["company_name"]

        # ensure we are only dealing with active companies
        if status not in ["active"]:
            continue

        assert valid_rtm_name(company_name), company_name

        # check there's a valid postcode for the registered office
        if not valid_postcode(company):
            continue

        yield (
            company["company_number"],
            company["date_of_creation"],
            company["registered_office_address"]["postal_code"],
            company["company_name"]
        )

def valid_rtm_name(company_name):
    """Returns true if company_name, once normalised, is a reasonable
    name for an RTM company.

    The policy adopted is fairly permissive."""

    # remove punctuation (etc) from name
    name = standardise_name(company_name)

    # check the company name actually is an RTM company name
    name_ok = False
    for suffix in suffixes:
        if name.endswith(suffix):
            name_ok = True
            break
    return name_ok

def standardise_name(company_name):
    """Return a modified version of company_name, replacing some
    material with synonyms and omitting some punctuation.

    See the end of this source file for a list of the textual substitutions
    applied."""
    name = company_name

    for before, after in substitutions:
        name = name.replace(before, after)

    return name

def valid_postcode(company):
    """Return a boolean about whether the company data contains a
       postcode member.  Does not care whether it's really a UK
       postcode, only whether it is there.

       Companies House occasionally fails to record postcodes from
       the IN01 or similar documentation, and this is reflected in the
       data that comes out of the API."""

    if "registered_office_address" not in company:
        return False
    if "postal_code" not in company["registered_office_address"]:
        return False
    return True

#############################################################################

# (before, after)
substitutions = [
    ("  ", " "),
    (" LTD LTD", " LTD"),
    (" LTD", " LIMITED"),
    (" MANAGEMENT", ""),
    ("(", ""),
    (")", ""),
    (".", ""),
    ('"', "")
]

# please excuse this rather hacky literal list
suffixes = (
"""RTM COMPANY LIMITED
RTM COMPANY BLOCK 3 LIMITED
RTM COMPANY BLOCK 1 LIMITED
RTM COMPANY BRISTOL LIMITED
COMPANY RTM LIMITED
RTM COMPANY 2011 LIMITED
RTM COMPANY 2012 LIMITED
RTM MARBLE ARCH COMPANY LIMITED
RTM COMPANY BLOCK 4 LIMITED
RTM COMPANY BLOCK 2 LIMITED
RTM COMPANY TROWBRIDGE LIMITED
RTM COMPANY
RTM FC COMPANY LIMITED
RTM COMPANY EDGEHILL LIMITED
RTM NO3 COMPANY LIMITED"""
).split("\n")
