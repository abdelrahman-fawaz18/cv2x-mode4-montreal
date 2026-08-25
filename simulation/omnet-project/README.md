# OMNeT++ / SUMO project

This directory contains the simulation configuration and three Montreal SUMO scenario bundles used by the project.

## Main files

- `omnetpp.ini`: OMNeT++ experiment settings and the active SUMO launch reference.
- `Highway.ned`: Mode 4 network definition.
- `config_channel.xml`: channel-model and fading parameters.
- `sidelink_configuration.xml`: C-V2X Mode 4 resource-selection parameters.
- `highway/`: SUMO networks, mobility inputs, routes, polygons, and launch files.

## Scenario directories

- `0066vpm`: selected by `omnetpp.ini`.
- `006vpm`: referenced by the Map1 raw-data export.
- `2006vpm`: referenced by the Map2 raw-data export.

The folder names come from the simulation workspace. Their internal references rely on the existing directory names.

## Local setup

Install compatible releases of OMNeT++, SUMO, Veins, INET, and SimuLTE/OpenCV2X. Update the absolute `basedir` value in each `.launchd.xml` file to match the local Veins workspace, then build the OMNeT++ project through the standard framework toolchain.

Review [the configuration reference](../../docs/methodology/CONFIGURATION.md) before starting a new run.
