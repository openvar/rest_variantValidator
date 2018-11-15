from distutils.core import setup

setup(
    # Application name:
    name="variantValidator",

    # Version number (initial):
    version="v0.1a",

    # Application author details:
    author="Peter Fausey-Freeman",
    author_email="variantvalidator@gmail.com",

    # Packages
    packages=['variantvalidator', 'variantvalidator.variantanalyser', 'variantvalidator.spam_filter'],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://PeteCauseyFreeman@bitbucket.org/PeteCauseyFreeman/variantvalidator",

    license="LICENSE.txt",
    
    description="Accurate validation, mapping and formatting of sequence variants using HGVS nomenclature",

    # Long description
    long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "biopython==1.66",
		"biotools==1.2.12",
		"bioutils==0.0.9",
		"blinker==1.4",
		"configparser==3.3.0.post2",
		"Flask==0.10.1",
		"Flask-Mail==0.9.1",
		"Flask-WTF==0.12",
		"hgvs==0.4.4",
		"httplib2==0.9.2",
		"itsdangerous==0.24",
		"Jinja2==2.8",
		"MarkupSafe==0.23",
		"Parsley==1.3",
		"psycopg2==2.6.1",
		"recordtype==1.1",
		"requests==2.9.0",
		"Reverend==0.4",
		"Werkzeug==0.11.2",
		"wheel==0.24.0",
		"WTForms==2.1",
    ],
)
