# V-Next
Somatic variant detection framework
# Requirements
VarNet has been tested on ubuntu 22.04 LTS.
Python=3.10
cmake=3.22.1
g++=11.4.0
conda install zlib=1.2.13 numpy=1.24.3 scipy=1.10.1 imageio=2.36.0
conda install pysam=0.22.1 pybedtools=0.10.0 samtools=1.13 tabix=1.11 bedtools=2.30.0 biopython=1.78 -c bioconda
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

V_Next will use GPUs in train/call steps if they are avilable.
CUDA_VISIBLE_DEVICES=0,1,2,3... python train.py
CUDA_VISIBLE_DEVICES=0,1,2,3... python call.py 




### V-Next 体细胞变异检测框架

#### 环境要求
VarNet 已在 Ubuntu 22.04 LTS 系统上完成测试，运行前请确保安装以下依赖：
```bash
# 基础环境
Python=3.10
cmake=3.22.1
g++=11.4.0

# 核心依赖
conda install zlib=1.2.13 numpy=1.24.3 scipy=1.10.1 imageio=2.36.0

# 生物信息学工具
conda install pysam=0.22.1 pybedtools=0.10.0 samtools=1.13 tabix=1.11 bedtools=2.30.0 biopython=1.78 -c bioconda
```

### 训练流程
#### 输入文件准备
- 肿瘤样本比对文件（BAM格式）
- 正常样本比对文件（BAM格式）
- 训练区域文件（BED格式）
- 真实体细胞变异文件（VCF格式）

#### 执行训练
```bash
# 数据预处理
python preprocess.py \
    --mode train \
    --reference ref.fa \
    --region_bed region.bed \
    --tumor_bam tumor.bam \
    --normal_bam normal.bam \
    --work work_train \
    --truth_vcf truth.vcf \
    --scan_alignments_binary ../bin/scan_alignments

# 模型训练（支持多线程）
python train.py \
    --candidates_tsv work_train/dataset/*/candidates*.tsv \
    --out work_train \
    --num_threads 8 \
    --batch_size 64
```

#### 断点续训
如需从预训练模型继续训练，可添加 `--checkpoint` 参数：
```bash
python train.py \
    --candidates_tsv work_train/dataset/*/candidates*.tsv \
    --out work_train \
    --checkpoint pretrained_model.pth \
    --num_threads 8 \
    --batch_size 64
```

### 变异检测流程
#### 输入文件准备
- 肿瘤样本比对文件（BAM格式）
- 正常样本比对文件（BAM格式）
- 检测区域文件（BED格式）
- 训练好的模型文件（PTH格式）

#### 执行变异检测
```bash
# 数据预处理
python preprocess.py \
    --mode call \
    --reference ref.fa \
    --region_bed region.bed \
    --tumor_bam tumor.bam \
    --normal_bam normal.bam \
    --work work_call \
    --scan_alignments_binary ../bin/scan_alignments

# 模型预测（支持GPU加速）
python call.py \
    --candidates_tsv work_call/dataset/*/candidates*.tsv \
    --reference ref.fa \
    --out work_call \
    --checkpoint work_train/some_checkpoint.pth \
    --num_threads 8 \
    --batch_size 64

# 后处理生成最终VCF
python postprocess.py \
    --reference ref.fa \
    --tumor_bam tumor.bam \
    --pred_vcf work_call/pred.vcf \
    --candidates_vcf work_call/work_tumor/filtered_candidates.vcf \
    --output_vcf work_call/V_Next.vcf \
    --work work_call
```

#### 最终结果
变异检测结果保存在：`work_call/V_Next.vcf`

### GPU加速使用说明
在训练和预测步骤中，V-Next会自动检测可用GPU。如需指定GPU，可使用以下方式：
```bash
# 使用指定GPU进行训练
CUDA_VISIBLE_DEVICES=0,1 python train.py [...]

# 使用指定GPU进行预测
CUDA_VISIBLE_DEVICES=0,1 python call.py [...]
```
