#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import io
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import re


DOCS_URL = "https://api.simplemdm.com"

SKIP_SECTIONS = set([
    "Introduction",
    "Authentication",
    "Errors",
    "Pagination",
    "Webhooks",
])


def parse_table(table):
    headers = table.thead.find_all("th")
    if (headers[0].string, headers[1].string) != ("Argument", "Description"):
        return None
    options = list()
    for tr in table.tbody.find_all("tr"):
        name, description = list(x.get_text() for x in tr.find_all("td"))
        options.append((name, description))
    return options


def parse_url(url):
    args = []
    for m in re.finditer(r"{(?P<arg>[^}]+)}", url):
        args.append(m.group("arg"))
    path = url[len("https://a.simplemdm.com/api/v1"):]
    return path, args


def parse_action(resource, action, tags):
    options = None
    description = None
    method = None
    for tag in tags:
        if tag.name == "p" and tag.code:
            request = tag.code.get_text()
            method, _, url = request.partition(" ")
            path, args = parse_url(url)
        elif tag.name == "table":
            options = parse_table(tag)
        elif tag.name == "p" and not tag.code:
            try:
                description += "\n" + tag.get_text()
            except TypeError:
                description = tag.get_text()
        elif tag.name == "div" and tag.attrs["class"] == ["highlight"]:
            pass
        elif tag.name == "h3":
            pass
        elif tag.name == "aside":
            pass
        elif tag.name:
            print(tag.name, tag.attrs, tag.get_text())
    if not method and description.startswith("Refer to"):
        return
    print(f"\n{resource} - {action}")
    print(f"Desc: {description}")
    print(f"Method: {method}")
    print(f"Path: {path}")
    print(f"Args: {', '.join(args)}")
    print("Options:")
    try:
        for name, desc in options:
            print(f"    {name}: {desc}")
    except TypeError:
        pass


def parse_soup(soup):
    content = soup.find("div", {"class": "content"})
    resource = None
    for elem in content.children:
        if elem.name == "h1":
            resource = elem.string
            continue
        if resource in SKIP_SECTIONS:
            continue
        if elem.name == "h2":
            action = elem.string
            tags = []
            for sibling in elem.next_siblings:
                if sibling.name in ["h1", "h2"]:
                    break
                elif sibling.name:
                    tags.append(sibling)
            parse_action(resource, action, tags)
            continue
#        if elem.name:
#            print(elem.name, elem.attrs)


def get_file_soup(path):
    with io.open(path, "rb") as f:
        return BeautifulSoup(f.read(), "html.parser")

def get_soup():
    resp = requests.get(DOCS_URL)
    return BeautifulSoup(resp.content, "html.parser")


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Verbose output.")
    p.add_argument("html", nargs="?")
    args = p.parse_args(argv[1:])
    
    if args.html:
        soup = get_file_soup(args.html)
    else:
        soup = get_soup()
    parse_soup(soup)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

