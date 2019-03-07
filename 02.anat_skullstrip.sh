#!/usr/bin/env bash

######### ANATOMICAL 01 for PJMASK
# Author:  Stefano Moia
# Version: 0.1
# Date:    06.02.2019
#########

## Variables
# anat
anat=$1
# folders
adir=$2

## Optional
# mask
mask=${3:-none}
aref=${4:-none}

######################################
######### Script starts here #########
######################################

cwd=$(pwd)

cd ${adir}

if [[ "${mask}" == "none" ]]
then
	echo "Skull Stripping ${anat}"
	3dSkullStrip -input ${anat}_bfc.nii.gz \
	-prefix ${anat}_brain.nii.gz \
	-orig_vol -overwrite
	fslmaths ${anat}_brain -bin ${anat}_brain_mask
	mask=${anat}_brain_mask
else
	if [[ -e "${mask}_brain_mask.nii.gz" ]]
	then
		mask=${mask}_brain_mask
	fi
	echo "Masking ${anat}"
	fslmaths ${anat}_bfc -mas ${mask} ${anat}_brain
	fslmaths ${anat}_brain -bin ${anat}_brain_mask
fi

if [[ "${aref}" != "none" ]]
then
	echo "Flirting ${mask} into ${aref}"
	flirt -in ${mask} -ref ${aref} -cost normmi -searchcost normmi \
	-init ../reg/${anat}2${aref}_fsl.mat -o ${aref}_brain_mask \
	-applyxfm -interp nearestneighbour
fi
	

cd ${cwd}