# Methodology

## System workflow

```text
OpenStreetMap extract
        ↓
SUMO network, routes, trips, and polygons
        ↓
OMNeT++ + Veins + OpenCV2X Mode 4 simulation
        ↓
OMNeT++ scalar and vector results
        ↓ scavetool CSV export
Python metric aggregation and plotting
```

OpenStreetMap data was converted into SUMO road networks for two Montreal environments. Veins connected the SUMO mobility process to the OMNeT++ simulation, while the OpenCV2X/SimuLTE model supplied the C-V2X Mode 4 communication stack.

## Experimental design

The comparison covers:

- a dense city-center grid and a lower-density corridor;
- 5, 10, 15, 20, 25, and 30 communicating vehicles;
- JAKES and NAKAGAMI fading models;
- 24 scenario/fading/vehicle-count combinations;
- one 100-second simulation per combination.

The application, radio-resource settings, transmit power, and simulation duration were held constant across the comparison.

## Main parameters

| Parameter | Value |
| --- | --- |
| Simulation time limit | 100 s |
| Veins manager update interval | 0.1 s |
| Position update interval | 0.01 s |
| Application | `Mode4App` |
| Packet size | 190 bytes |
| Subchannels | 3 |
| Subchannel size | 16 resource blocks |
| Resource-keeping probability | 0.4 |
| Vehicle/D2D transmit power | 23 dBm |
| Channel-model carrier frequency | 5.91 GHz |
| Channel scenario | `ANALYTICAL` |

## Metric definitions

Let `N` be the number of communicating vehicles in a run. For vehicle `i`, let `S_i` be the number of packets transmitted and `R_i` the number received.

Aggregate packet reception rate:

```text
PRR = (Σ R_i) / ((N − 1) × Σ S_i)
```

Each broadcast has `N − 1` potential receivers, which produces the denominator above.

Receiver-side PRR for vehicle `i`:

```text
PRR_rx_i = R_i / (Σ S_j − S_i)
```

The analysis reports the mean, population standard deviation (`ddof=0`), minimum, and maximum of `PRR_rx_i`. Mean CBR is the arithmetic mean of the per-vehicle `cbr:mean` scalar values.

The parser selects `sentMsg:sum` and `rcvdMsg:sum` records from modules ending in `.appl`, and `cbr:mean` from scalar records. Scenario, fading model, and vehicle count are parsed from each input filename.

## Analysis outputs

`analysis/extended_metrics_batch_plot.py` creates:

- per-file metrics;
- grouped metrics by scenario, fading model, and vehicle count;
- a compact results table;
- combined PRR and mean-CBR plots.

Each execution writes to a new timestamped output directory.
