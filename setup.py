from setuptools import setup, find_packages  # type: ignore

dev_requires = ["black"]
tests_require = ["pytest", ]
setup(
    name="document_helpers",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="",
    url="http://github.com/paulgessinger/document_helpers",
    author="Paul Gessinger",
    author_email="hello@paulgessinger.com",
    license="MIT",
    install_requires=[
        "click",
        "coloredlogs"
    ],
    tests_require=tests_require,
    extras_require={"dev": dev_requires, "test": tests_require},
    entry_points={"console_scripts": [
      "sync_tags=document_helpers.sync_tags:main",
      "sort_docs=document_helpers.sort:main"
    ]},
    packages=find_packages("src"),
    package_dir={"": "src"},
)
