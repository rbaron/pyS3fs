from setuptools import setup, find_packages

setup(
      name="pyS3fs",
      description="Mount Amazon's S3 bucket as a filesystem",
      version="0.1",
      url="http://github.com/rbaron/pyS3fs",
      install_requires=["fusepy", "boto"],
      packages=find_packages(),
      scripts=["scripts/pyS3fs"]
     )
