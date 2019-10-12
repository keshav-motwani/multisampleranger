# cellranger_wrapper

### Wrapper around cellranger count and vdj (not implemented yet) to run multiple samples at once.

`cellranger count` and `vdj` only take a single sample at a time, making it troublesome to run multiple samples through at once. This is especially the case in libraries with feature barcoding, such as those prepared using the CITE-seq assay, as for each sample, one must create a libraries csv for each sample independently, containing the path to fastqs for the gene expression and any other feature barcoding libraries. To get around this limitation, using this wrapper, one can instead create a single libraries file, and specify this. This wrapper will split this by sample origin and process them independently.

### Usage

Currently, this only supports `cellranger count` workflows.

To use this wrapper, run the following command:

```
python3 count.py [-h] [--libraries_path LIBRARIES_PATH]
                 [--feature_reference_path FEATURE_REFERENCE_PATH]
                 [--transcriptome TRANSCRIPTOME] [--localcores LOCALCORES]
                 [--localmem LOCALMEM] [--fastq_pattern FASTQ_PATTERN]
                 [--nosecondary NOSECONDARY] [--expect_cells EXPECT_CELLS]
```

#### Description of arguments:

* `libraries_path`: Path to libraries file with the following columns:
  - `sample_origin`: Column indicating the biological sample from which the library originated.
  - `sample_name`: Column indicating the name of library, multiple libraries per `sample_origin` are common for CITE-seq - one for gene expression, one for feature barcodes
  - `library_type`: Can be `Gene Expression`, `Antibody Capture`, `CRISPR`, or `Custom`
  - `fastqs`: [If `fastq_pattern` not specified]: Path to folder containing fastqs for the library

* `feature_reference_path`: Path to feature reference information in same format as `cellranger count --feature-ref` argument.

* `transcriptome`, `localcores`, `localmem`, `expect_cells`: Same as respective arguments to `cellranger count`.

* `fastq_pattern`: A string containing the path to fastqs, but instead of including each `sample_name`, the string contains `<sample_name>` which will be replaced with the sample name as specified in the `libraries_path` file.
  - Example: `/home/PREFIX/<sample_name>/SUFFIX`
