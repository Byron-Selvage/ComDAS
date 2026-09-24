# ComDAS

ComDAS (Compressed DAS) is a companion package to [DASCore](https://github.com/DASDAE/dascore) that adds support for compressed DAS data. ComDAS depends on DASCORE directly and is designed to extend DASCORE behavior.

## Features
- NumPy-compatible arrays backed by compressed payloads
- Lossy truncated-SVD compression for two-dimensional DAS data
- A codec interface for implementing additional compression methods
- Codec-agnostic HDF5 storage integrated with DASCore's I/O system

ComDAS is in active development. The file format and public API may change between releases.

## Installation
```bash
git clone https://github.com/Byron-Selvage/ComDAS.git
cd comdas
pip install -e .
```

## Documentation

Documentation is available at [byron-selvage.github.io/ComDAS](https://byron-selvage.github.io/ComDAS/).

## License 
ComDAS is licensed under the [GNU Lesser General Public License](LICENSE).
