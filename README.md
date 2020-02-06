# easyranger

### Wrapper around cellranger count and vdj to run multiple samples at once.

`cellranger count` and `vdj` only take a single sample at a time, making it troublesome to run multiple samples through at once. This is especially the case in libraries with feature barcoding, such as those prepared using the CITE-seq assay, as for each sample, one must create a libraries csv for each sample independently, containing the path to fastqs for the gene expression and any other feature barcoding libraries. To get around this limitation, using this wrapper, one can instead create a single libraries file, and specify this. This wrapper will split this by sample name and process them independently.

## Usage

### `count`

```
python3 source/count.py [-h] [--libraries_path LIBRARIES_PATH]
                        [--feature_reference_path FEATURE_REFERENCE_PATH]
                        [--transcriptome TRANSCRIPTOME] [--localcores LOCALCORES]
                        [--localmem LOCALMEM] [--nosecondary NOSECONDARY]
                        [--fastq_pattern FASTQ_PATTERN] [--execute EXECUTE]
                        [--result_path RESULT_PATH]
```

#### Arguments:

* `libraries_path`: Path to libraries file with the following columns:
  - `sample_name`: Column indicating the biological sample from which the library originated.
  - `library_name`: Column indicating the name of library, multiple libraries per `sample_name` are common for CITE-seq - one for gene expression, one for feature barcodes
  - `library_type`: Can be `Gene Expression`, `Antibody Capture`, `CRISPR`, or `Custom`
  - `expected_cell_count`: Number of cells expected from each sample (should be consistent for each sample_name across libraries, if column not included, defaults to `cellranger`'s default)
  - `fastqs`: [If `fastq_pattern` not specified]: Path to folder containing fastqs for the library
  - Example contents: 
 
| sample_name   | library_name  | library_type     | expected_cell_count |
|---------------|---------------|------------------|---------------------|
| Control1      | Control1_GEX  | Gene Expression  | 5000                |
| Diseased1     | Diseased1_GEX | Gene Expression  | 5000                |
| Control2      | Control2_GEX  | Gene Expression  | 5000                |
| Diseased2     | Diseased2_GEX | Gene Expression  | 5000                |
| Control1      | Control1_FB   | Antibody Capture | 5000                |
| Diseased1     | Diseased1_FB  | Antibody Capture | 5000                |
| Control2      | Control2_FB   | Antibody Capture | 5000                |
| Diseased2     | Diseased2_FB  | Antibody Capture | 5000                |


* `feature_reference_path`: Path to feature reference information in same format as `cellranger count --feature-ref` argument.
  - Example contents:
  
| id      | sequence        | name    | read | pattern          | feature_type     | 
|---------|-----------------|---------|------|------------------|------------------| 
| HLA-DRA | AATAGCGAGCAAGTA | HLA-DRA | R2   | 5PNNNNNNNNNN(BC) | Antibody Capture | 
| CD3     | CTCATTGTAACTCCT | CD3     | R2   | 5PNNNNNNNNNN(BC) | Antibody Capture | 
| CD15    | TCACCAGTACCTAGT | CD15    | R2   | 5PNNNNNNNNNN(BC) | Antibody Capture | 
| CD127   | GTGTGTTGTCCTATG | CD127   | R2   | 5PNNNNNNNNNN(BC) | Antibody Capture | 

* `transcriptome`, `localcores`, `localmem`, `nosecondary`: Same as respective arguments to `cellranger count`.

* `fastq_pattern`: A string containing the path to fastqs, but instead of including each `library_name`, the string contains `<library_name>` which will be replaced with the sample name as specified in the `libraries_path` file.
  - Example: `/home/PREFIX/<library_name>/SUFFIX`

* `execute`: whether cellranger commands should actually be executed, or if only the input and commands should be prepared (see more below in the section on array jobs)

* `result_path`: path where `cellranger count` output should be  stored.

#### Output:

A folder named `easyranger_count` is created in the `result_path`, containing the following:

* `libraries`: a folder containing the files for the `libraries` input to `cellranger`, one for each unique `sample_name` in the `libraries_path` file
* `run_script.bash`: script containing all of the `cellranger` commands
* `array_run_script.bash`: script containing the command used in creating a SLURM array job
* `sample_names.txt`: text file containing the unique `sample_name`, also used in creating a SLURM array job

### Using SLURM Job Arrays

To run each of the `cellranger` commands as a separate SLURM job, we can use job arrays so that the SLURM manager can submit and manage the jobs for you, and execute each command as resources become available.

First, the `easyranger` wrapper needs to be run, with argument `--execute False`. This stops it from running each command sequentially, but we can still use the outputs to generate the job array. 

We assume that this has been run, and once this is run, the following SLURM script can be run. The `#SBATCH` options depend on your use-case, but ensure that the `--array` command is `1-[n_samples]`. 

This must be run from either within the `result_path`, or `cd` to the `result_path`, or adjust the file paths in the script.

```
#!/bin/bash
#SBATCH --job-name=XXX
#SBATCH --time=XXX
#SBATCH --mail-user=XXX
#SBATCH --mail-type=ALL
#SBATCH --ntasks=XXX
#SBATCH --cpus-per-task=XXX
#SBATCH --mem=XXX
#SBATCH --qos=XXX
#SBATCH --array=1-39
#SBATCH --output=XXX.log

ml cellranger/3.1.0

# set working directory to result_path
cd out/count

# read in sample names as array, so that it can be indexed
IFS=$'\n' read -d '' -r -a sample_names < easyranger_count/sample_names.txt

# export sample_name so it can be used by array_run_script
export sample_name=${sample_names[$SLURM_ARRAY_TASK_ID]}

# run cellranger command using output from easyranger
chmod u+x easyranger_count/array_run_script.bash
./easyranger_count/array_run_script.bash
```

While this example was for the `count` wrapper, this also applies to the `vdj` wrapper. Simply replace instances of `easyranger_count` with `easyranger_vdj`.
