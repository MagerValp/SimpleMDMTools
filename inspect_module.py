#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import io
import sys
import argparse
import inspect
import re


def parse_sig(sig):
    args = []
    options = []
    for name, param in sig.parameters.items():
        if param.default == inspect.Parameter.empty:
            args.append(name)
        else:
            options.append((name, param.default))
    return args, options


def cap_resource(name):
    parts = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()
    return " ".join(x.capitalize() for x in parts)


def cap_method(name):
    return name.replace("_", " ").capitalize()


def sort_items(items):
    for index, item in enumerate(items):
        name = item[0]
        prev_name = items[index - 1][0]
        if name.endswith("s"):
            if prev_name in (name[:-1] + "Groups", name[:-1] + "Jobs"):
                items[index], items[index - 1] = items[index - 1], items[index]


def find_request_method(func):
    requests = [
        ("self.get_data(", "GET"),
        ("self.get_raw_content(", "GET"),
        ("self.patch_data(", "PATCH"),
        ("self.post_data(", "POST"),
        ("self.put_data(", "PUT"),
        ("self.delete_data(", "DELETE"),
    ]
    source = inspect.getsource(func)
    for request, method in requests:
        if request in source:
            return method


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Verbose output.")
    p.add_argument("module")
    args = p.parse_args(argv[1:])
    
    sys.path.insert(0, args.module)
    import SimpleMDMpy
    session = SimpleMDMpy.Session(api_key="DUMMY")
    cls_name = session.__class__.__name__
    items = list(session.__dict__.items())
    sort_items(items)
    for resource, obj in items:
        #print(f"{cls_name}.{resource}\t{obj}")
        for name, method in inspect.getmembers(obj):
            if name not in obj.__class__.__dict__:
                continue
            if name.startswith("_"):
                continue
            if inspect.ismethod(method):
                annotation = ""
                if hasattr(method, "__is_legacy"):
                    if method.__replaced_by:
                        annotation += f" (legacy, replaced by {method.__replaced_by})"
                    else:
                        annotation += " (legacy)"
                print(f"\n{cap_resource(resource)} - {cap_method(name)}{annotation}")
                docs = inspect.getdoc(method)
                if docs:
                    print(f"Desc: {inspect.cleandoc(docs)}")
                else:
                    print("Desc: None")
                req_method = find_request_method(method)
                print(f"Method: {req_method}")
                sig = inspect.signature(method)
                print(f"Call: {resource}.{name}{sig}")
                args, options = parse_sig(sig)
                print(f"Args: {', '.join(args)}")
                print("Options:")
                try:
                    for name, desc in options:
                        print(f"    {name}: {desc}")
                except TypeError:
                    pass

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

