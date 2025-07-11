### V-Next Somatic Variant Detection Framework

#### Environment Requirements
VarNet has been tested on Ubuntu 22.04 LTS. Ensure the following dependencies are installed:
```bash
# Base Environment
Python=3.10
cmake=3.22.1
g++=11.4.0

# Core Dependencies
conda install zlib=1.2.13 numpy=1.24.3 scipy=1.10.1 imageio=2.36.0

# Bioinformatics Tools
conda install pysam=0.22.1 pybedtools=0.10.0 samtools=1.13 tabix=1.11 bedtools=2.30.0 biopython=1.78 -c bioconda
```

### Training Workflow
#### Input Files Preparation
- Tumor alignment file (BAM format)
- Normal alignment file (BAM format)
- Training region file (BED format)
- Truth somatic variant file (VCF format)

#### Execute Training
```bash
# Data Preprocessing
python preprocess.py \
    --mode train \
    --reference ref.fa \
    --region_bed region.bed \
    --tumor_bam tumor.bam \
    --normal_bam normal.bam \
    --work work_train \
    --truth_vcf truth.vcf \
    --scan_alignments_binary ../bin/scan_alignments

# Model Training (Supports Multi-threading)
python train.py \
    --candidates_tsv work_train/dataset/*/candidates*.tsv \
    --out work_train \
    --num_threads 8 \
    --batch_size 64
```

#### Resume Training from Checkpoint
To continue training from a pre-trained model, use the `--checkpoint` parameter:
```bash
python train.py \
    --candidates_tsv work_train/dataset/*/candidates*.tsv \
    --out work_train \
    --checkpoint pretrained_model.pth \
    --num_threads 8 \
    --batch_size 64
```

### Variant Calling Workflow
#### Input Files Preparation
- Tumor alignment file (BAM format)
- Normal alignment file (BAM format)
- Calling region file (BED format)
- Trained model file (PTH format)

#### Execute Variant Calling
```bash
# Data Preprocessing
python preprocess.py \
    --mode call \
    --reference ref.fa \
    --region_bed region.bed \
    --tumor_bam tumor.bam \
    --normal_bam normal.bam \
    --work work_call \
    --scan_alignments_binary ../bin/scan_alignments

# Model Prediction (Supports GPU Acceleration)
python call.py \
    --candidates_tsv work_call/dataset/*/candidates*.tsv \
    --reference ref.fa \
    --out work_call \
    --checkpoint work_train/some_checkpoint.pth \
    --num_threads 8 \
    --batch_size 64

# Postprocessing to Generate Final VCF
python postprocess.py \
    --reference ref.fa \
    --tumor_bam tumor.bam \
    --pred_vcf work_call/pred.vcf \
    --candidates_vcf work_call/work_tumor/filtered_candidates.vcf \
    --output_vcf work_call/V_Next.vcf \
    --work work_call
```

#### Final Output
The final variant calling results are saved in: `work_call/V_Next.vcf`

### GPU Acceleration Instructions
V-Next will automatically detect available GPUs during training and prediction. To specify GPUs, use:
```bash
# Train with specific GPUs
CUDA_VISIBLE_DEVICES=0,1 python train.py [...]

# Predict with specific GPUs
CUDA_VISIBLE_DEVICES=0,1 python call.py [...]
```
