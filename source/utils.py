from pathlib import Path


class Utils:

    @staticmethod
    def create_path(path):

        path = Path("/".join(Path(path).parts))
        path.mkdir(parents=True, exist_ok=True)
