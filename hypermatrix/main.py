#!/usr/bin/env python3
# file: hypermatrix/main.py

import pkg_resources
import argparse
import subprocess
import os
import sys

# Set the script directory and config file path
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.py')
sys.path.append(script_dir)

# Import config file
from config import config

VERSION = """
Hypermatrix version 0.1 - A tool for integrating
multi-omics data and epigenetic analysis using
advanced tensor techniques.
"""

def main():
    parser = argparse.ArgumentParser(description='Hypermatrix command-line tool')
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    # Subcommands
    subparsers = parser.add_subparsers(dest='command')

    # preprocess subcommand
    preprocess_parser = subparsers.add_parser('preprocess', help='Preprocess BAM files for analysis')
    preprocess_parser.add_argument('--nomehic', action='store_true', help='Process BAM files from the scNOMe-HiC technique')
    preprocess_parser.add_argument('--m3C', action='store_true', help='Process BAM files from the m3C-seq technique')
    preprocess_parser.add_argument('--input_dir', type=str, required=True, help='Directory containing BAM files')
    preprocess_parser.add_argument('--output_dir', type=str, required=True, help='Directory where the output files will be saved')
    preprocess_parser.add_argument('--ref_genome', type=str, required=True, help='Reference genome (e.g., hg19 or hg38)')

    # ABcluster subcommand
    abcluster_parser = subparsers.add_parser('ABcluster', help='Run the ABcluster analysis')
    abcluster_parser.add_argument('--methy', type=str, help='Path to the single-cell CpG methylation directory')
    abcluster_parser.add_argument('--hic', type=str, help='Path to the single-cell chromosome conformation directory')
    abcluster_parser.add_argument('--output_dir', type=str, help='Directory where the output files will be saved')
    abcluster_parser.add_argument('-cumulant', action='store_true', help='Run cumulant shell script')
    abcluster_parser.add_argument('-impute', action='store_true', help='Run impute shell script')
    abcluster_parser.add_argument('-genome_id', type=str, help='Reference genome (e.g., hg19 or hg38)')
    abcluster_parser.add_argument('-res', type=str, help='Resolution, size of genomic bins')

    # differentiate_chromosomes subcommand
    diffchrom_parser = subparsers.add_parser('differentiate_chromosomes', help='Analyze distinct A/B compartments for homologous chromosomes')
    diffchrom_parser.add_argument('--hic_file', type=str, help='Path to the Hi-C data file')
    diffchrom_parser.add_argument('--epigenetic_file', type=str, help='Path to the epigenetic data file (optional)')
    diffchrom_parser.add_argument('--output_dir', type=str, help='Directory where the output files will be saved')

    args = parser.parse_args()


    # Dispatch the command
    if args.command == 'ABcluster':
        abcluster(args)
    elif args.command == 'differentiate_chromosomes':
        diffchrom(args)
    elif args.command == 'preprocess':
        preprocess(args)
    else:
        print(f"Unknown command: {args.command}. Try the ABcluster, differentiate_chromosomes, or preprocess command")
        parser.print_help()

def update_config_file(config_file_path, updates):
    """
    Function to update multiple config values in the config.py file.
    Args:
    - config_file_path (str): Path to the config.py file.
    - updates (dict): Dictionary of config parameters to update.
    """
    with open(config_file_path, 'r') as file:
        lines = file.readlines()

    with open(config_file_path, 'w') as file:
        for line in lines:
            for key, value in updates.items():
                if line.startswith(f'{key} ='):
                    line = f"{key} = '{value}'\n"
            file.write(line)

    print(f"[INFO]: Updated config values in {config_file_path}")

def abcluster(args):
    # Collect updates for the config file
    updates = {}
    if args.methy:
        updates['methy_directory'] = args.methy
    if args.hic:
        updates['bam_directory'] = args.hic
    if args.output_dir:
        updates['output_directory'] = args.output_dir
    if args.genome_id:
        updates['reference_genome'] = args.genome_id
    if args.res:
        updates['resolutions'] = args.res

    # Apply the updates to the config.py file if any
    if updates:
        update_config_file(config_path, updates)

    # Now run the appropriate script based on the flags provided
    standard_script = "/utilities/single-cell/standard_pipeline/single_cell_pipeline.sh"
    cumulant_script = "/utilities/single-cell/cumulant_pipeline/single_cell_pipeline_cumulant.sh"
    impute_script = "/utilities/single-cell/impute_pipeline/single_cell_pipeline_impute.sh"

    # Decide which script to run
    if args.cumulant:
        run_shell_script(cumulant_script)
    elif args.impute:
        run_shell_script(impute_script)
    else:
        run_shell_script(standard_script)

def diffchrom(args):
    # Hi-C and epigenetic analysis based on the differentiate_chromosomes command
    hic_file = args.hic_file if args.hic_file else config['bam_directory']
    epigenetic_file = args.epigenetic_file if args.epigenetic_file else None
    output_dir = args.output_dir if args.output_dir else config['output_directory']

    # Placeholder for actual analysis code
    print(f"Running differentiate_chromosomes with Hi-C file: {hic_file}, Epigenetic file: {epigenetic_file}, Output directory: {output_dir}")
    # Add the actual analysis code for differentiating chromosomes here

def preprocess(args):
    # Check that either --nomehic or --m3C flag is provided
    if not args.nomehic and not args.m3C:
        print("[ERROR]: Either the --nomehic flag or the --m3C flag is required.")
        sys.exit(1)

    # Preprocess BAM files for analysis
    input_dir = args.input_dir
    output_dir = args.output_dir
    ref_genome = args.ref_genome

    # Set appropriate scripts based on the flags provided
    preprocess_script = "nomehic_preprocess.sh" if args.nomehic else "m3C_preprocess.sh"
    preprocess_script_path = os.path.join(script_dir, 'utilities', 'single-cell', preprocess_script)

    # Make sure the script is executable
    if not os.access(preprocess_script_path, os.X_OK):
        print(f"[INFO]: Adding executable permissions to {preprocess_script_path}.")
        os.chmod(preprocess_script_path, 0o755)

    # Construct and run the shell command
    command = f"{preprocess_script_path} --input {input_dir} --output {output_dir} --ref_genome {ref_genome}"
    print(f"[INFO]: Executing preprocess command: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[INFO]: Preprocessing completed successfully. Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR]: Preprocessing failed with return code {e.returncode}. Error message:\n{e.stderr}")

def run_shell_script(script_name):
    # Resolve the full path of the script using pkg_resources
    full_script_path = pkg_resources.resource_filename('hypermatrix', os.path.join('utilities', 'single-cell', script_name))
    print(f"[INFO]: Script path resolved to: {full_script_path}")

    # Ensure the script is executable
    if not os.access(full_script_path, os.X_OK):
        print(f"[INFO]: Adding executable permissions to {full_script_path}.")
        os.chmod(full_script_path, 0o755)

    # Execute the shell script
    command = f"{full_script_path}"
    print(f"[INFO]: Executing command: {command}")

    # Run the command and capture output
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[INFO]: Command executed successfully. Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR]: Command failed with return code {e.returncode}. Error message:\n{e.stderr}")

if __name__ == "__main__":
    main()

