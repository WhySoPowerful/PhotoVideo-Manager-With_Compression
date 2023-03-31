from google.cloud import storage
from flask import current_app


def setup_client():
    current_app.config["GOOGLE_CLOUD_CLIENT"] = storage.Client()


def setup_bucket(bucket_name: str, bucket_location: str="US"):
    client = current_app.config["GOOGLE_CLOUD_CLIENT"]

    for bucket in client.list_buckets():
        if bucket.name == bucket_name:
            break
    else:
        bucket = client.create_bucket(
            client.bucket(bucket_name), bucket_location
        )

    current_app.config["GOOGLE_CLOUD_BUCKET"] = bucket
    return bucket


def upload_file(destination, contents):
    bucket = current_app.config["GOOGLE_CLOUD_BUCKET"]
    blob = bucket.blob(destination)
    blob.upload_from_string(contents)
    return blob


def get_files():
    bucket = current_app.config["GOOGLE_CLOUD_BUCKET"]
    return bucket.list_blobs()


def get_file(name):
    bucket = current_app.config["GOOGLE_CLOUD_BUCKET"]
    return bucket.get_blob(name)


def save_file(blob, file):
    blob.download_to_file(file)


def rename_file(dest_file, src_file):
    bucket = current_app.config["GOOGLE_CLOUD_BUCKET"]

    print("Src:", src_file, "\tDest:", dest_file)
    blob_copy = bucket.copy_blob(
        bucket.blob(src_file), bucket, dest_file
    )
    bucket.delete_blob(src_file)

    return get_file(dest_file)


def delete_file(file_name):
    bucket = current_app.config["GOOGLE_CLOUD_BUCKET"]
    blob = bucket.blob(file_name)
    blob.delete()

