def local(infile, outfile):
    outfile.write(infile.read())
    outfile.close()
    infile.close()

def s3(client, infile, bucket, name):
    client.upload_fileobj(infile, bucket, name)

def gcs(client, infile, bucket, name):
    bucket_name = client.bucket(bucket)
    blob = bucket_name.blob(name)
    blob.upload_from_string(infile.read())
    infile.close()

