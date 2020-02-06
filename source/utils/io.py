import warnings


class IO:

    @staticmethod
    def write_sample_names(sample_names_file_path, sample_names):

        with open(sample_names_file_path, 'w') as filehandle:
            filehandle.writelines("%s\n" % sample_name for sample_name in sample_names)

    @staticmethod
    def write_run_script(run_script_path, array_run_script_path, command_strings, sample_names):

        command_strings = sorted(command_strings)
        sample_names = sorted(sample_names)

        with open(run_script_path, 'w') as run_script:
            run_script.writelines([command + "\n" for command in command_strings])

        with open(array_run_script_path, 'w') as run_script:
            run_script.write(command_strings[0].replace(sample_names[0], "${sample_name}") + '\n')

    @staticmethod
    def parse_fastqs(libraries, library_column, fastq_column, fastq_pattern):

        if fastq_column in libraries.columns:
            warnings.warn("fastq_pattern ignored, fastqs already specified in input libraries file")
        else:
            libraries[fastq_column] = [fastq_pattern.replace("<library_name>", x) for x in
                                       libraries[library_column].values]

        return libraries
