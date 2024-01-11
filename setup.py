from setuptools import setup, find_namespace_packages

setup(
    name='auto-illumina-run-qc-check',
    version='0.1.0-alpha',
    packages=find_namespace_packages(),
    entry_points={
        "console_scripts": [
            "auto-illumina-run-qc-check = auto_illumina_run_qc_check.__main__:main",
        ]
    },
    scripts=[],
    package_data={
    },
    python_requires='>=3.5,<3.11',
    install_requires=[
    ],
    description='Automated checking of run-level QC metrics for illumina sequencing runs.',
    url='https://github.com/BCCDC-PHL/auto-illumina-run-qc-check',
    author='Dan Fornika',
    author_email='dan.fornika@bccdc.ca',
    include_package_data=True,
    keywords=[],
    zip_safe=False
)
