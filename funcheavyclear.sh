#!/usr/bin/env bash

######### FULL PREPROC for PJMASK
# Author:  Stefano Moia
# Version: 1.0
# Date:    31.06.2019
#########


sub=$1
ses=$2
wdr=${3:-/data}

flpr=sub-${sub}_ses-${ses}

fdir=${wdr}/sub-${sub}/ses-${ses}/func_preproc
fmap=${wdr}/sub-${sub}/ses-${ses}/fmap_preproc

####################

######################################
######### Script starts here #########
######################################

cd ${fdir}

echo "************************************"
echo "*** Coping SBREF ${f} "
echo "************************************"
echo "************************************"

for img in *_task-breathhold_rec-magnitude_echo-1_sbref_cr*
do
	immv ${img} 99.${img}
done

for fld in *_meica
do
	mv ${fld} 99.${fld}
done

for fld in *_topup
do
	mv ${fld} 99.${fld}
done

rm -rf sub*.nii.gz

for img in *_task-breathhold_rec-magnitude_echo-1_sbref_cr*
do
	imcp ${img} ${img:3}
done

for fld in *_meica
do
	mv ${fld} ${fld:3}
done

for fld in *_topup
do
	mv ${fld} ${fld:3}
done

cd ${cwd}