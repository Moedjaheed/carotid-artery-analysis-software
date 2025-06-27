"""
Configuration file untuk Carotid Segmentation Project
Ubah parameter di sini untuk menyesuaikan dengan setup Anda
"""

import os

# =====================================
# ENVIRONMENT CONFIGURATIONS
# =====================================

# Conda/Virtual Environment
CONDA_ENV_NAME = "ridho-ta"
PYTHON_ENV_PATH = f"C:\\Users\\{os.getenv('USERNAME', 'User')}\\anaconda3\\envs\\{CONDA_ENV_NAME}"

# =====================================
# PATH CONFIGURATIONS
# =====================================

# Base paths - ubah sesuai lokasi Anda
PROJECT_BASE_PATH = r"D:\Ridho\TA\fix banget"
DATASET_BASE_PATH = r"D:\Ridho\TA\fix banget\Dataset"
TRAINING_DATA_PATH = r"D:\Ridho\TA\Common Carotid Artery Ultrasound Images"

# Training data paths
IMAGES_DIR = os.path.join(TRAINING_DATA_PATH, "US images")
MASKS_DIR = os.path.join(TRAINING_DATA_PATH, "masks")

# Model paths
MODEL_SAVE_PATH = os.path.join(PROJECT_BASE_PATH, "models")
BEST_MODEL_PATH = os.path.join(MODEL_SAVE_PATH, "best_unet_model.pth")
FINAL_MODEL_PATH = os.path.join(MODEL_SAVE_PATH, "final_unet_model.pth")
INFERENCE_MODEL_PATH = os.path.join(PROJECT_BASE_PATH, "UNet_25Mei_Sore.pth")

# Output paths
RESULTS_PATH = os.path.join(PROJECT_BASE_PATH, "results")
VIDEOS_OUTPUT_PATH = os.path.join(RESULTS_PATH, "videos")
PLOTS_OUTPUT_PATH = os.path.join(RESULTS_PATH, "plots")
CSV_OUTPUT_PATH = os.path.join(RESULTS_PATH, "csv_data")
SYNC_OUTPUT_PATH = os.path.join(RESULTS_PATH, "synced_data")

# =====================================
# TRAINING CONFIGURATIONS
# =====================================

# Model parameters
INPUT_CHANNELS = 1
OUTPUT_CHANNELS = 1
IMAGE_SIZE = (256, 256)

# Training parameters
BATCH_SIZE = 8
LEARNING_RATE = 0.001
EPOCHS = 50
VALIDATION_SPLIT = 0.15
TEST_SPLIT = 0.15

# Data augmentation parameters
AUGMENTATION_PARAMS = {
    'horizontal_flip_prob': 0.5,
    'rotation_limit': 10,
    'shift_scale_rotate_prob': 0.5,
    'gaussian_blur_prob': 0.3,
    'gaussian_noise_prob': 0.3,
    'brightness_contrast_prob': 0.5,
    'elastic_transform_prob': 0.3
}

# Loss function parameters
LOSS_ALPHA = 0.5  # BCE vs Dice loss weight

# Optimizer parameters
OPTIMIZER_PARAMS = {
    'lr': LEARNING_RATE,
    'weight_decay': 1e-5,
    'betas': (0.9, 0.999)
}

# Scheduler parameters
SCHEDULER_PARAMS = {
    'mode': 'min',
    'factor': 0.1,
    'patience': 5,
    'min_lr': 1e-7
}

# =====================================
# INFERENCE CONFIGURATIONS
# =====================================

# Video processing parameters
PIXEL_TO_MM_RATIO = 0.1  # Sesuaikan dengan kalibrasi Anda
SEGMENTATION_THRESHOLD = 0.5
MAX_DISPLAY_WIDTH = 400  # untuk preview di data viewer

# Video codec settings
VIDEO_CODEC = 'mp4v'
VIDEO_QUALITY = 80

# =====================================
# DATA SYNCHRONIZATION CONFIGURATIONS
# =====================================

# Interpolation parameters
INTERPOLATION_METHOD = 'linear'
EXTRAPOLATION_FILL_VALUE = "extrapolate"

# Analysis parameters
CORRELATION_MIN_SAMPLES = 10  # minimum samples untuk hitung korelasi

# =====================================
# GUI CONFIGURATIONS
# =====================================

# Data viewer settings
GUI_WINDOW_SIZE = "1400x900"
IMAGE_DISPLAY_MAX_WIDTH = 400
PLOT_FIGURE_SIZE = (10, 6)

# Launcher settings
LAUNCHER_WINDOW_SIZE = "600x400"

# =====================================
# SUBJECT CONFIGURATIONS
# =====================================

# Subject numbers to process
SUBJECT_NUMBERS = list(range(1, 8))  # [1, 2, 3, 4, 5, 6, 7]

# Subject file name patterns
SUBJECT_VIDEO_PATTERN = "Subjek{}.mp4"
SUBJECT_PRESSURE_PATTERN = "subject{}.csv"
SUBJECT_TIMESTAMP_PATTERN = "timestamps.csv"

# =====================================
# OUTPUT FILE PATTERNS
# =====================================

# Video inference outputs
VIDEO_OUTPUT_PATTERN = "subjek{}_hasil_segmentasi_video_diameter.mp4"
PLOT_OUTPUT_PATTERN = "subjek{}_diameter_vs_frame.png"
CSV_OUTPUT_PATTERN = "subjek{}_diameter_data.csv"

# Data sync outputs
SYNC_DATA_PATTERN = "synced_data_subject{}.csv"
SYNC_PLOT_PATTERN = "synced_data_plot_subject{}.png"
SYNC_SUMMARY_FILE = "synchronization_summary.csv"

# =====================================
# LOGGING CONFIGURATIONS
# =====================================

# Wandb settings
WANDB_PROJECT = "carotid-segmentation"
WANDB_ENTITY = None  # Set to your wandb username if needed

# Progress reporting
PROGRESS_UPDATE_INTERVAL = 100  # frames

# =====================================
# VALIDATION FUNCTIONS
# =====================================

def validate_paths():
    """Validasi dan buat direktori yang diperlukan"""
    required_dirs = [
        MODEL_SAVE_PATH,
        RESULTS_PATH,
        VIDEOS_OUTPUT_PATH,
        PLOTS_OUTPUT_PATH,
        CSV_OUTPUT_PATH,
        SYNC_OUTPUT_PATH
    ]
    
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    return True

def get_subject_paths(subject_number):
    """
    Dapatkan semua path untuk subjek tertentu
    
    Args:
        subject_number (int): Nomor subjek
        
    Returns:
        dict: Dictionary berisi semua path
    """
    subject_folder = f"Subjek{subject_number}"
    base_path = os.path.join(DATASET_BASE_PATH, subject_folder)
    
    paths = {
        'video': os.path.join(base_path, SUBJECT_VIDEO_PATTERN.format(subject_number)),
        'pressure': os.path.join(base_path, SUBJECT_PRESSURE_PATTERN.format(subject_number)),
        'timestamps': os.path.join(base_path, SUBJECT_TIMESTAMP_PATTERN),
        'output_video': os.path.join(VIDEOS_OUTPUT_PATH, VIDEO_OUTPUT_PATTERN.format(subject_number)),
        'output_plot': os.path.join(PLOTS_OUTPUT_PATH, PLOT_OUTPUT_PATTERN.format(subject_number)),
        'output_csv': os.path.join(CSV_OUTPUT_PATH, CSV_OUTPUT_PATTERN.format(subject_number)),
        'sync_data': os.path.join(SYNC_OUTPUT_PATH, SYNC_DATA_PATTERN.format(subject_number)),
        'sync_plot': os.path.join(SYNC_OUTPUT_PATH, SYNC_PLOT_PATTERN.format(subject_number))
    }
    
    return paths

def check_requirements():
    """
    Cek apakah semua requirement terpenuhi
    
    Returns:
        tuple: (success, missing_items)
    """
    missing_items = []
    
    # Check training data
    if not os.path.exists(IMAGES_DIR):
        missing_items.append(f"Images directory: {IMAGES_DIR}")
    
    if not os.path.exists(MASKS_DIR):
        missing_items.append(f"Masks directory: {MASKS_DIR}")
    
    # Check dataset
    if not os.path.exists(DATASET_BASE_PATH):
        missing_items.append(f"Dataset directory: {DATASET_BASE_PATH}")
    
    # Check model for inference
    if not os.path.exists(INFERENCE_MODEL_PATH):
        missing_items.append(f"Inference model: {INFERENCE_MODEL_PATH}")
    
    return len(missing_items) == 0, missing_items

# =====================================
# INITIALIZATION
# =====================================

# Create required directories on import
validate_paths()

# Print configuration summary when imported
if __name__ == "__main__":
    print("=== Carotid Segmentation Configuration ===")
    print(f"Project Base: {PROJECT_BASE_PATH}")
    print(f"Dataset Base: {DATASET_BASE_PATH}")
    print(f"Training Images: {IMAGES_DIR}")
    print(f"Training Masks: {MASKS_DIR}")
    print(f"Model Save Path: {MODEL_SAVE_PATH}")
    print(f"Results Path: {RESULTS_PATH}")
    print(f"Subjects: {SUBJECT_NUMBERS}")
    
    success, missing = check_requirements()
    if success:
        print("[SUCCESS] All requirements met!")
    else:
        print("[ERROR] Missing requirements:")
        for item in missing:
            print(f"   - {item}")
