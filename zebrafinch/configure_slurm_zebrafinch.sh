#!/bin/bash

#SBATCH -J slurm_zebrafinch_parallel # job name
#SBATCH -p cpu # partition
#SBATCH -N 1   # number of nodes
#SBATCH --mem 64G # memory pool for all cores
#SBATCH -n 10 # number of cores
#SBATCH -t 0-01:00 # time (D-HH:MM)
#SBATCH -o std_slurm/slurm.%x.%N.%j.out # write STDOUT
#SBATCH -e std_slurm/slurm.%x.%N.%j.err # write STDERR
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<user@email.com>

# Load the required modules
module load template-builder

# Set up QBATCH variables to configure parallel jobs that will be spawned by modelbuild.sh
export QBATCH_PPJ=1
export QBATCH_CHUNKSIZE=1
export QBATCH_CORES=24
export QBATCH_SYSTEM="slurm"
export QBATCH_QUEUE="cpu"
export QBATCH_MEM="128G"
export QBATCH_OPTIONS="--mail-type=ALL --mail-user=<user@email.com> --mem 128G"

# Define atlas-forge directory, species and template names, and average type
ATLAS_DIR="/ceph/neuroinformatics/neuroinformatics/atlas-forge"
SPECIES="ZebraFinch"
TEMP_NAME="template_sym_mixed_res-25um_n-20_avg-trimean"
AVE_TYPE="efficient_trimean"

TEMPLATE_DIR="${ATLAS_DIR}/${SPECIES}/templates/${TEMP_NAME}/"
INITIAL_TARGET="${ATLAS_DIR}/${SPECIES}/templates/sub-ZF8222f_res-25x25x25um_origin-asr_processed.nii_orig-asr_pad-extra-60_aligned.nii.gz"

if [ ! -d "${TEMPLATE_DIR}" ]; then
  mkdir $TEMPLATE_DIR
  echo "Created new template directory ${TEMPLATE_DIR}"
else
  echo "Continuing work on existing template in ${TEMPLATE_DIR}"
fi

if [ ! -f "${INITIAL_TARGET}" ]; then
  echo "Error: Initial target not found"
  exit 1
fi

# log the script to the output folder for traceability
cp $0 "${TEMPLATE_DIR}slurm_configuration_script_log.txt"

# And give whole NIU group read permission
chmod g+r "${TEMPLATE_DIR}slurm_configuration_script_log.txt"

# Path to the bash script that builds the template
BUILD_SCRIPT="${ATLAS_DIR}/build_template_with_slurm.sh"

if [ ! -f $BUILD_SCRIPT ]; then
  echo "Error: ${BUILD_SCRIPT} does not exist."
  exit 1
fi

# Run the script to build the template
bash $BUILD_SCRIPT --template-dir $TEMPLATE_DIR \
  --average-type $AVE_TYPE \
  --toggle-dry-run "--no-dry-run" \
  --walltime-short "10:00:00" \
  --walltime-linear "20:00:00" \
  --walltime-nonlinear "240:00:00" \
  --initial_target $INITIAL_TARGET

