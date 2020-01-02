import os
from datetime import datetime
import re


def dataclass(**kwargs):
    class Container:
        def __repr__(self):
            s = (
                "Container("
                + ", ".join(["{}={}".format(k, v) for k, v in kwargs.items()])
                + ")"
            )
            return s

    c = Container()
    for k, v in kwargs.items():
        setattr(c, k, v)

    return c


def parse_filename(file):

    m = re.match(
        r"(?:^(?P<date>\d{4}-\d{2}-\d{2})--)?(?:--)?(?P<name>.*?)(?:__)?(?:(?<=__)(?P<tags>[\wÄÖÜäöü\- ]+?))?(?P<ext>\.\w+)$",
        file,
    )

    assert m is not None, "Regex did not match"

    if m.group("date") is not None:
        dt = datetime.strptime(m.group("date"), "%Y-%m-%d")
    else:
        dt = None

    if m.group("tags") is not None:
        tags = set(m.group("tags").split("_"))
    else:
        tags = set()

    name = m.group("name") + m.group("ext")

    return dataclass(dt=dt, name=name, tags=tags)


def format_filename(name, dt, tags=None):
    tags = tags or set()
    if name is None:
        raise ValueError()
    root, ext = os.path.splitext(name)
    dtstr = ""
    if dt is not None:
        dtstr = "%s--" % dt.strftime("%Y-%m-%d")

    return "{}{}{}{}".format(
        dtstr, root, ("__" + "_".join(sorted(tags))) if len(tags) > 0 else "", ext
    )
