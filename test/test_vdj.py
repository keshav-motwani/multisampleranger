import shutil
from pathlib import Path
from unittest import TestCase

from easyranger.vdj import VDJ


class TestVDJ(TestCase):

    def test_run(self):

        tmp_path = Path("tmp")
        tmp_path.mkdir(parents=True, exist_ok=True)

        libraries_path = tmp_path/"libraries.csv"

        libraries_txt = """sample_name,library_name
Control1,Control1_GEX
Diseased1,Diseased1_GEX
Control2,Control2_GEX
Diseased2,Diseased2_GEX"""

        with open(libraries_path, "w") as file:
            file.writelines(libraries_txt)

        result_path = "test_results_hi"

        VDJ.run(libraries_path,
                  "some_reference.txt",
                  64,
                  128,
                  "/home/PREFIX/<library_name>/SUFFIX",
                  False,
                  result_path)

        shutil.rmtree(tmp_path, ignore_errors=True)
        shutil.rmtree(result_path, ignore_errors=True)
        shutil.rmtree(VDJ.OUTPUT_PATH, ignore_errors=True)
