import subprocess


def get_tags(f):
    output = subprocess.check_output(["/usr/local/bin/tag", "--list", "--no-name", f])
    tagstr = output.decode("utf-8").strip()
    if tagstr == "":
        return set()
    return set(tagstr.split(","))


def set_tags(f, tags):
    subprocess.check_call(["/usr/local/bin/tag", "--set", ",".join(tags), f])
