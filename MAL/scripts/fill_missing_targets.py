from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA


MAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = MAL_DIR / "data"

DEFAULT_INPUT_PATH = DATA_DIR / "processed" / "linearized_sessions_with_missing_targets.csv"
DEFAULT_OUTPUT_PATH = DATA_DIR / "processed" / "linearized_session_windows.csv"
RANDOM_STATE = 42
DEFAULT_N_CLUSTERS = 5


def generate_visualizations(
    df: pd.DataFrame,
    x_scaled: np.ndarray,
    cluster_labels: np.ndarray,
    n_clusters: int,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Rating Distribution Plot (Bar chart)
    plt.figure(figsize=(8, 5))
    rating_counts = df["rating"].value_counts(dropna=False).sort_index()
    
    # Convert index to string for plotting to handle NaN nicely
    x_labels = [str(x) if pd.notna(x) else "NaN (Unfilled)" for x in rating_counts.index]
    
    plt.bar(x_labels, rating_counts.values, color="skyblue", edgecolor="black")
    plt.xlabel("Rating Value")
    plt.ylabel("Session/Segment Count")
    plt.title("Distribution of Segment Ratings (Final Filled Dataset)")
    for i, v in enumerate(rating_counts.values):
        plt.text(i, v + (max(rating_counts.values) * 0.01), str(v), ha='center', va='bottom', fontweight='bold')
    
    rating_plot_path = output_dir / "rating_distribution.png"
    plt.tight_layout()
    plt.savefig(rating_plot_path, dpi=150)
    plt.close()
    print(f"Saved rating distribution plot to: {rating_plot_path}")

    # 2. PCA Clusters Plot (2D Projection)
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    x_pca = pca.fit_transform(x_scaled)
    
    # Compute cluster centroids in 2D space
    centroids_pca = []
    for c in range(n_clusters):
        cluster_points = x_pca[cluster_labels == c]
        if len(cluster_points) > 0:
            centroids_pca.append(cluster_points.mean(axis=0))
        else:
            centroids_pca.append([0.0, 0.0])
    centroids_pca = np.array(centroids_pca)

    plt.figure(figsize=(10, 8))
    
    # Use discrete colormap setup to fix ticks and colors
    cmap = plt.colormaps.get_cmap("tab10")
    # Wrap colormap with discrete bounds to center colors on integers
    import matplotlib.colors as mcolors
    bounds = np.arange(n_clusters + 1) - 0.5
    norm = mcolors.BoundaryNorm(bounds, n_clusters)
    
    scatter = plt.scatter(
        x_pca[:, 0],
        x_pca[:, 1],
        c=cluster_labels,
        cmap=cmap,
        norm=norm,
        alpha=0.6,
        edgecolors="none",
        s=15,
    )
    
    # Plot centroids
    plt.scatter(
        centroids_pca[:, 0],
        centroids_pca[:, 1],
        c="red",
        marker="X",
        s=200,
        label="Centroids",
        edgecolors="black",
    )
    
    plt.xlabel(f"PCA Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
    plt.ylabel(f"PCA Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
    plt.title("2D PCA Projection of Segment Clusters")
    
    # Configure discrete ticks on colorbar
    cb = plt.colorbar(scatter, label="Cluster Label")
    cb.set_ticks(np.arange(n_clusters))
    cb.set_ticklabels([f"Cluster {i}" for i in range(n_clusters)])
    
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    
    pca_plot_path = output_dir / "pca_clusters.png"
    plt.tight_layout()
    plt.savefig(pca_plot_path, dpi=150)
    plt.close()
    print(f"Saved PCA clusters plot to: {pca_plot_path}")


def fill_missing_targets_via_clustering(
    df: pd.DataFrame,
    n_clusters: int = DEFAULT_N_CLUSTERS,
    random_state: int = RANDOM_STATE,
    strategy: str = "mean",
    enable_overrides: bool = True,
) -> tuple[pd.DataFrame, dict[str, any]]:
    filled_df = df.copy()
    
    # 1. Identify feature columns for clustering
    clustering_features = []
    for col in filled_df.columns:
        if col in ["duration_minutes", "n_readings"] or any(
            col.endswith(f"_{suffix}")
            for suffix in ["mean", "min", "max", "std", "latest", "count", "range"]
        ):
            clustering_features.append(col)

    print(f"Features used for clustering ({len(clustering_features)}): {', '.join(clustering_features)}")

    # 2. Impute missing feature values
    imputer = SimpleImputer(strategy="median")
    x_imputed = imputer.fit_transform(filled_df[clustering_features])

    # 3. Scale features
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_imputed)

    # Setup random state for sampling
    rng = np.random.default_rng(random_state)

    cluster_reports = {}
    unfillable_clusters = []

    if strategy in ["mean", "sample"]:
        # 4. Cluster using KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        filled_df["cluster"] = kmeans.fit_predict(x_scaled)

        for cluster_id in range(n_clusters):
            cluster_mask = filled_df["cluster"] == cluster_id
            cluster_df = filled_df[cluster_mask]
            
            labeled_subset = cluster_df.dropna(subset=["focus_score"])
            n_total = len(cluster_df)
            n_labeled = len(labeled_subset)
            n_missing = n_total - n_labeled

            if n_labeled > 0:
                if strategy == "mean":
                    fill_value = int(round(labeled_subset["focus_score"].mean()))
                    filled_df.loc[cluster_mask & filled_df["focus_score"].isna(), "focus_score"] = fill_value
                    fill_desc = f"{fill_value} (mean)"
                else:
                    # 'sample' strategy
                    counts = labeled_subset["focus_score"].value_counts(normalize=True)
                    possible_values = counts.index.values
                    probs = counts.values
                    
                    missing_mask = cluster_mask & filled_df["focus_score"].isna()
                    n_to_fill = missing_mask.sum()
                    if n_to_fill > 0:
                        sampled_values = rng.choice(possible_values, size=n_to_fill, p=probs)
                        filled_df.loc[missing_mask, "focus_score"] = sampled_values
                    fill_desc = f"Sampled from {dict(zip(possible_values, np.round(probs, 2)))}"
                
                cluster_reports[f"Cluster {cluster_id}"] = {
                    "total_sessions": n_total,
                    "labeled_sessions": n_labeled,
                    "missing_sessions": n_missing,
                    "mean_target": float(labeled_subset["focus_score"].mean()),
                    "fill_value_assigned": fill_desc,
                    "status": "Filled"
                }
            else:
                unfillable_clusters.append(cluster_id)
                cluster_reports[f"Cluster {cluster_id}"] = {
                    "total_sessions": n_total,
                    "labeled_sessions": 0,
                    "missing_sessions": n_missing,
                    "mean_target": None,
                    "fill_value_assigned": None,
                    "status": "Unfillable (Lack of Data)"
                }

    elif strategy == "hierarchical":
        # Strategy B: Iterative / Hierarchical propagation
        k_sequence = [50, 20, 10, n_clusters]
        
        filled_df["temp_focus_score"] = filled_df["focus_score"]
        
        for step_idx, K in enumerate(k_sequence):
            kmeans = KMeans(n_clusters=K, random_state=random_state, n_init=10)
            step_clusters = kmeans.fit_predict(x_scaled)
            
            filled_count_this_step = 0
            
            for cid in range(K):
                cluster_mask = step_clusters == cid
                cluster_df = filled_df[cluster_mask]
                
                labeled_subset = cluster_df.dropna(subset=["temp_focus_score"])
                n_total = len(cluster_df)
                n_labeled = len(labeled_subset)
                n_missing = (cluster_df["temp_focus_score"].isna()).sum()
                
                if n_labeled > 0 and n_missing > 0:
                    counts = labeled_subset["temp_focus_score"].value_counts(normalize=True)
                    possible_values = counts.index.values
                    probs = counts.values
                    
                    missing_mask = cluster_mask & filled_df["temp_focus_score"].isna()
                    sampled_values = rng.choice(possible_values, size=n_missing, p=probs)
                    filled_df.loc[missing_mask, "temp_focus_score"] = sampled_values
                    filled_count_this_step += n_missing
                    
            print(f"Hierarchical step {step_idx+1} (K={K}): Filled {filled_count_this_step} missing targets.")
            
            if filled_df["temp_focus_score"].notna().all():
                print("All targets successfully filled.")
                break
                
        filled_df["focus_score"] = filled_df["temp_focus_score"]
        filled_df.drop(columns=["temp_focus_score"], inplace=True)
        
        final_kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        filled_df["cluster"] = final_kmeans.fit_predict(x_scaled)
        
        for cluster_id in range(n_clusters):
            cluster_mask = filled_df["cluster"] == cluster_id
            cluster_df = filled_df[cluster_mask]
            
            original_labeled = df[cluster_mask].dropna(subset=["focus_score"])
            n_total = len(cluster_df)
            n_labeled = len(original_labeled)
            n_missing = n_total - n_labeled
            
            filled_subset = filled_df[cluster_mask]
            still_missing = filled_subset["focus_score"].isna().sum()
            
            if still_missing < n_missing:
                status = "Filled"
                filled_vals = filled_subset.loc[df[cluster_mask]["focus_score"].isna(), "focus_score"].value_counts()
                fill_desc = f"Filled {n_missing - still_missing} via hierarchy: {filled_vals.to_dict()}"
            else:
                status = "Unfillable (Lack of Data)"
                fill_desc = None
                unfillable_clusters.append(cluster_id)
                
            cluster_reports[f"Cluster {cluster_id}"] = {
                "total_sessions": n_total,
                "labeled_sessions": n_labeled,
                "missing_sessions": n_missing,
                "mean_target": float(original_labeled["focus_score"].mean()) if n_labeled > 0 else None,
                "fill_value_assigned": fill_desc,
                "status": status
            }

    # 5.5 Apply post-propagation rule-based overrides for bad comfort conditions
    if enable_overrides:
        print("\nApplying post-propagation rule-based overrides for poor environmental conditions...")
        
        # Rule 1: Very Poor conditions (Rating = 1.0)
        rule_1 = (
            (filled_df["temperature_mean"] >= 29.0) |
            (filled_df["co2_mean"] >= 2000.0) |
            (filled_df["noise_mean"] >= 65.0)
        )
        
        # Rule 2: Poor conditions (Rating = 2.0)
        rule_2 = (
            ((filled_df["temperature_mean"] >= 27.5) & (filled_df["temperature_mean"] < 29.0)) |
            ((filled_df["co2_mean"] >= 1300.0) & (filled_df["co2_mean"] < 2000.0)) |
            ((filled_df["noise_mean"] >= 60.0) & (filled_df["noise_mean"] < 65.0))
        )
        
        # Only override ratings of rows that were originally unlabeled
        original_unlabeled_mask = df["focus_score"].isna()
        
        # Apply rule_2 first, then rule_1 to make sure rule_1 takes precedence
        filled_df.loc[original_unlabeled_mask & rule_2, "focus_score"] = 2.0
        filled_df.loc[original_unlabeled_mask & rule_1, "focus_score"] = 1.0
        
        n_rule_1 = (original_unlabeled_mask & rule_1).sum()
        n_rule_2 = (original_unlabeled_mask & rule_2).sum()
        print(f"  Overrode {n_rule_1} unlabeled segments to 1.0 due to severe discomfort conditions.")
        print(f"  Overrode {n_rule_2} unlabeled segments to 2.0 due to moderate discomfort conditions.")

    if unfillable_clusters:
        print(f"\n[WARNING] Could not fill targets for clusters: {unfillable_clusters} due to lack of labeled data!")
    else:
        print("\n[SUCCESS] All clusters successfully filled with targets.")

    # 6. Map columns for model compatibility:
    filled_df["currentTemperature"] = filled_df["temperature_latest"]
    filled_df["maxTemp"] = filled_df["temperature_max"]
    filled_df["minTemp"] = filled_df["temperature_min"]
    filled_df["meanTemp"] = filled_df["temperature_mean"]
    filled_df["rating"] = filled_df["focus_score"]

    # 7. Generate visualizations
    notebook_dir = MAL_DIR / "notebooks" / "data_related"
    generate_visualizations(
        df=filled_df,
        x_scaled=x_scaled,
        cluster_labels=filled_df["cluster"].values,
        n_clusters=n_clusters,
        output_dir=notebook_dir,
    )

    return filled_df, {
        "cluster_reports": cluster_reports,
        "unfillable_clusters": unfillable_clusters
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill missing session targets using KMeans-based label propagation."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--clusters", type=int, default=DEFAULT_N_CLUSTERS)
    parser.add_argument("--seed", type=int, default=RANDOM_STATE)
    parser.add_argument("--strategy", type=str, default="mean", choices=["mean", "sample", "hierarchical"])
    parser.add_argument("--disable-overrides", action="store_true", help="Disable post-propagation rule-based overrides for bad conditions.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Reading linearized sessions from: {args.input}")
    df = pd.read_csv(args.input, low_memory=False)

    filled_df, info = fill_missing_targets_via_clustering(
        df,
        n_clusters=args.clusters,
        random_state=args.seed,
        strategy=args.strategy,
        enable_overrides=not args.disable_overrides,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    filled_df.to_csv(args.output, index=False)
    print(f"\nSaved final holy grail dataset to: {args.output}")

    # Print cluster report
    print("\nCluster Aggregation Report:")
    for cluster_name, report in info["cluster_reports"].items():
        print(f"\n{cluster_name}:")
        print(f"  Total Sessions:     {report['total_sessions']}")
        print(f"  Labeled Sessions:   {report['labeled_sessions']}")
        print(f"  Missing Sessions:   {report['missing_sessions']}")
        if report['status'] == "Filled":
            if report['mean_target'] is not None:
                print(f"  Mean Target Val:    {report['mean_target']:.2f}")
            print(f"  Assigned Target:    {report['fill_value_assigned']}")
        else:
            print("  Status:             UNFILLABLE (No labeled sessions in this cluster)")


if __name__ == "__main__":
    main()
