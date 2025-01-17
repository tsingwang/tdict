from pathlib import Path


class Profile:

    def __init__(self):
        workdir = Path.home().joinpath(".tdict")
        workdir.mkdir(exist_ok=True)
        self.filepath = workdir.joinpath("tdictrc")
        if not self.filepath.exists():
            self.filepath.touch()

    @property
    def current_user(self):
        return self.read('USER')

    @current_user.setter
    def current_user(self, user: str):
        self.update('USER', user)

    @property
    def db_path(self):
        return Path.home().joinpath(".tdict/{}.sqlite3".format(self.read('USER', 'tdict')))

    @property
    def schedule_days(self):
        default = '0,1,3,7,14,30,90,180,360'
        return [int(d) for d in self.read('SCHEDULE_DAYS', default).split(',')]

    @property
    def max_daily_words(self):
        return int(self.read('MAX_DAILY_WORDS', 20))

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
