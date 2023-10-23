import subprocess

def get_tags(f, tags_exe=None):
    #  print(tags_exe)
    tags_exe = tags_exe or subprocess.check_output(["which", "tag"]).decode().strip()
    output = subprocess.check_output([tags_exe, "--list", "--no-name", f])
    tagstr = output.decode("utf-8").strip()
    if tagstr == "":
        return set()
    return set(tagstr.split(","))


def set_tags(f, tags, tags_exe=None):
    tags_exe = tags_exe or subprocess.check_output(["which", "tag"]).decode().strip()
    subprocess.check_call([tags_exe, "--set", ",".join(tags), f])
