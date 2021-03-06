# -*- coding: utf-8 -*-

# Define self package variable
__version__ = '1.1a1'
__all__ = ["pycoQC", "pycoQC_fun"]
__description__="""
PycoQC is a Python 3 package for Jupyter Notebook, computing metrics and generating simple QC plots
from the sequencing summary report generated by Oxford Nanopore technologies Albacore basecaller
"""
__long_description__="""
pycoQC is a very simple quality control package for Nanopore data written in pure **python3**, meant
to be used directly in a **jupyter notebook** 4.0.0 +. As opposed to more exhaustive QC programs for nanopore
data, pycoQC is very fast as it relies entirely on the *sequencing_summary.txt* file generated by ONT Albacore
Sequencing Pipeline Software 1.2.1+, during base calling. Consequently, pycoQC will only provide metrics at read level
metrics (and not at base level). The package supports 1D and 1D2 runs analysed with Albacore.

PycoQC requires the following fields in the sequencing.summary.txt file:

* 1D run => **read_id**, **run_id**, **channel**, **start_time**, **sequence_length_template**, **mean_qscore_template**
* 1D2 run =>**read_id**, **run_id**, **channel**, **start_time**, **sequence_length_2d**, **mean_qscore_2d**

In addition it will try to get the following optional fields if they are available:

* **num_events**, **calibration_strand_genome_template**, **passes_filtering** """

# Collect info in a dictionnary for setup.py
setup_dict = {
    "name": __name__,
    "version": __version__,
    "description": __description__,
    "long_description": __long_description__,
    "url": "https://github.com/a-slide/pycoQC",
    "author": 'Adrien Leger',
    "author_email": 'aleg@ebi.ac.uk',
    "license": 'GPLv3',
    "python_requires":'>=3.3',
    "classifiers": [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',],
    "install_requires": ['numpy>=1.13.0', 'pandas>=0.20.0', 'matplotlib>=2.0.0', 'seaborn>= 0.7.0', 'notebook>=4.0.0'],
    "packages": [__name__],
    "package_dir": {__name__: __name__},
    "package_data": {__name__: ['data/*.txt']},
    }
