#! /bin/bash

rm -fr images/*
rm -fr nohup.out *.recode annotations/xmls/*

# backup previous model
PREV_MODEL_NAME="learned_models_"`date "+%Y%m%d%H%M%S"`
echo "[${PREV_MODEL_NAME}]" >> backup_models/description_list.txt
cat learned_models/description.txt >> backup_models/description_list.txt
tar cfvz backup_models/${PREV_MODEL_NAME}.tar.gz learned_models # opposite operation: tar xfvz learned_models_*.tar.gz 
rm -fr learned_models/*

# generate barcode for training
python gen_barcode/gen_barcode.py

ls *.config >> learned_models/description.txt

# create tf recode
CUDA_VISIBLE_DEVICES=0 python create_tf_record.py

# train
cd models/research

rm -f nohup.out

export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
CUDA_VISIBLE_DEVICES=0 python object_detection/train.py --pipeline_config_path=../../ssd_mobilenet_v1.config --train_dir=../../learned_models --logtostderr

cd ../../
