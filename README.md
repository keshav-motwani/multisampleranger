# easyranger

### Wrapper around cellranger count and vdj to run multiple samples at once.

`cellranger count` and `vdj` only take a single sample at a time, making it troublesome to run multiple samples through at once. This is especially the case in libraries with feature barcoding, such as those prepared using the CITE-seq assay, as for each sample, one must create a libraries csv for each sample independently, containing the path to fastqs for the gene expression and any other feature barcoding libraries. To get around this limitation, using this wrapper, one can instead create a single libraries file, and specify this. This wrapper will split this by sample name and process them independently.

## Usage

### `count`

```
easyranger/count [-h] [--libraries_path LIBRARIES_PATH]
                 [--feature_reference_path FEATURE_REFERENCE_PATH]
                 [--transcriptome TRANSCRIPTOME] [--localcores LOCALCORES]
                 [--localmem LOCALMEM] [--nosecondary NOSECONDARY]
                 [--fastq_pattern FASTQ_PATTERN] [--execute EXECUTE]
                 [--result_path RESULT_PATH]
```

#### Description of arguments:

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