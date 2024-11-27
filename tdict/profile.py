from pathlib import Path


class Profile:

    def __init__(self):
        workdir = Path.home().joinpath(".tdict")
        workdir.mkdir(exist_ok=True)
        self.filepath = workdir.joinpath("tdictrc")
        if not self.filepath.exists():
            self.filepath.touch()

    @property
    def db_path(self):
        if self.read('USER'):
            return Path.home().joinpath(".tdict/{}.sqlite3".format(self.read('USER')))
        return Path.home().joinpath(".tdict/tdict.sqlite3")

    def read(self, keyword, default=""):
        with open(self.filepath) as f:
            for line in f:
                if keyword in line:
                    return line.replace(keyword + "=", "").replace("\n", "")
        return default

    def update(self, keyword, content=None):
        if content:
            content = keyword + "=" + content
            if not content.endswith("\n"):
                content += "\n"

        lines = []
        with open(self.filepath) as f:
            lines = f.readlines()
        with open(self.filepath, "w") as f:
            for line in lines:
                if keyword in line:
                    continue
                f.write(line)
            if content:
                f.write(content)


profile = Profile()