# TPLDetector
This is the repository for the tool OSSDetector, which is used to detect third-party libraries (TPL) in C/C++ projects.

#cve
The folder "CVE" contains relevant information about vulnerabilities in C/C++ code.

#sample
The "sample" folder contains four examples, and you can use them as target software to detect the third-party libraries (TPLs) they use.

#detector
The "detector" folder contains the code used in the detection phase. Specifically, it includes:

- "detector-TPL": Used to detect the third-party libraries (TPLs) used by the target software.
- "detector-1day": Used to detect whether the TPLs are vulnerable (i.e., if they have known vulnerabilities).
- "detector-time": Used to detect whether the TPLs used in the target software are outdated.

These components are designed to perform various checks and analyses on the TPLs within the target software.

#database
The "database" folder contains a processed database of C/C++ third-party libraries (TPLs). This database likely includes information and metadata about various TPLs, making it a resource for referencing and managing these libraries in the context of C/C++ software development.
