import argparse
import warnings
from subprocess import Popen

from pathlib import Path
import shutil
import os

import pandas as pd


class count:

    FASTQS = "fastqs"
    SAMPLE_ORIGIN = "sample_origin"
    SAMPLE_NAME = "sample_name"
    LIBRARY_TYPE = "library_type"

    TMP_PATH = "tmp/"

    @staticmethod
    def main():

        args = count.parse_args()

        count.run(args.libraries_path,
                  args.feature_reference_path,
                  args.transcriptome,
                  args.localcores,
                  args.localmem,
                  args.fastq_pattern,
                  args.nosecondary,
                  args.expect_cells)

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

        return parser.parse_args()

    @staticmethod
    def run(libraries_path, feature_reference_path, transcriptome_path, localcores, localmem, fastq_pattern, nosecondary, expect_cells):

        libraries = pd.read_csv(libraries_path)
        count.check_libraries(libraries, fastq_pattern)

        libraries = count.parse_fastqs(libraries, fastq_pattern)

        feature_reference = pd.read_csv(feature_reference_path)

        for library in count.split_libraries(libraries):
            count._run(library, feature_reference, transcriptome_path, localcores, localmem, nosecondary, expect_cells)

    @staticmethod
    def _run(library: pd.DataFrame, feature_reference: pd.DataFrame, transcriptome_path, localcores, localmem, nosecondary, expect_cells):

        count.create_tmp_path()

        library_path = count.TMP_PATH + "libraries.csv"
        feature_ref_path = count.TMP_PATH + "feature_reference.csv"

        sample_id = library[count.SAMPLE_ORIGIN].values[0]
        library["sample"] = library.sample_name
        library[["fastqs", "sample", "library_type"]].to_csv(library_path)
        feature_reference.to_csv(feature_ref_path)

        cellranger_str = "cellranger count --id={sample}" + \
                         " --libraries={library_path}" \
                         " --feature-ref={feature_ref_path}" \
                         " --transcriptome={transcriptome_path}" + \
                         " --localcores={localcores}" + \
                         " --localmem={localmem}"

        if nosecondary:
            cellranger_str = cellranger_str + " --nosecondary"

        if expect_cells is not None:
            cellranger_str = cellranger_str + " --expect_cells=" + expect_cells

        cellranger_str = cellranger_str.format(sample=sample_id,
                                               library_path=library_path,
                                               feature_ref_path = feature_ref_path,
                                               transcriptome_path=transcriptome_path,
                                               localcores=localcores,
                                               localmem=localmem)

        print(cellranger_str)

        p = Popen(cellranger_str, shell=True)
        p.communicate()

        count.remove_tmp_path()

    @staticmethod
    def split_libraries(libraries):

        libraries = libraries.groupby(count.SAMPLE_ORIGIN)

        return [libraries.get_group(x) for x in libraries.groups]

    @staticmethod
    def check_libraries(libraries, fastq_pattern):

        assert count.SAMPLE_ORIGIN in libraries.columns, \
            count.SAMPLE_ORIGIN + " column must be present in libraries file"

        assert count.SAMPLE_NAME in libraries.columns, \
            count.SAMPLE_NAME + " column must be present in libraries file"

        assert count.LIBRARY_TYPE in libraries.columns, \
            count.LIBRARY_TYPE + " column must be present in libraries file"

        if fastq_pattern is None:
            assert count.FASTQS in libraries.columns, \
                count.FASTQS + " column must be present in libraries file if fastq_pattern not specified"

    # libraries csv in following format
    # [fastq], sample_origin, sample_name, library_type

    # arguments: [fastq_pattern (root_path/.../{sample_name}/...)] libraries features

    @staticmethod
    def parse_fastqs(libraries, fastq_pattern):

        if count.FASTQS in libraries.columns:
            warnings.warn("fastq_pattern ignored, fastqs already specified in input libraries file")
        else :
            libraries[count.FASTQS] = [fastq_pattern.replace("<sample_name>", x) for x in libraries[count.SAMPLE_NAME].values]

        return libraries

    @staticmethod
    def create_tmp_path():

        path = Path(count.TMP_PATH)
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def remove_tmp_path():

        shutil.rmtree(count.TMP_PATH)


if __name__ == "__main__":
    count.main()
