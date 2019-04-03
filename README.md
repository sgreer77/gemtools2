# gemtools


## Installation


### **Dependencies:**

**Python packages:** pandas, numpy, pysam, pyvcf, pybedtools, rpy2, mappy

**R package:** ggplot2

**NOTE: gemtools was built under python version 2.7**
See 'test_versions' file for tested package versions. 

### **To install gemtools:**

**If you already have the dependencies:**

	git clone https://github.com/sgreer77/gemtools.git
	cd gemtools
	pip install .

**If you do not already have the dependencies, the recommended installation is to create a conda virtual environment and install the dependencies with conda:**
                                
1. **Check your anaconda installation:**

		conda

	If you do not receive the usage information then you can install anaconda/miniconda by following the instructions at: 
	<https://conda.io/docs/user-guide/install/download.html>

2. **If/when you have anaconda installed:**

      **Create a conda virtual environment:**

		conda create -n gemtools_env python=2.7
		source activate gemtools_env
		
      **Install the dependencies with conda:**
		
		conda install pandas pysam rpy2
		conda install -c bioconda pyvcf pybedtools mappy
		conda install -c r r-ggplot2

      **Finally, install gemtools:**

		git clone https://github.com/sgreer77/gemtools.git
		cd gemtools
		pip install .	


### **Test the gemtools installation:**

	cd test
	./test_script.sh

**If the test is successful, it will generate:**
- 1 bed file
- 10 txt files
- 1 png file
- A directory containing 16 gzipped fastq files

## Running gemtools


gemtools is a collection of tools that use the **output of Long Ranger** (10X Genomics) to perform additional analyses      (Long Ranger output files are indicated in the instructions below with an **LR** prefix)

**General usage: gemtools -T [tool] [-options]**


### Tools for getting basic information about the phase blocks:


**get_phased_basic**: Obtain phasing information for all SNVs in the vcf file

	gemtools -T get_phased_basic -v [LR.vcf.gz] -o [output.phased_basic] -n [chr_num]
	
	Ex: gemtools -T get_phased_basic -v phased_variants.vcf.gz -o output.phased_basic
	
	Ex: gemtools -T get_phased_basic -v phased_variants.vcf.gz -o output.phased_basic -n 22
	
	Input:
		-v gzipped vcf file output from LR
		
		-n chromosome (optional)
	Output:
		-o output file: each row is an SNV; columns are phasing information for each SNV

**get_phase_blocks**: Summarize phase blocks -- coordinates, size, number of phased heterozygous SNVs per phase block etc.

	gemtools -T get_phase_blocks -i [out.phased_basic] -o [out.phase_blocks]
	
	Ex: gemtools -T get_phase_blocks -i out.phased_basic -o out.phase_blocks
	
	Input:
		-i output from 'get_phased_basic' tool
	Output:
		-o output file: each row is a phase block, columns summarize information for each phase block (size etc.)


### Generally useful tools:


**get_phased_bcs:** For a particular phase block, return the haplotype 1 and haplotype 2 barcodes

	gemtools -T get_phased_bcs -i [out.phased_basic] -p [phase_block_id] -o [out.phased_bcs]
	
	Ex: gemtools -T get_phased_bcs -i out.phased_basic -p 1356780 -o out.phased_bcs

	Input:
		-i output from 'get_phased_basic' tool
		
		-p id number for phase block of interest (phase block ids are originally assigned in the LR.vcf.gz file)
	Output:
		-o output file: a table with the haplotype 1 and haplotype 2 barcodes indicated
	
**get_bcs_in_region:** Get all the barcodes that exist in a given region(s) of the genome

	gemtools -T get_bcs_in_region -b [LR.bam] -f [region_in] -o [out.bcs]
	
	Ex: gemtools -T get_bcs_in_region -b phased_possorted.bam -f chr1,1000,2000 -o out.bcs.txt
	
	Ex: gemtools -T get_bcs_in_region -b phased_possorted.bam -f chr1,1000,2000;chr1,3000,4000 -o out.bcs.txt

	Input:
		-b bam file generated by Long Ranger
		
		-f region(s) where barcodes must be located (does not require that barcode be in all regions)
		
	Output:
		-o output file: list of barcodes

**count_bcs_list:** Determine presence and quantity of given barcodes across a given region

	gemtools -T count_bcs_list -b [LR.bam] -f [region_in] -x [in_window] -l [bc_list] -o [out.bc_count]
	
	Ex: gemtools -T count_bcs_list -b phased_possorted.bam -f chr1,1000,2000 -x 100 -l bc_list.txt -o out.bc_count.txt

	Input:
		-b bam file generated by Long Ranger
		
		-f region(s) to assess barcodes
		
		-x size of windows to check for barcodes
		
		-b file containing list of barcodes (one barcode per line)
		
	Output:
		-o output file: rows are genomic window coordinates, columns are each barcode in bc_list file, entries are number of each barcode in each window

**plot_hmw:** Generate a plot of the mapping locations of reads with each barcode

	gemtools -T plot_hmw -i [out.bc_count] -o [out.png]

	Input:
		-i output file generated by 'count_bcs_list' tool (png file)

		--sort sort barcodes by mapping coordinate (optional)
		
	Output:
		-o output file: plot of barcode mapping locations in a given region


### SV analysis tools:


**set_bc_window:** Generate windows around SV breakpoints for SV analysis

	gemtools -T set_bc_window [OPTIONS] -i [LR_input.bedpe] -o [out.bed] -m [run_mode:auto|window] -w [window_size]
	
	Ex: gemtools -T set_bc_window -i large_sv_calls.bedpe -o large_sv_calls.bc_wndw.bed -m auto -w 100000

	Input:
		-i bedpe file of SV breakpoints; this is typically the Long Ranger output: large_sv_calls.bedpe OR large_sv_candidates.bedpe

		-w size of window to generate around the breakpoints (should be approximately the size of the HMW molecules)
		
		-m mode to generate windows; can be 'auto' or 'window'
				
	Output:
		-o output file: bed file with windows around breakpoints

**get_shared_bcs:** Determine barcodes shared between SV breakpoints

	gemtools -T get_shared_bcs -i [out.bed] -b [LR_bam_file] -o [out.shared]
	
	Ex: gemtools -T get_shared_bcs -i large_sv_calls.bc_wndw.bed -b phased_possorted.bam -o out.shared.txt
	
	Input:
		-i output bed file from 'set_bc_window' tool (or custom bed file with relevant columns)
		
		-b bam file generated by Long Ranger
		
	Output:
		-o output file: List and count of SV-specific barcodes for each SV event

**set_hap_window:** Generate windows around SV breakpoints for haplotype analysis

	gemtools -T set_hap_window [OPTIONS] -i [LR_input.bedpe] -o [out.txt] -w [window_size]
	
	Ex: gemtools -T set_hap_window -i large_sv_calls.bedpe -o large_sv_calls.hap_wndw.txt -w 1000000

	Input:
		-i bedpe file of SV breakpoints; this is typically the Long Ranger output: large_sv_calls.bedpe OR large_sv_candidates.bedpe

		-w size of window to generate around the breakpoints (should be approximately the size of the phase blocks)
				
	Output:
		-o output file: bedpe file with windows around breakpoints

**assign_sv_haps:** Assign SV barcodes to existing haplotypes (SNVs)

	gemtools -T assign_sv_haps -i [out.txt] -e [out.shared] -c [LR_control.vcf.gz] -v [LR_test.vcf.gz] -o [out.haps]
	
	Ex: gemtools -T assign_sv_haps -i large_sv_calls.hap_wndw.txt -e out.shared.txt -v phased_variants.vcf.gz -c phased_variants.vcf.gz -o out.haps.txt
	
	Input:
		-i output file from 'set_hap_window'
		
		-e output file from 'get_shared_bcs'

		-v vcf file generated by Long Ranger for test sample (ex: tumor sample)
		
		-c vcf file generated by Long Ranger for control sample (ex: normal sample) -- this is optional, for if the user wants to use a different vcf to define phase blocks
				
	Output:
		-o output file: List of breakpoints with phase id and number of barcodes supporting assignment to each haplotype

**count_bcs:** Determine presence and quantity of given barcodes across a given region surrounding the SV breakpoints

	gemtools -T count_bcs -i [LR_input.bedpe] -e [out.shared] -b [LR.bam] -x [in_window] -y [out_window] -s [sv_name] -o [out.bc_count]
	
	Ex: gemtools -T count_bcs -i large_sv_calls.bedpe -e out.shared.txt -b phased_possorted.bam -x 1000 -y 50000 -s call_110 -q shared -o out.bc_count.txt 
	
	Input:
		-i bedpe file of SV breakpoints; this is typically the Long Ranger output: large_sv_calls.bedpe OR large_sv_candidates.bedpe

		-e output file from 'get_shared_bcs'
		
		-b bam file generated by Long Ranger
		
		-x size of small windows to check for barcodes
		
		-y size of large windows around breakpoints to check for barcodes
		
		-s name(s) of the SV(s) to check; if multiple, use a comma-separated list
		
	Output:
		-o output file: rows are genomic window coordinates, columns are each barcode in bc_list file, entries are number of each barcode in each window

**plot_hmw:** Generate a plot of the mapping locations of reads with each barcode (SAME AS ABOVE)

	gemtools -T plot_hmw -i [out.bc_count] -o [out.png]

	Input:
		-i output file generated by 'count_bcs' tool

		--sort sort barcodes by mapping coordinate (optional)		

	Output:
		-o output file: plot of barcode mapping locations in a given region (png file)


### Tools for extracting subset barcoded reads from fastq files:


**extract_reads**: Obtain reads with particular barcodes from Long Ranger fastq files (where fastq output is R1,R2,I1)

	gemtools -T extract_reads --bc_list [bc_list] --outdir [fastq_output_dir] --read1 [LR_R1.fastq.gz] --read2 [LR_R2.fastq.gz] --index1 [LR_I1.fastq.gz]
	
	Ex: gemtools -T extract_reads --bc_list bc_list.txt --outdir fastq_subset --read1 SAMPLE_S1_L001_R1_001.fastq.gz --read2 SAMPLE_S1_L001_R2_001.fastq.gz --index1 SAMPLE_S1_L001_I1_001.fastq.gz
	
	Input:
		--bc_list file containing list of barcodes (one barcode per line)
		
		--read1 Long Ranger read 1 fastq
		
		--read2 Long Ranger read 2 fastq
		
		--index1 Long Ranger index 1 fastq
	Output:
		--outdir Output directory for output fastq files; subsetted R1, R2 and I1 files will be generated here

**extract_reads_interleaved**: Obtain reads with particular barcodes from Long Ranger fastq files (where fastq output is RA,I1,I2)

	gemtools -T extract_reads_interleaved --bc_list [bc_list] --outdir [fastq_output_dir] --fqdir [LR_fastq_dir] --sample_bcs [sample_barcodes] --lanes [sample_lanes]
	
	Ex: gemtools -T extract_reads_interleaved --bc_list bc_list.txt --outdir fastq_subset --fqdir fastq --sample_bcs 'ACGACGCT,CGCCATTC,GTAGTCAG,TATTGAGA' --lanes '1,5'
	
	Input:
		--bc_list file containing list of barcodes (one barcode per line)
		
		--fqdir Long Ranger fastq directory, containing RA and I1 fastq files
		
		--sample_bcs comma-separated list of Long Ranger sample barcodes
		
		--lanes comma-separated list of seq lanes to consider
	Output:
		--outdir Output directory for output fastq files; subsetted RA and I1 files will be generated here
