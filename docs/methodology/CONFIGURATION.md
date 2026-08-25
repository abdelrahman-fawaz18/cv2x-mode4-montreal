# Configuration reference

## Entry points

| File | Purpose |
| --- | --- |
| `simulation/omnet-project/omnetpp.ini` | Main OMNeT++ experiment configuration |
| `simulation/omnet-project/Highway.ned` | Network definition for the Mode 4 simulation |
| `simulation/omnet-project/config_channel.xml` | Propagation and fading parameters |
| `simulation/omnet-project/sidelink_configuration.xml` | Sidelink resource-selection parameters |
| `simulation/omnet-project/highway/0066vpm/mtl.launchd.xml` | SUMO launch selected by `omnetpp.ini` |

## Scenario bundles

| Directory | Project role |
| --- | --- |
| `highway/0066vpm` | Scenario selected by the checked-in `omnetpp.ini` |
| `highway/006vpm` | Launch configuration embedded in `Map1.csv.gz` |
| `highway/2006vpm` | Launch configuration embedded in `Map2.csv.gz` |

Each bundle contains its SUMO network, routes, trips, polygon data, OpenStreetMap extract, launch file, and SUMO configuration.

## Setup notes

- The `.launchd.xml` files contain absolute `/home/veins/...` paths. Update each `basedir` for the local installation.
- `omnetpp.ini` sets `channelControl.carrierFrequency` to 6.0 GHz, while `config_channel.xml` sets the OpenCV2X channel model to 5.91 GHz. Confirm the intended values for the installed framework versions before running a new experiment.
- The checked-in `config_channel.xml` selects NAKAGAMI fading. Switching to JAKES requires the corresponding channel-model setting used by the installed OpenCV2X version.
- Compatible versions of OMNeT++, SUMO, Veins, INET, and SimuLTE/OpenCV2X must be installed separately.
- Generated Makefiles and compiled binaries are excluded from the repository.
