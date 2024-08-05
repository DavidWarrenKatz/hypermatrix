# config_and_print.py
bam_directory = '/home/dwk681/workspace/cluster_cells_from_GSE189158_NOMe_HiC/filesFromCluster/bam'
software_directory = '../../bin/softwarefiles'
chrom_file = f"{software_directory}/hg19.autosome.chrom.sizes"
fragments_file = f"{software_directory}/hg19_DpnII.txt"
output_directory = '../../projects/single_cell_files'
filtered_list = f"{output_directory}/filtered_bam_list.txt"
schicluster_env = 'schicluster2'
bisulfite_env = 'bisulfitehic27'
min_high_quality_reads=250000

print(f"bam_directory='{bam_directory}'")
print(f"software_directory='{software_directory}'")
print(f"chrom_file='{chrom_file}'")
print(f"fragments_file='{fragments_file}'")
print(f"output_directory='{output_directory}'")
print(f"filtered_list='{filtered_list}'")
print(f"schicluster_env='{schicluster_env}'")
print(f"bisulfite_env='{bisulfite_env}'")
print(f"min_high_quality_reads='{min_high_quality_reads}'")

