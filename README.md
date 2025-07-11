# V-Next
Somatic variant detection framework
# Requirements
VarNet has been tested on ubuntu 22.04 LTS.
### 输入文件要求

#### 训练模式（Training Mode）
需提供以下输入文件：
- tumor alignment file.bam（肿瘤样本比对文件）
- normal alignment file.bam（正常样本比对文件）
- training region file.bed（训练区域文件）
- truth somatic variant file.vcf（真实体细胞变异文件）

#### 调用模式（Calling Mode）
需提供以下输入文件：
- tumor alignment file.bam（肿瘤样本比对文件）
- normal alignment file.bam（正常样本比对文件）
- call region file.bed（调用区域文件）
- trained model file.pth（已训练的模型文件）
