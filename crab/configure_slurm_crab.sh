#!/bin/bash

#SBATCH -J slurm_crab_parallel # job name
#SBATCH -p cpu # partition
#SBATCH -N 1   # number of nodes
#SBATCH --mem 32G # memory pool for all cores
#SBATCH -n 10 # number of cores
#SBATCH -t 0-01:00 # time (D-HH:MM)
#SBATCH -o slurm.%x.%N.%j.out # write STDOUT
#SBATCH -e slurm.%x.%N.%j.err # write STDERR
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<name@email.com>

# Load the required modules
module load /ceph/neuroinformatics/neuroinformatics/modules/modulefiles/template-builder/2024-12-02

# Set up QBATCH variables to configure parallel jobs that will be spawned by modelbuild.sh
export QBATCH_PPJ=5
export QBATCH_CHUNKSIZE=1
export QBATCH_CORES=1
export QBATCH_SYSTEM="slurm"
export QBATCH_QUEUE="cpu"
export QBATCH_MEM="32G"
export QBATCH_OPTIONS="--mail-type=ALL --mail-user=<name@email.com> --mem 32G"

# Define atlas-forge directory, species and template names, and average type
ATLAS_DIR="/ceph/neuroinformatics/neuroinformatics/atlas-forge"
SPECIES="Crab"
TEMP_NAME="template_sym_res-6um_n-5_avg-mean"
AVE_TYPE="mean"

TEMPLATE_DIR="${ATLAS_DIR}/${SPECIES}/templates/${TEMP_NAME}/"

if [ ! -d "${TEMPLATE_DIR}" ]; then
  mkdir $TEMPLATE_DIR
  echo "Created new template directory ${TEMPLATE_DIR}"
else
  echo "Continuing work on existing template in ${TEMPLATE_DIR}"
fi

# log the script to the output folder for traceability
cp $0 "${TEMPLATE_DIR}/slurm_configuration_script_log.txt"

# And give whole NIU group read permission
chmod g+r "${TEMPLATE_DIR}/slurm_configuration_script_log.txt"

# Path to the bash script that builds the template
BUILD_SCRIPT="${ATLAS_DIR}/build_template_with_slurm.sh"

if [ ! -f $BUILD_SCRIPT ]; then
  echo "Error: ${BUILD_SCRIPT} does not exist."
fi

# Run the script to build the template
bash $BUILD_SCRIPT --template-dir $TEMPLATE_DIR --average-type $AVE_TYPE --toggle-dry-run "--no-dry-run" 
