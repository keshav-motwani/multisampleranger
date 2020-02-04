import argparse
import warnings
from subprocess import Popen

import pandas as pd

from source.utils import Utils


class Count:

    FASTQS = "fastqs"
    SAMPLE_NAME = "sample_name"
    LIBRARY_NAME = "library_name"
    LIBRARY_TYPE = "library_type"

    OUTPUT_PATH = "easyranger_count_output/"
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
                  args.nosecondary,
                  args.expect_cells,
                  args.execute)

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
        parser.add_argument('--expect_cells', action="store", default=None)
        parser.add_argument('--execute', action="store", default=True)

        return parser.parse_args()

    @staticmethod
    def run(libraries_path, feature_reference_path, transcriptome_path, localcores, localmem, fastq_pattern,
            nosecondary, expect_cells, execute):

        Utils.create_path(Count.OUTPUT_PATH)
        Utils.create_path(Count.LIBRARIES_PATH)

        libraries = pd.read_table(libraries_path)
        Count.check_libraries(libraries, fastq_pattern)

        libraries = Count.parse_fastqs(libraries, fastq_pattern)

        sample_names = set()

        for index, library in enumerate(Count.split_libraries(libraries)):
            Count._run(library, feature_reference_path, transcriptome_path, localcores, localmem, nosecondary, expect_cells, execute, index)
            sample_names.add(library.sample_name.values[0])

        Count.write_sample_names(sample_names)

    @staticmethod
    def _run(library: pd.DataFrame, feature_ref_path: str, transcriptome_path, localcores, localmem,
             nosecondary, expect_cells, execute, index):

        sample_name = library[Count.SAMPLE_NAME].values[0]

        library_path = Count.LIBRARIES_PATH + sample_name + "_libraries.csv"

        library["sample"] = library.library_name
        library[["fastqs", "sample", "library_type"]].to_csv(library_path, index=False)

        cellranger_str = "cellranger count --id={sample}" + \
                         " --libraries={library_path}" \
                         " --feature-ref={feature_ref_path}" \
                         " --transcriptome={transcriptome_path}" + \
                         " --localcores={localcores}" + \
                         " --localmem={localmem}"

        if nosecondary:
            cellranger_str = cellranger_str + " --nosecondary"

        if expect_cells is not None:
            cellranger_str = cellranger_str + " --expect_cells=" + str(expect_cells)

        cellranger_str = cellranger_str.format(sample=sample_name,
                                               library_path=library_path,
                                               feature_ref_path=feature_ref_path,
                                               transcriptome_path=transcriptome_path,
                                               localcores=localcores,
                                               localmem=localmem)

        if execute:
            p = Popen(cellranger_str, shell=True)
            p.communicate()

        Count.write_run_script(cellranger_str, sample_name)

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

    @staticmethod
    def parse_fastqs(libraries, fastq_pattern):

        if Count.FASTQS in libraries.columns:
            warnings.warn("fastq_pattern ignored, fastqs already specified in input libraries file")
        else:
            libraries[Count.FASTQS] = [fastq_pattern.replace("<library_name>", x) for x in
                                       libraries[Count.LIBRARY_NAME].values]

        return libraries

    @staticmethod
    def write_sample_names(sample_names):

        with open(Count.SAMPLE_NAMES_FILE_PATH, 'w') as filehandle:
            filehandle.writelines("%s\n" % sample_name for sample_name in sample_names)

    @staticmethod
    def write_run_script(command_str, sample_name):

        with open(Count.RUN_SCRIPT_PATH, 'a') as run_script:
            run_script.write(command_str + '\n')

        with open(Count.ARRAY_RUN_SCRIPT_PATH, 'w') as run_script:
            run_script.write(command_str.replace(sample_name, "${sample_name}") + '\n')


if __name__ == "__main__":
    Count.main()
