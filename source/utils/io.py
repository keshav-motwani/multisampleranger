import warnings


class IO:

    @staticmethod
    def write_run_script(run_script_path, command_strings):

        with open(run_script_path, 'w') as run_script:
            run_script.writelines([command + "\n" for command in command_strings])

    @staticmethod
    def parse_fastqs(libraries, library_column, fastq_column, fastq_pattern):

        if fastq_column in libraries.columns:
            warnings.warn("fastq_pattern ignored, fastqs already specified in input libraries file")
        else:
            libraries[fastq_column] = [fastq_pattern.replace("<library_name>", x) for x in
                                       libraries[library_column].values]

        return libraries
