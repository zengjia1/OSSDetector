# TPLDetector
This repository is for the OSSDetector tool, which is used to detect third-party libraries (TPL) in C/C++ projects.

## Contents
- [CVE](#cve)
- [Sample](#sample)
- [Detector](#detector)
- [Database](#database)

## CVE
The **CVE** folder contains relevant information about vulnerabilities in C/C++ code.

## Sample
The **Sample** folder contains four examples, which can be used as target software to detect the third-party libraries (TPLs) they use.

## Detector
The **Detector** folder contains the code used in the detection phase. It consists of the following components:
- **detector-TPL**: Used to detect the third-party libraries (TPLs) used by the target software.
- **detector-1day**: Used to detect whether the TPLs are vulnerable (i.e., if they have known vulnerabilities).
- **detector-time**: Used to detect whether the TPLs used in the target software are outdated.

These components are designed to perform various checks and analyses on the TPLs within the target software.

## Database
The **Database** folder contains a processed database of C/C++ third-party libraries (TPLs). This database likely includes information and metadata about various TPLs, making it a resource for referencing and managing these libraries in the context of C/C++ software development.
