# Analysis

`extended_metrics_batch_plot.py` processes OMNeT++ `scavetool` CSV exports and produces the project’s PRR and CBR summaries.

## Input format

Each CSV file must contain these columns:

- `type`
- `module`
- `name`
- `value`

Filenames must end with the fading model and vehicle count:

```text
city_center_Nakagami_05.csv
city_center_JAKES_30.csv
lower_density_Nakagami_20.csv
```

The aliases `city`, `urban`, and `downtown` are displayed as **City center**. The aliases `rural`, `suburb`, `highway`, `low_density`, and `lower_density` are displayed as **Lower-density**.

## Metrics

The script calculates:

- aggregate packet reception rate (PRR);
- receiver-side PRR mean, population standard deviation, minimum, and maximum;
- mean channel busy ratio (CBR);
- grouped summaries by scenario, fading model, and vehicle count.

## Usage

```powershell
python -m pip install -r requirements.txt
python extended_metrics_batch_plot.py `
  --input-dir INPUT_DIRECTORY `
  --pattern "*.csv" `
  --output-dir metrics_outputs
```

The output directory contains:

- `all_metrics_by_file.csv`
- `summary_metrics_by_scenario_fading_and_num_vehicles.csv`
- `paper_table_main_metrics.csv`
- `prr_vs_num_vehicles_combined.png`
- `mean_cbr_vs_num_vehicles_combined.png`

Outputs are placed in a timestamped subdirectory so previous analysis runs remain available.
