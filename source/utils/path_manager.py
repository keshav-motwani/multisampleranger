from pathlib import Path


class PathManager:

    @staticmethod
    def create_path(path):

        path = Path("/".join(Path(path).parts))
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_size(path):

        path = Path(path)
        size_mb = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file()) * 1e-6

        return size_mb
