from setuptools import setup, find_packages

setup(
    name="SlurmUtils",
    version="1.0",
    author="Core Dumped",
    author_email="DeliCoredumped@outlook.com",
    description=
    "Python Module Used to Bridge Slurm API",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    package_data={
    },
    python_requires=">=3",
)
