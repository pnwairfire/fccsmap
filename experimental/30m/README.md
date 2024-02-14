## TODOs
 - total fuel loading a) of included fuelbeds, b) of truncated
 - operationalize:  run batches and combine into single, usable fuelbed file, add eflookup class/module to lookup by fire grid cell (with fuelbed file specified as config setting, not bundled in eflookup package)


 - read up on rasterio.features.shapes, esp. kwargs `mask=None` and  `transform=tiff.transform`

### Done
 - [**DONE**] compute and show how much of cell is burnable (percentage)
 - [**DONE**] show 'truncated' section percentages as percentage of burnable (truncated+ + fuelbeds)
 - [**DONE**] make popup a table with columns:  fccsId, percentage of total, percentage of category, percentage of burnable
 - [**DONE**] make firegrid resolution a script arg
