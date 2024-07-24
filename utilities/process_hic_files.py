import numpy as np
import h5py
import os
import sys

def load_hic_matrix(file_path):
    try:
        with h5py.File(file_path, 'r') as hf:
            matrix = hf['matrix'][:]
        return matrix
    except Exception as e:
        print(f"[ERROR] Failed to load Hi-C matrix from {file_path}: {e}")
        return None

def load_dark_bins(file_path):
    try:
        with h5py.File(file_path, 'r') as hf:
            dark_bins = hf['dark_bins_indices'][:]
        return dark_bins
    except Exception as e:
        print(f"[ERROR] Failed to load dark bins from {file_path}: {e}")
        return None

def remove_dark_bins(matrix, dark_bins):
    try:
        mask = np.ones(matrix.shape[0], dtype=bool)
        mask[dark_bins] = False
        filtered_matrix = matrix[mask][:, mask]
        return filtered_matrix
    except Exception as e:
        print(f"[ERROR] Failed to remove dark bins: {e}")
        return None

def compute_correlation_matrix(matrix):
    try:
        correlation_matrix = np.corrcoef(matrix)
        return correlation_matrix
    except Exception as e:
        print(f"[ERROR] Failed to compute correlation matrix: {e}")
        return None

def compute_degree_2_cumulant(matrix):
    try:
        n, m = matrix.shape
        mean_vec = np.mean(matrix, axis=1)
        std_vec = np.std(matrix, axis=1)

        degree_2_cumulant = np.zeros((n, n, n))
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    numerator = np.sum((matrix[i] - mean_vec[i]) * (matrix[j] - mean_vec[j]) * (matrix[k] - mean_vec[k]))
                    denominator = np.sqrt(np.sum((matrix[i] - mean_vec[i])**2) * np.sum((matrix[j] - mean_vec[j])**2) * np.sum((matrix[k] - mean_vec[k])**2))
                    degree_2_cumulant[i, j, k] = numerator / denominator if denominator != 0 else 0
        return degree_2_cumulant
    except Exception as e:
        print(f"[ERROR] Failed to compute degree-2 cumulant: {e}")
        return None

def process_hic_files(path, resolutions, chromosomes, data_types):
    for resolution in resolutions:
        for chromosome in chromosomes:
            for data_type in data_types:
                hic_file = f'{path}Workspaces/individual/ch{chromosome}_res{resolution}_{data_type}_KR.h5'
                dark_bins_file = f'{path}Workspaces/individual/ch{chromosome}_res{resolution}_darkBins.h5'
                
                hic_matrix = load_hic_matrix(hic_file)
                dark_bins = load_dark_bins(dark_bins_file)

                if hic_matrix is not None and dark_bins is not None:
                    filtered_matrix = remove_dark_bins(hic_matrix, dark_bins)
                    if filtered_matrix is not None:
                        correlation_matrix = compute_correlation_matrix(filtered_matrix)
                        degree_2_cumulant = compute_degree_2_cumulant(filtered_matrix)
                        if correlation_matrix is not None:
                            output_file = f'{path}Workspaces/individual/ch{chromosome}_res{resolution}_{data_type}_KR_corr.h5'
                            try:
                                with h5py.File(output_file, 'w') as hf:
                                    hf.create_dataset('correlation_matrix', data=correlation_matrix)
                                print(f'[INFO] Saved correlation matrix to {output_file}')
                            except Exception as e:
                                print(f"[ERROR] Failed to save correlation matrix: {e}")

                        if degree_2_cumulant is not None:
                            output_file = f'{path}Workspaces/individual/ch{chromosome}_res{resolution}_{data_type}_KR_cumulant.h5'
                            try:
                                with h5py.File(output_file, 'w') as hf:
                                    hf.create_dataset('degree_2_cumulant', data=degree_2_cumulant)
                                print(f'[INFO] Saved degree-2 cumulant matrix to {output_file}')
                            except Exception as e:
                                print(f"[ERROR] Failed to save degree-2 cumulant matrix: {e}")

if __name__ == "__main__":
    data_path = sys.argv[1]
    resolutions_list = sys.argv[2].split(',')
    chromosomes_list = sys.argv[3].split(',')
    data_types_list = sys.argv[4].split(',')
    process_hic_files(data_path, resolutions_list, chromosomes_list, data_types_list)
