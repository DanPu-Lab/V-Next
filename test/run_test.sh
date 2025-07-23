#!/bin/bash
set -e

test_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
V_Next_dir="$( dirname ${test_dir} )"

cd ${test_dir}
mkdir -p example
cd example
if [ ! -f Homo_sapiens.GRCh37.75.dna.chromosome.22.fa ]
then
	if [ ! -f Homo_sapiens.GRCh37.75.dna.chromosome.22.fa.gz ]
	then
		wget ftp://ftp.ensembl.org/pub/release-75//fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.75.dna.chromosome.22.fa.gz
	fi
	gunzip -f Homo_sapiens.GRCh37.75.dna.chromosome.22.fa.gz
fi
if [ ! -f Homo_sapiens.GRCh37.75.dna.chromosome.22.fa.fai ]
then
	samtools faidx Homo_sapiens.GRCh37.75.dna.chromosome.22.fa
fi
rm -rf work_file
# V_Next test 
python ${V_Next_dir}/V_Next/python/preprocess.py \
	--mode call \
	--reference Homo_sapiens.GRCh37.75.dna.chromosome.22.fa \
	--region_bed ${test_dir}/region.bed \
	--tumor_bam ${test_dir}/tumor.bam \
	--normal_bam ${test_dir}/normal.bam \
	--work work_file \
	--scan_maf 0.05 \
	--min_mapq 10 \
	--snp_min_af 0.05 \
	--snp_min_bq 20 \
	--snp_min_ao 10 \
	--ins_min_af 0.05 \
	--del_min_af 0.05 \
	--num_threads 1 \
	--scan_alignments_binary ${V_Next_dir}/V_Next/bin/scan_alignments

CUDA_VISIBLE_DEVICES= python ${V_Next_dir}/V_Next/python/call.py \
		--candidates_tsv work_file/dataset/*/candidates*.tsv \
		--reference Homo_sapiens.GRCh37.75.dna.chromosome.22.fa \
		--out work_file \
		--checkpoint ${V_Next_dir}/V_Next/models/DREAM.pth \
		--num_threads 1 \
		--batch_size 100

python ${V_Next_dir}/V_Next/python/postprocess.py \
		--reference Homo_sapiens.GRCh37.75.dna.chromosome.22.fa \
		--tumor_bam ${test_dir}/tumor.bam \
		--pred_vcf work_file/pred.vcf \
		--candidates_vcf work_file/work_tumor/filtered_candidates.vcf \
		--output_vcf work_file/V_Next.vcf \
		--work work_file 



cd ..

file1=${test_dir}/example/work_file/V_Next.vcf
file2=${test_dir}/V_Next.vcf

cmp --silent $file1 $file2 && echo "### V_Next: SUCCESS! ###" \
|| echo "### V_Next FAILED: Files ${file1} and ${file2} Are Different! ###"

