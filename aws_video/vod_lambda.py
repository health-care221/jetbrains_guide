"""Python lambda function to trigger Media Convert."""

import json
import os
import time
from dataclasses import dataclass
from pathlib import PurePath

import boto3


def pathlib_parents(path: PurePath) -> str:
    """Convert a nested path (minus the extension) to a key for CDN."""
    if path.root == "/":
        # Remove the root to avoid a part for /
        parts = list(path.parts)[1:]
    else:
        parts = list(path.parts)
    parts[-1] = path.stem
    return "/".join(parts)


def get_s3_source_key_path(event):
    this_s3 = event["Records"][0]["s3"]
    this_bucket_name = this_s3["bucket"]["name"]
    this_bucket_key = this_s3["object"]["key"]
    this_bucket_path = PurePath(f"s3://{this_bucket_name}/{this_bucket_key}")
    print(
        f"#### Name: {this_bucket_name} .. Key: {this_bucket_key} ... Path: {this_bucket_key}"
    )
    return this_bucket_key, this_bucket_path


@dataclass
class VideoRecord:
    # Comes from event["Records"][0]["s3"]["bucket"]["name"]
    bucket_name: str
    # Comes from event["Records"][0]["s3"]["object"]["key"]
    object_key: str


# noinspection PyUnusedLocal
def lambda_handler(event, context):
    # #### Name: jetvideo-source Key: pwe/failed_tests.mp4
    s3_key, s3_source_path = get_s3_source_key_path(event)
    s3_source_basename = s3_source_path.stem
    joined_parents = pathlib_parents(PurePath(s3_key))
    print(f"####### Uploading: {s3_key} Joined Parents: {joined_parents}")

    region = os.environ["AWS_DEFAULT_REGION"]
    status_code = 200
    body = {}
    if not s3_key.endswith(".mp4"):
        raise ValueError(f"Tried to upload a file {s3_key} not ending in .mp4")

    # Use MediaConvert SDK UserMetadata to tag jobs with the assetID
    # Events from MediaConvert will have the assetID in UserMedata
    job_metadata = {"assetID": s3_source_basename}
    try:
        # Job settings are in the lambda zip file in the current working directory
        with open("job.json") as json_data:
            job_settings = json.load(json_data)

        # get the account-specific mediaconvert endpoint for this region
        mc_client = boto3.client("mediaconvert", region_name=region)
        endpoints = mc_client.describe_endpoints()

        # Update the job settings with the source video from the S3 event and destination
        # paths for converted videos
        job_settings["Inputs"][0]["FileInput"] = "s3://" + str(s3_source_path)[4:]
        # job_settings["Inputs"][0]["FileInput"] = (
        #     "s3://" + "jetvideo-source" + "/" + s3_key
        # )
        print(f"Job metadata", job_settings["Inputs"][0]["FileInput"])

        destination_s3 = "s3://" + os.environ["DestinationBucket"]
        og = job_settings["OutputGroups"]

        # Clean up the CDN caching
        print(f"####### CDN update")
        cdn_path = f"/assets/{joined_parents}/HLS/*"
        print(f"##### cdn_path {cdn_path}")
        cdn_client = boto3.client("cloudfront")
        cdn_client.create_invalidation(
            DistributionId="E1166YMX8A3BF5",
            InvalidationBatch={
                "Paths": {"Quantity": 1, "Items": [cdn_path]},
                "CallerReference": str(time.time()),
            },
        )

        # HLS
        hd = destination_s3 + f"/assets/{joined_parents}/HLS/{s3_source_basename}"
        print(f"####### HLS Setup")
        print(f"##### hd: {hd}")
        og[0]["OutputGroupSettings"]["HlsGroupSettings"]["Destination"] = hd

        # Thumbnails
        print(f"####### Thumbnails Setup")
        td = (
            destination_s3 + f"/assets/{joined_parents}/Thumbnails/{s3_source_basename}"
        )
        print(f"##### td: {td}")
        og[1]["OutputGroupSettings"]["FileGroupSettings"]["Destination"] = td

        # Convert the video using AWS Elemental MediaConvert
        print(f"####### Send to MediaConvert")
        media_convert_role = os.environ["MediaConvertRole"]
        client = boto3.client(
            "mediaconvert",
            region_name=region,
            endpoint_url=endpoints["Endpoints"][0]["Url"],
            verify=False,
        )
        print(
            "##### MC settings",
            s3_source_basename,
            job_metadata,
        )
        client.create_job(
            Role=media_convert_role, UserMetadata=job_metadata, Settings=job_settings
        )
        print(f"####### Finished uploading video")

    except Exception as e:
        print("Exception: %s" % e)
        status_code = 500
        raise

    finally:
        return {
            "statusCode": status_code,
            "body": json.dumps(body),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
