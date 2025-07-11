# V-Next
Somatic variant detection framework
# Requirements
VarNet has been tested on ubuntu 22.04 LTS.
Python=3.10

#### Training
The following inputs are required:
- tumor alignment file.bam
- normal alignment file.bam
- training region file.bed
- truth somatic variant file.vcf

python preprocess.py \
	--mode train \
	--reference ref.fa \
	--region_bed region.bed \
	--tumor_bam tumor.bam \
	--normal_bam normal.bam \
	--work work_train \
	--truth_vcf truth.vcf \
	--scan_alignments_binary ../bin/scan_alignments

python train.py \
	--candidates_tsv work_train/dataset/* /candidates*.tsv \
	--out work_train \
	--num_threads 8 \
	--batch_size 64 

#### Calling 
The following inputs are required:
- tumor alignment file.bam
- normal alignment file.bam
- call region file.bed
- trained model file.pth

