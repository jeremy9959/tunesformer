#!/bin/bash
#SBATCH --nodes=1
#SBATCH --tasks=8
#SBATCH --mem=64G
#SBATCH --partition=general-gpu
#SBATCH --gres=gpu:1
#SBATCH --mail-type=FAIL,END
#SBATCH --time=12:00:00
#SBATCH --mail-user=jeremy.teitelbaum@uconn.edu

cd $HOME
source .bashrc
conda activate torch-310
export HF_DATASETS_CACHE="$HOME/scratch/.cache/huggingface/datasets"
cd $HOME/tunesformer
echo "Running....."
echo `pwd`
which python
python train.py 

