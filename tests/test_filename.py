import sys, os
parent = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent + '/../')

import pytest

from document_helpers.filename import parse_filename, format_filename
from datetime import datetime

def test_parse_filename():
    res = parse_filename("2018-08-01--3482274514__google_invoice.pdf")
    assert res.dt == datetime(year=2018, month=8, day=1)
    assert res.name == "3482274514.pdf"
    assert res.tags == set(["google", "invoice"])

    res = parse_filename("3482274514__google_invoice.pdf")
    assert res.dt == None
    assert res.name == "3482274514.pdf"
    assert res.tags == set(["google", "invoice"])

    res = parse_filename("--3482274514__google_invoice.pdf")
    assert res.dt == None
    assert res.name == "3482274514.pdf"
    assert res.tags == set(["google", "invoice"])

    res = parse_filename("2018-08-01--3482274514.pdf")
    assert res.dt == datetime(year=2018, month=8, day=1)
    assert res.name == "3482274514.pdf"
    assert res.tags == set()

    res = parse_filename("2018-08-01--3482274514__.pdf")
    assert res.dt == datetime(year=2018, month=8, day=1)
    assert res.name == "3482274514.pdf"
    assert res.tags == set()

    res = parse_filename("2018-08-14--Scan Something__tag1.pdf")
    assert res.dt == datetime(year=2018, month=8, day=14)
    assert res.name == "Scan Something.pdf"
    assert res.tags == set(["tag1"])

    # bug with spaces in tags
    res = parse_filename("2018-08-14--Scan__Steuer FR.pdf")
    assert res.dt == datetime(year=2018, month=8, day=14)
    assert res.name == "Scan.pdf"
    assert res.tags == set(["Steuer FR"])

    res = parse_filename("2018-08-14--Scan__tag-dashed.pdf")
    assert res.dt == datetime(year=2018, month=8, day=14)
    assert res.name == "Scan.pdf"
    assert res.tags == set(["tag-dashed"])

def test_format_filename():
    now = datetime(year=2018, month=8, day=17)
    name = "SOMENAME.pdf"
    tags = set(["tag1", "tag2"])
    assert format_filename(name, now, tags) == "2018-08-17--SOMENAME__tag1_tag2.pdf"
    assert format_filename(name, None, tags) == "SOMENAME__tag1_tag2.pdf"
    assert format_filename(name, now) == "2018-08-17--SOMENAME.pdf"

    with pytest.raises(ValueError):
        assert format_filename(None, now, tags) == "2018-08-17--SOMENAME__tag1_tag2.pdf"

    assert format_filename(name, 
                           now, 
                           set(["Tag With Spaces"])) == "2018-08-17--SOMENAME__Tag With Spaces.pdf"
