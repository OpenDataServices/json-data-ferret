from setuptools import find_packages, setup

setup(
    name="jsondataferret",
    version="0.7.0",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    packages=[p for p in find_packages() if p.startswith("jsondataferret")],
    package_data={
        "jsondataferret": [
            "templates/*",
            "templates/*/*",
            "templates/*/*/*",
            "templates/*/*/*/*",
            "templates/*/*/*/*/*",
        ]
    },
    url="https://github.com/OpenDataServices/json-data-ferret",
    license="MIT",
    description="Django App for managing JSON Data",
    install_requires=[
        "Django>=3.2",
        "django-filter",
        "jsonmerge",
        "spreadsheetforms",
        "Pygments",
        "jsonschema",
        "psycopg2",
        "json-merge-patch",
    ],
    extras_require={
        "dev": ["pip-tools", "black==22.3", "flake8", "isort", "django-environ"]
    },
    python_requires=">=3.8",
)
