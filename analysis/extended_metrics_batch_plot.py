import argparse
import re
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_scavetool_csv(csv_path: Path) -> pd.DataFrame:
    encodings_to_try = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    for enc in encodings_to_try:
        try:
            return pd.read_csv(csv_path, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue

    return pd.read_csv(
        csv_path,
        encoding="latin1",
        encoding_errors="replace",
        low_memory=False,
    )


def parse_filename_metadata(csv_path: Path) -> dict:
    """
    Expected filename format:
        scenario_fading_numVehicles.csv

    Examples:
        city_center_Nakagami_05.csv
        city_center_JAKES_10.csv
        rural_Nakagami_15.csv

    Also tolerates accidental names like:
        rural_JAKES_30.csv.csv
    """
    name = csv_path.name.strip()

    while name.lower().endswith(".csv"):
        name = name[:-4]

    m = re.fullmatch(r"(.+?)_([A-Za-z]+)_(\d+)", name)
    if not m:
        raise ValueError(
            f"{csv_path.name}: expected filename like "
            f"'scenario_fading_num.csv', e.g. city_center_Nakagami_05.csv"
        )

    scenario_raw, fading_raw, num_str = m.groups()

    scenario_key = scenario_raw.strip().lower()
    fading_key = fading_raw.strip().upper()

    if scenario_key in {
        "suburbs",
        "suburb",
        "suburban",
        "rural",
        "highway",
        "low_density",
        "low-density",
        "lower_density",
        "lower-density",
    }:
        scenario_label = "Lower-density"
    elif scenario_key in {
        "city",
        "urban",
        "downtown",
        "city_center",
        "citycentre",
        "city-center",
        "citycenter",
    }:
        scenario_label = "City center"
    else:
        scenario_label = scenario_raw.replace("_", " ").title()

    if fading_key == "NAKAGAMI":
        fading_label = "NAKAGAMI"
    elif fading_key == "JAKES":
        fading_label = "JAKES"
    else:
        fading_label = fading_key

    return {
        "scenario": scenario_label,
        "fading_model": fading_label,
        "vehicles_from_filename": int(num_str),
    }


def build_output_dir(base_output_dir: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"{base_output_dir}_{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=False)
    return out_dir


def compute_metrics_from_csv(csv_path: Path) -> dict:
    """
    Metrics computed from the CSV:

    1) Global PRR
       PRR = (sum_i R_i) / ((N - 1) * sum_i S_i)

    2) Per-car receiver PRR statistics
       For receiver i:
           PRR_rx_i = R_i / (sum_j S_j - S_i)
       Then report mean/std/min/max across receivers.

    3) Mean CBR
       Arithmetic mean of cbr:mean across vehicles.
    """
    df = load_scavetool_csv(csv_path)

    required_cols = {"type", "module", "name", "value"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path.name}: missing required columns {sorted(missing)}")

    scalars = df[df["type"] == "scalar"].copy()
    appl = scalars[scalars["module"].str.endswith(".appl", na=False)].copy()

    sent_rows = appl[appl["name"] == "sentMsg:sum"].copy()
    rcvd_rows = appl[appl["name"] == "rcvdMsg:sum"].copy()

    if sent_rows.empty:
        raise ValueError(f"{csv_path.name}: no sentMsg:sum rows found")
    if rcvd_rows.empty:
        raise ValueError(f"{csv_path.name}: no rcvdMsg:sum rows found")

    sent_rows["value"] = pd.to_numeric(sent_rows["value"], errors="coerce")
    rcvd_rows["value"] = pd.to_numeric(rcvd_rows["value"], errors="coerce")

    total_sent = sent_rows["value"].sum()
    total_received = rcvd_rows["value"].sum()
    n_vehicles = sent_rows["module"].nunique()

    if n_vehicles <= 1:
        raise ValueError(f"{csv_path.name}: invalid number of vehicles ({n_vehicles})")
    if total_sent <= 0:
        raise ValueError(f"{csv_path.name}: total sent packets is zero")

    global_prr = total_received / ((n_vehicles - 1) * total_sent)

    # Per-car PRR statistics
    per_car_df = pd.merge(
        sent_rows[["module", "value"]].rename(columns={"value": "sent_i"}),
        rcvd_rows[["module", "value"]].rename(columns={"value": "rcvd_i"}),
        on="module",
        how="outer",
    ).fillna(0.0)

    per_car_df["recv_opportunities_i"] = total_sent - per_car_df["sent_i"]

    if (per_car_df["recv_opportunities_i"] <= 0).any():
        raise ValueError(
            f"{csv_path.name}: invalid per-car PRR denominator encountered"
        )

    per_car_df["per_car_prr"] = (
        per_car_df["rcvd_i"] / per_car_df["recv_opportunities_i"]
    )

    per_car_prr_mean = per_car_df["per_car_prr"].mean()
    per_car_prr_std = per_car_df["per_car_prr"].std(ddof=0)
    per_car_prr_min = per_car_df["per_car_prr"].min()
    per_car_prr_max = per_car_df["per_car_prr"].max()

    cbr_rows = scalars[scalars["name"] == "cbr:mean"].copy()
    if cbr_rows.empty:
        raise ValueError(f"{csv_path.name}: no cbr:mean rows found")

    cbr_rows["value"] = pd.to_numeric(cbr_rows["value"], errors="coerce")
    mean_cbr = cbr_rows["value"].mean()

    return {
        "file": csv_path.name,
        "num_vehicles": int(n_vehicles),
        "total_sent": float(total_sent),
        "total_received": float(total_received),
        "prr": float(global_prr),
        "prr_percent": float(100.0 * global_prr),
        "per_car_prr_mean": float(per_car_prr_mean),
        "per_car_prr_std": float(per_car_prr_std),
        "per_car_prr_min": float(per_car_prr_min),
        "per_car_prr_max": float(per_car_prr_max),
        "per_car_prr_mean_percent": float(100.0 * per_car_prr_mean),
        "per_car_prr_std_percent": float(100.0 * per_car_prr_std),
        "per_car_prr_min_percent": float(100.0 * per_car_prr_min),
        "per_car_prr_max_percent": float(100.0 * per_car_prr_max),
        "mean_cbr": float(mean_cbr),
        "mean_cbr_percent": float(100.0 * mean_cbr),
    }


def make_series_label(scenario: str, fading_model: str) -> str:
    return f"{scenario} — {fading_model}"


def plot_metric_by_scenario_and_fading(
    summary_df: pd.DataFrame,
    y_col: str,
    y_label: str,
    title: str,
    output_png: Path,
) -> None:
    plt.figure(figsize=(8.5, 5.8))

    style_map = {
        ("City center", "NAKAGAMI"): {"marker": "o", "linestyle": "-"},
        ("City center", "JAKES"): {"marker": "s", "linestyle": "--"},
        ("Lower-density", "NAKAGAMI"): {"marker": "^", "linestyle": "-"},
        ("Lower-density", "JAKES"): {"marker": "D", "linestyle": "--"},
    }

    series_keys = (
        summary_df[["scenario", "fading_model"]]
        .drop_duplicates()
        .sort_values(["scenario", "fading_model"])
        .itertuples(index=False, name=None)
    )

    for scenario, fading_model in series_keys:
        sub = summary_df[
            (summary_df["scenario"] == scenario)
            & (summary_df["fading_model"] == fading_model)
        ].sort_values("num_vehicles")

        style = style_map.get(
            (scenario, fading_model),
            {"marker": "o", "linestyle": "-"},
        )

        plt.plot(
            sub["num_vehicles"],
            sub[y_col],
            marker=style["marker"],
            linestyle=style["linestyle"],
            linewidth=2.0,
            markersize=6,
            label=make_series_label(scenario, fading_model),
        )

    plt.xlabel("Number of vehicles", fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.title(title, fontsize=13)
    plt.xticks(sorted(summary_df["num_vehicles"].unique()))
    plt.grid(True, linestyle="--", linewidth=0.6, alpha=0.7)
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Batch-compute global PRR, per-car PRR summary statistics, and mean CBR "
            "from OMNeT++/scavetool CSV files for multiple scenarios and fading models."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=".",
        help="Directory containing the CSV files",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.csv",
        help="Glob pattern for CSV files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="metrics_outputs",
        help="Base name for the output directory; timestamp is appended automatically",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    csv_files = sorted(input_dir.glob(args.pattern))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {input_dir.resolve()} with pattern {args.pattern!r}"
        )

    out_dir = build_output_dir(args.output_dir)

    rows = []
    for csv_path in csv_files:
        print(f"Processing: {csv_path.name}")
        metrics = compute_metrics_from_csv(csv_path)
        meta = parse_filename_metadata(csv_path)

        row = {**meta, **metrics}

        if row["vehicles_from_filename"] != row["num_vehicles"]:
            print(
                f"Warning: {csv_path.name} -> filename says {row['vehicles_from_filename']} vehicles "
                f"but CSV content implies {row['num_vehicles']} vehicles. Using CSV content."
            )

        rows.append(row)

    detailed_df = pd.DataFrame(rows).sort_values(
        by=["scenario", "fading_model", "num_vehicles", "file"]
    )

    detailed_csv = out_dir / "all_metrics_by_file.csv"
    detailed_df.to_csv(detailed_csv, index=False)

    summary_df = (
        detailed_df.groupby(["scenario", "fading_model", "num_vehicles"], as_index=False)
        .agg(
            prr=("prr", "mean"),
            prr_percent=("prr_percent", "mean"),
            per_car_prr_mean=("per_car_prr_mean", "mean"),
            per_car_prr_std=("per_car_prr_std", "mean"),
            per_car_prr_min=("per_car_prr_min", "mean"),
            per_car_prr_max=("per_car_prr_max", "mean"),
            per_car_prr_mean_percent=("per_car_prr_mean_percent", "mean"),
            per_car_prr_std_percent=("per_car_prr_std_percent", "mean"),
            per_car_prr_min_percent=("per_car_prr_min_percent", "mean"),
            per_car_prr_max_percent=("per_car_prr_max_percent", "mean"),
            mean_cbr=("mean_cbr", "mean"),
            mean_cbr_percent=("mean_cbr_percent", "mean"),
            total_sent=("total_sent", "mean"),
            total_received=("total_received", "mean"),
            n_files=("file", "count"),
        )
        .sort_values(by=["scenario", "fading_model", "num_vehicles"])
    )

    summary_csv = out_dir / "summary_metrics_by_scenario_fading_and_num_vehicles.csv"
    summary_df.to_csv(summary_csv, index=False)

    paper_table = summary_df[
        [
            "scenario",
            "fading_model",
            "num_vehicles",
            "prr_percent",
            "per_car_prr_mean_percent",
            "per_car_prr_std_percent",
            "per_car_prr_min_percent",
            "per_car_prr_max_percent",
            "mean_cbr_percent",
        ]
    ].copy()
    paper_table.to_csv(out_dir / "paper_table_main_metrics.csv", index=False)

    plot_metric_by_scenario_and_fading(
        summary_df,
        y_col="prr_percent",
        y_label="PRR (%)",
        title="Packet Reception Rate versus Number of Vehicles",
        output_png=out_dir / "prr_vs_num_vehicles_combined.png",
    )

    plot_metric_by_scenario_and_fading(
        summary_df,
        y_col="mean_cbr_percent",
        y_label="Mean CBR (%)",
        title="Mean Channel Busy Ratio versus Number of Vehicles",
        output_png=out_dir / "mean_cbr_vs_num_vehicles_combined.png",
    )

    print("\nDone.")
    print(f"Output folder: {out_dir.resolve()}")
    print(f"Detailed metrics file: {detailed_csv.name}")
    print(f"Summary metrics file: {summary_csv.name}")
    print("Generated:")
    print(" - paper_table_main_metrics.csv")
    print(" - prr_vs_num_vehicles_combined.png")
    print(" - mean_cbr_vs_num_vehicles_combined.png")
    print("\nPer-car PRR outputs included:")
    print(" - per_car_prr_mean_percent")
    print(" - per_car_prr_std_percent")
    print(" - per_car_prr_min_percent")
    print(" - per_car_prr_max_percent")


if __name__ == "__main__":
    main()
