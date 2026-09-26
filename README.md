# ComDAS

![Python versions tested](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)

ComDAS (Compressed DAS) is a companion package to [DASCore](https://github.com/DASDAE/dascore) that adds support for compressed DAS data. 
Save patches as COMDAS HDF5 files and open them with DASCore's usual `dc.spool()` interface. 

## Supported codecs

- **SVD**: lossy truncated singular value decomposition. Choose a fixed rank with `SVDCodec(rank=XX)` or a retained-energy fraction with `SVDCodec(energy=0.XX)`. Lower ranks generally produce smaller files with more compression error.

> [!NOTE]
> ComDAS is in active development. The file format and public API may change between releases.

## Installation

```bash
git clone https://github.com/Byron-Selvage/ComDAS.git
cd ComDAS
pip install -e .
```

## Write compressed files

The function `write_compressed` accepts a DASCore-readable file or directory, a patch, or a spool. It writes a COMDAS HDF5 file. Attempting to write to an existing COMDAS file appends patches.

```python
import dascore as dc
from comdas import SVDCodec, write_compressed

write_compressed("raw.h5", "compressed.h5", SVDCodec(rank=20))

# A patch or spool can be written the same way.
patch = dc.get_example_patch()
write_compressed(patch, "example.h5", SVDCodec(energy=0.99))
```

## Read compressed files

DASCore recognizes COMDAS files after ComDAS is installed. Read patches, inspect metadata, and select by coordinate range using the usual DASCore APIs. No codec needs to be supplied when reading.

```python
import dascore as dc

spool = dc.spool("compressed.h5")
patches = list(spool)
metadata = dc.scan("compressed.h5")

# Select a time range from a file-backed spool.
selected = spool.select(time=(start_time, end_time))
```

## Documentation

Documentation is available at [byron-selvage.github.io/ComDAS](https://byron-selvage.github.io/ComDAS/).

## License
ComDAS is licensed under the [GNU Lesser General Public License](LICENSE).
