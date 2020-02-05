import os
import sys; sys.path.extend([os.path.abspath(__file__ + "/../../")])
import argparse
from subprocess import Popen

import pandas as pd

from source.utils.path_manager import PathManager
from source.utils.io import IO


class Count:

    FASTQS = "fastqs"
    SAMPLE_NAME = "sample_name"
    LIBRARY_NAME = "library_name"
    LIBRARY_TYPE = "library_type"
    EXPECT_CELLS = "expected_cell_count"

    OUTPUT_PATH = "easyranger_count/"
    LIBRARIES_PATH = OUTPUT_PATH + "libraries/"
    RUN_SCRIPT_PATH = OUTPUT_PATH + "run_script.bash"
    ARRAY_RUN_SCRIPT_PATH = OUTPUT_PATH + "array_run_script.bash"
    SAMPLE_NAMES_FILE_PATH = OUTPUT_PATH + "sample_names.txt"

    @staticmethod
    def main():

        args = Count.parse_args()

        Count.run(args.libraries_path,
                  args.feature_reference_path,
                  args.transcriptome,
                  args.localcores,
                  args.localmem,
                  args.fastq_pattern,
                  args.nosecondary.lower() == "true",
                  args.execute.lower() == "true",
                  args.result_path)

    @staticmethod
    def parse_args():

        parser = argparse.ArgumentParser(description='Wrapper around cellranger count for running multiple samples')

        parser.add_argument('--libraries_path', action="store")
        parser.add_argument('--feature_reference_path', action="store")
        parser.add_argument('--transcriptome', action="store")
        parser.add_argument('--localcores', action="store", default=32)
        parser.add_argument('--localmem', action="store", default=120)
        parser.add_argument('--fastq_pattern', action="store", default=None)
        parser.add_argument('--nosecondary', action="store", default=True)
        parser.add_argument('--execute', action="store", default=True)
        parser.add_argument('--result_path', action="store", default=".")

        return parser.parse_args()

    @staticmethod
    def run(libraries_path, feature_reference_path, transcriptome_path, localcores, localmem, fastq_pattern,
            nosecondary, execute, result_path):

        libraries = pd.read_csv(libraries_path)

        Count.check_libraries(libraries, fastq_pattern)

        libraries = IO.parse_fastqs(libraries, Count.LIBRARY_NAME, Count.FASTQS, fastq_pattern)

        PathManager.create_path(result_path + "/" + Count.OUTPUT_PATH)
        PathManager.create_path(result_path + "/" + Count.LIBRARIES_PATH)

        sample_names = set()
        command_strings = set()

        for library in Count.split_libraries(libraries):
            command = Count._run(library, feature_reference_path, transcriptome_path, localcores, localmem, nosecondary, execute, result_path)
            command_strings.add(command)
            sample_names.add(library.sample_name.values[0])

        IO.write_sample_names(result_path + "/" + Count.SAMPLE_NAMES_FILE_PATH,
                              sample_names)

        IO.write_run_script(result_path + "/" + Count.RUN_SCRIPT_PATH,
                            result_path + "/" + Count.ARRAY_RUN_SCRIPT_PATH,
                            command_strings,
                            sample_names)

    @staticmethod
    def _run(library: pd.DataFrame, feature_ref_path: str, transcriptome_path, localcores, localmem, nosecondary, execute, result_path):

        sample_name = library[Count.SAMPLE_NAME].values[0]

        expect_cells = library[Count.EXPECT_CELLS].values[0] if Count.EXPECT_CELLS in library.columns else None

        library_path = result_path + "/" + Count.LIBRARIES_PATH + sample_name + "_libraries.csv"

        library = library.assign(sample=library.library_name)
        library[["fastqs", "sample", "library_type"]].to_csv(library_path, index=False)

        cellranger_str = "cellranger count --id={sample}" + \
                         " --libraries={library_path}" \
                         " --transcriptome={transcriptome_path}" + \
                         " --localcores={localcores}" + \
                         " --localmem={localmem}"

        if nosecondary:
            cellranger_str = cellranger_str + " --nosecondary"

        if expect_cells is not None:
            cellranger_str = cellranger_str + " --expect_cells=" + str(expect_cells)

        if feature_ref_path is not None:
            cellranger_str = cellranger_str + " --feature-ref=" + os.path.abspath(str(feature_ref_path))

        cellranger_str = cellranger_str.format(sample=sample_name,
                                               library_path=os.path.abspath(library_path),
                                               feature_ref_path=os.path.abspath(feature_ref_path),
                                               transcriptome_path=os.path.abspath(transcriptome_path),
                                               localcores=localcores,
                                               localmem=localmem)

        cellranger_str = "cd " + os.path.abspath(result_path) + "; " + cellranger_str

        if execute:
            p = Popen(cellranger_str, shell=True)
            p.communicate()

        return cellranger_str

    @staticmethod
    def split_libraries(libraries):

        libraries = libraries.groupby(Count.SAMPLE_NAME)

        return [libraries.get_group(x) for x in libraries.groups]

    @staticmethod
    def check_libraries(libraries, fastq_pattern):

        assert Count.SAMPLE_NAME in libraries.columns, \
            Count.SAMPLE_NAME + " column must be present in libraries file"

        assert Count.LIBRARY_NAME in libraries.columns, \
            Count.LIBRARY_NAME + " column must be present in libraries file"

        assert Count.LIBRARY_TYPE in libraries.columns, \
            Count.LIBRARY_TYPE + " column must be present in libraries file"

        if fastq_pattern is None:
            assert Count.FASTQS in libraries.columns, \
                Count.FASTQS + " column must be present in libraries file if fastq_pattern not specified"


if __name__ == "__main__":
    Count.main()
