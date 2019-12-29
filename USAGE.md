# Running the AT Pipeline


## Start / Stop atbackend

The `atbackend` command is used to start/stop the backend Docker containers.

### Start the backend
The backend must be started before any data can be processed or viewed:
```bash
atbackend --startall
```

### Check the status of the backend
```bash
atbackend --status
```

### Stop the backend
```bash
atbackend --killall
```

## Process data (atcore)

The `atcore` command is used to process data.

To test if a data folder can be read, run `atcli` with the `--datasummary` flag:

```bash
atcore --data /atp-testdata/input/M33Quarter --datasummary
```

To run the stitching pipeline:

```bash
atcore --data /atp-testdata/input/M33Quarter --pipeline stitch
```

### Pipeline options

The `--pipeline PIPELINE` flag is used to specify one of the following pipelines:
* `stitch`
  * Stitch tiles on individual layers into complete montages.
  * Will run flatfield correction.
  * Stitched stacks are called `S1_Stitched_Dropped`, `S2_Stitched_Dropped`, etc.
* `register`
  * Register multiple sessions of stitched data to each other.
  * Calls `stitch` first.
  * The merged stack (with all channels from all sessions) is called `S1_Stitched_Dropped_Registered_Merged`.
* `roughalign`
  * Perform a rough (rigid) alignment of stitched layers.
  * Calls `stitch` first.
  * Rough aligned stacks are called `S1_RoughAligned`, `S2_RoughAligned`, etc.
* `roughalignregister`
  * Perform registration between sessions on the roughly aligned data.
  * Calls `roughalign` first.
  * The merge stack (with all channels from all sessions) is called `S1_RoughAligned_Registered_Merged`.
* `finealign`
  * Performs a fine alignment (per-tile affine).
  * Calls `roughalign` first.
  * Fine aligned stacks are called `S1_FineAligned`, `S2_FineAligned`, etc.
* `finealignregister`
  * Perform registration between fine-aligned stacks.
  * Calls `finealign` first.
  * The merge stack (with all channels from all sessions) is called `S1_FineAligned_Registered_Merged`.
* `singletile`
  * Mode for alignment of a dataset with 1 tile per layer. Skips stitching step.

### Running on a subsection of data

`atcore` has flags to limit the range of sessions (`--sessions`), ribbons (`--ribbons`) and sections (`--firstsection`, `--lastsection`) being processed. This is useful for trying on a small subset of the data first.

```bash
atcore --data /atp-testdata/input/M33Quarter --pipeline stitch --ribbons Ribbon0004 --sessions session01,session02 --firstsection 0 --lastsection 10
```




### Logging

To get more verbose logs, add `--logging DEBUG`.

Logs will be saved as a text file in `${DATA_PATH}/processed/${DATA_NAME}.log`.

### Other flags



### Note about the 'processed/' directory

The processed directory (`$DATA/processed`) contains all intermediate work products of the pipeline.
The easiest way to re-run the entire pipeline is to delete this directory.

## Access data

## Other utilities

### Delete render stacks

### Rename channels

The `atutil` command can be used to rename a channel in previously acquired data. It will rename all of the image files and related metadata files under the given path. Add the `--dryrun` command to see what will be changed without modifying the data.

Rename all references to `DAPI` as `DAPI_1`:
```bash
atutil rename --data /path/to/data/acquire/raw/data/Ribbon000?/session01/ DAPI DAPI_1
```
