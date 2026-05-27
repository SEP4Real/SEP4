import sys
import subprocess
from pathlib import Path

def run_step(command: list[str], description: str) -> None:
    print(f"\n==================================================")
    print(f"👉 Running Step: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"==================================================")
    
    try:
        # Run subprocess and stream output
        result = subprocess.run(command, check=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description} completed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed with exit code {e.returncode}.")
        sys.exit(e.returncode)

def main():
    MAL_DIR = Path(__file__).resolve().parent.parent
    scripts_dir = MAL_DIR / "scripts"
    
    # Define pipeline steps as executable command lists
    python_bin = sys.executable

    # Optional Step A: KETI Resampling (if interim file not found)
    keti_interim = MAL_DIR / "data" / "interim" / "keti_1min_resampled.csv"
    if not keti_interim.exists():
        run_step(
            [python_bin, str(scripts_dir / "resample_keti_data.py")],
            "Resampling KETI Data"
        )
    else:
        print("\nSkipping Step: KETI data resampling (interim file already exists).")

    # Optional Step B: HomeCoach Preparation (if interim file not found)
    homecoach_interim = MAL_DIR / "data" / "interim" / "HomeCoach_combined.csv"
    if not homecoach_interim.exists():
        run_step(
            [python_bin, str(scripts_dir / "prepare_homecoach.py")],
            "Preparing HomeCoach Data"
        )
    else:
        print("Skipping Step: HomeCoach data preparation (interim file already exists).")

    # Step 1: Merging & Unifying
    run_step(
        [python_bin, str(scripts_dir / "build_unified_environment_dataset.py")],
        "Merging and Unifying Datasets"
    )

    # Step 2: Imputation & Cleaning (Notebook 3 equivalent script)
    run_step(
        [python_bin, str(scripts_dir / "clean_and_impute_dataset.py")],
        "Dataset Cleaning and MICE Imputation"
    )

    # Step 3: Session Linearization
    run_step(
        [python_bin, str(scripts_dir / "linearize_session_windows.py")],
        "Session Linearization"
    )

    # Step 4: Target Propagation (using hierarchical strategy)
    run_step(
        [python_bin, str(scripts_dir / "fill_missing_targets.py"), "--strategy", "hierarchical"],
        "Target Imputation via Hierarchical Clustering"
    )

    # Step 5: Model Training
    run_step(
        [python_bin, str(scripts_dir / "train_model.py")],
        "Neural Network Model Training"
    )

    # Step 6: Real Data Linearization (runs only if real sensor history exists)
    real_sensor = MAL_DIR / "data" / "real" / "sensor_history.csv"
    if real_sensor.exists():
        run_step(
            [python_bin, str(scripts_dir / "linearize_and_glue.py")],
            "Real Data Preprocessing and Linearization"
        )
    else:
        print("\nSkipping Step: Real data preprocessing (real/sensor_history.csv not found).")

    print("\n==================================================")
    print("🎉 Pipeline executed successfully end-to-end!")
    print("==================================================")

if __name__ == "__main__":
    main()
