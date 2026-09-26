Installation
============

ComDAS requires Python 3.10 or newer. Installing it also installs `DASCore <https://dascore.org/>`_, NumPy, h5py, and PyWavelets.

From PyPI
---------

.. code-block:: bash

   pip install comdas

From source
-----------

.. code-block:: bash

   git clone https://github.com/Byron-Selvage/ComDAS.git
   cd ComDAS
   pip install -e .

To also install the tools used for tests and documentation:

.. code-block:: bash

   pip install -e ".[dev]"

Check the installation
----------------------

Installing ComDAS registers the ``COMDAS`` file format with DASCore. To validate your installation, you can confirm DASCore sees it:

.. code-block:: python

   import dascore as dc
   from dascore.io.core import FiberIO

   print("COMDAS" in FiberIO.manager.known_formats)
