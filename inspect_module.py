#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import io
import sys
import argparse
import inspect

import utils


def parse_sig(sig):
    args = []
    options = []
    for name, param in sig.parameters.items():
        if param.default == inspect.Parameter.empty:
            args.append(name)
        else:
            options.append((name, param.default))
    return args, options


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
    actions = {}
    for resource, obj in items:
        #print(f"{cls_name}.{resource}\t{obj}")
        for name, method in sorted(inspect.getmembers(obj)):
            if name not in obj.__class__.__dict__:
                continue
            if name.startswith("_"):
                continue
            if inspect.ismethod(method):
                output = []
                annotation = ""
                if hasattr(method, "__is_legacy"):
                    if method.__replaced_by:
                        annotation += f" (legacy, replaced by {utils.cap_action(method.__replaced_by)})"
                    else:
                        annotation += " (legacy)"
                #output.append(f"\n{utils.cap_resource(resource)} - {utils.cap_action(name)}{annotation}")
                actions[f"{utils.cap_resource(resource)} - {utils.cap_action(name)}{annotation}"] = output
                if hasattr(method, "__is_legacy"):
                    continue
                docs = inspect.getdoc(method)
                if docs:
                    output.append(f"Desc: {inspect.cleandoc(docs)}")
                else:
                    output.append("Desc: None")
                req_method = find_request_method(method)
                output.append(f"Method: {req_method}")
                sig = inspect.signature(method)
                output.append(f"Call: {resource}.{name}{sig}")
                args, options = parse_sig(sig)
                output.append(f"Args: {', '.join(args)}")
                output.append("Options:")
                try:
                    for name, desc in options:
                        output.append(f"    {name}: {desc}")
                except TypeError:
                    pass
    for key, output in sorted(actions.items()):
        print(f"\n{key}")
        print("\n".join(output))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

