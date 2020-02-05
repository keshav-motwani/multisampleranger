import shutil
from pathlib import Path
from unittest import TestCase

from source.count import Count


class TestCount(TestCase):

    def test_run(self):

        tmp_path = Path("tmp")
        tmp_path.mkdir(parents=True, exist_ok=True)

        libraries_path = tmp_path/"libraries.csv"

        libraries_txt = """sample_name,library_name,library_type
Control1,Control1_GEX,Gene Expression
Diseased1,Diseased1_GEX,Gene Expression
Control2,Control2_GEX,Gene Expression
Diseased2,Diseased2_GEX,Gene Expression
Control1,Control1_FB,Antibody Capture
Diseased1,Diseased1_FB,Antibody Capture
Control2,Control2_FB,Antibody Capture
Diseased2,Diseased2_FB,Antibody Capture"""

        with open(libraries_path, "w") as file:
            file.writelines(libraries_txt)

        feature_reference_path = tmp_path/"feature_reference.tsv"

        feature_reference_txt = """id,sequence,name,read,pattern,feature_type
HLA-DRA,AATAGCGAGCAAGTA,HLA-DRA,R2,5PNNNNNNNNNN(BC),Antibody Capture
CD3,CTCATTGTAACTCCT,CD3,R2,5PNNNNNNNNNN(BC),Antibody Capture
CD15,TCACCAGTACCTAGT,CD15,R2,5PNNNNNNNNNN(BC),Antibody Capture
CD127,GTGTGTTGTCCTATG,CD127,R2,5PNNNNNNNNNN(BC),Antibody Capture"""

        with open(feature_reference_path, "w") as file:
            file.writelines(feature_reference_txt)

        Count.run(libraries_path,
                  feature_reference_path,
                  "some_transcriptome.txt",
                  64,
                  128,
                  "/home/PREFIX/<library_name>/SUFFIX",
                  False,
                  False)

        shutil.rmtree(tmp_path, ignore_errors=True)
        shutil.rmtree(Count.OUTPUT_PATH, ignore_errors=True)
