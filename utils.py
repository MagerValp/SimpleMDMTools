import re


def capitalize(s):
    special_caps = {
        "and": "and",
        "but": "but",
        "for": "for",
        "or": "or",
        "nor": "nor",
        "the": "the",
        "a": "a",
        "an": "an",
        "to": "to",
        "as": "as",
        "dep": "DEP",
        "csr": "CSR",
        "filevault": "FileVault",
        "os": "OS",
    }
    try:
        return special_caps[s.lower()]
    except KeyError:
        return s.capitalize()

def title_caps(s):
    parts = list(x.lower() for x in s.split())
    return " ".join(capitalize(x) for x in parts)

def cap_resource(name):
    parts = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()
    return title_caps(" ".join(parts))

def cap_action(name):
    return title_caps(name.replace("_", " "))
