# Company Info, Tools for using the Companies House API, by Martin Keegan
#
# To the extent (if any) permissible by law, Copyright (C) 2022  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify it under
# the terms of the Apache Software Licence v2.0.

from delayed_client import DelayedClient

def valid_rtms(args):
    host = args.host
    dc = DelayedClient(args.api_key)
    url = f"https://{host}/advanced-search/companies"
    common_params = {
            "company_name_includes": "RTM COMPANY"
    }
    start_index = args.start_index or 0

    rtm_companies = dc.iter_results(url, common_params, start_index)

    for start_index, c in rtm_companies:
        status = c["company_status"]
        company_name = c["company_name"]

        # ensure we are only dealing with active companies
        if status not in ["active"]:
            continue

        assert valid_rtm_name(company_name), company_name

        # check there's a valid postcode for the registered office
        if not valid_postcode(c):
            continue

        yield (
            c["company_number"],
            c["date_of_creation"],
            c["registered_office_address"]["postal_code"],
            c["company_name"]
        )

def valid_rtm_name(company_name):
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
    name = company_name

    for before, after in substitutions:
        name = name.replace(before, after)

    return name

def valid_postcode(company):
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
