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

 If you want to continue training starting from a pretrained model you can use --checkpoint
#### Calling 
The following inputs are required:
- tumor alignment file.bam
- normal alignment file.bam
- call region file.bed
- trained model file.pth

python preprocess.py \
	--mode call \
	--reference ref.fa \
	--region_bed region.bed \
	--tumor_bam tumor.bam \
	--normal_bam normal.bam \
	--work work_call \
	--scan_alignments_binary ../bin/scan_alignments

python call.py \
	--candidates_tsv work_call/dataset/* /candidates*.tsv \
	--reference ref.fa \
	--out work_call \
	--checkpoint work_train/some_checkpoint.pth \
	--num_threads 8 \
	--batch_size 64 

python postprocess.py \
	--reference ref.fa \
	--tumor_bam tumor.bam \
	--pred_vcf work_call/pred.vcf \
	--candidates_vcf work_call/work_tumor/filtered_candidates.vcf \
	--output_vcf work_call/V_Next.vcf \
	--work work_call 
The final V_Next prediction is work_call/V_Next.vcf
