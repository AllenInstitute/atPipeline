# Running the AT Pipeline


## Start / Stop atbackend
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

## Process data



## Rename channels

The `atutil` command can be used to rename a channel in previously acquired data. It will rename all of the image files and related metadata files. Add the `--dryrun` command to see what will be changed without modifying the data.

```bash
atutil rename --data /path/to/data/acquire DAPI DAPI_1
```