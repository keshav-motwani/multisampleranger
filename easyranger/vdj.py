#!/usr/bin/env python3

import os
import sys; sys.path.extend([os.path.abspath(__file__ + "/../../")])
import argparse
from subprocess import Popen

import pandas as pd

from easyranger.utils.path_manager import PathManager
from easyranger.utils.io import IO


class VDJ:

    FASTQS = "fastqs"
    SAMPLE_NAME = "sample_name"
    LIBRARY_NAME = "library_name"

    OUTPUT_PATH = "easyranger_vdj/"
    RUN_SCRIPT_PATH = OUTPUT_PATH + "run_script.bash"
    ARRAY_RUN_SCRIPT_PATH = OUTPUT_PATH + "array_run_script.bash"
    SAMPLE_NAMES_FILE_PATH = OUTPUT_PATH + "sample_names.txt"

    @staticmethod
    def main():

        args = VDJ.parse_args()

        VDJ.run(args.libraries_path,
                args.reference,
                args.localcores,
                args.localmem,
                args.fastq_pattern,
                args.execute.lower() == "true",
                args.result_path)

    @staticmethod
    def parse_args():

        parser = argparse.ArgumentParser(description='Wrapper around cellranger vdj for running multiple samples')

        parser.add_argument('--libraries_path', action="store")
        parser.add_argument('--reference', action="store")
        parser.add_argument('--localcores', action="store", default=32)
        parser.add_argument('--localmem', action="store", default=120)
        parser.add_argument('--fastq_pattern', action="store", default=None)
        parser.add_argument('--execute', action="store", default="true")
        parser.add_argument('--result_path', action="store", default=".")

        return parser.parse_args()

    @staticmethod
    def run(libraries_path, reference_path, localcores, localmem, fastq_pattern, execute, result_path):

        libraries = pd.read_table(libraries_path, sep=None, engine="python")

        VDJ.check_libraries(libraries, fastq_pattern)

        libraries = IO.parse_fastqs(libraries, VDJ.LIBRARY_NAME, VDJ.FASTQS, fastq_pattern)

        PathManager.create_path(result_path + "/" + VDJ.OUTPUT_PATH)

        sample_names = set()
        command_strings = set()

        for library in VDJ.split_libraries(libraries):
            command = VDJ._run(library, reference_path, localcores, localmem, execute, result_path)
            command_strings.add(command)
            sample_names.add(library.sample_name.values[0])

        IO.write_sample_names(result_path + "/" + VDJ.SAMPLE_NAMES_FILE_PATH,
                              sample_names)

        IO.write_run_script(result_path + "/" + VDJ.RUN_SCRIPT_PATH,
                            result_path + "/" + VDJ.ARRAY_RUN_SCRIPT_PATH,
                            command_strings,
                            sample_names)

    @staticmethod
    def _run(library: pd.DataFrame, reference_path, localcores, localmem, execute, result_path):

        sample_name = library[VDJ.SAMPLE_NAME].values[0]

        fastqs = ",".join(library[VDJ.FASTQS].values)

        cellranger_str = "cellranger vdj --id={sample}" + \
                         " --fastqs={fastqs}" \
                         " --reference={reference_path}" + \
                         " --localcores={localcores}" + \
                         " --localmem={localmem}"

        cellranger_str = cellranger_str.format(sample=sample_name,
                                               fastqs=fastqs,
                                               reference_path=reference_path,
                                               localcores=localcores,
                                               localmem=localmem)

        cellranger_str = "cd " + os.path.abspath(result_path) + "; " + cellranger_str

        if execute:
            p = Popen(cellranger_str, shell=True)
            p.communicate()

        return cellranger_str

    @staticmethod
    def split_libraries(libraries):

        libraries = libraries.groupby(VDJ.SAMPLE_NAME)

        return [libraries.get_group(x) for x in libraries.groups]

    @staticmethod
    def check_libraries(libraries, fastq_pattern):

        assert VDJ.SAMPLE_NAME in libraries.columns, \
            VDJ.SAMPLE_NAME + " column must be present in libraries file"

        assert VDJ.LIBRARY_NAME in libraries.columns, \
            VDJ.LIBRARY_NAME + " column must be present in libraries file"

        if fastq_pattern is None:
            assert VDJ.FASTQS in libraries.columns, \
                VDJ.FASTQS + " column must be present in libraries file if fastq_pattern not specified"


if __name__ == "__main__":
    VDJ.main()
