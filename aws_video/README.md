# AWS Video Support

We're adding the ability to deliver videos hosted in AWS instead of YouTube.
This requires some companion files, such as Python scripts used as Lambda functions.

This directory has the versioned-controlled copies that are uploaded.

## Useful Commands

```shell
$ aws --profile guides s3 ls s3://jetvideo-generated/assets
$ aws --profile guides s3 ls s3://jetvideo-source/
$ aws --profile guides s3 rm --recursive s3://jetvideo-generated/assets/pwe/

```