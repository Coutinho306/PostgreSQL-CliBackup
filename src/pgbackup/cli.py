from argparse import Action, ArgumentParser
from fileinput import filename

class DriverAction(Action):
    def __call__(self, parser, namespace, values, option_string):
        driver, destination = values
        namespace.driver = driver.lower()
        namespace.destination = destination

def create_parser():
    parser = ArgumentParser(description="""
    Back up PostgreSQL databases locally or to Cloud Storages(S3 or GCS)
    """)

    parser.add_argument("url", help="URL of the database to backup")
    parser.add_argument("--driver", '-d',
                        help="how & where to store the backup",
                        nargs=2,
                        metavar=('DRIVER', 'DESTINATION'),
                        action=DriverAction,
                        required=True)

    return parser

def main():
    import boto3
    from google.cloud import storage as gs
    import time
    from pgbackup import pgdump, storage
    
    args = create_parser().parse_args()
    dump = pgdump.dump(args.url)
    if args.driver == 's3':
        client = boto3.client('s3')
        timestamp = time.strftime("%Y-%m-%dT%H-%M", time.localtime())
        file_name = pgdump.dump_file_name(args.url, timestamp)
        print(f'Backing database up to {args.destination} in S3 as {file_name}')
        storage.s3(client, dump.stdout, args.destination, file_name)
    elif args.driver == 'gcs':
        client = gs.Client()
        timestamp = time.strftime("%Y-%m-%dT%H-%M", time.localtime())
        file_name = pgdump.dump_file_name(args.url, timestamp)
        print(f'Backing database up to {args.destination} in GCS as {file_name}')
        storage.gcs(client, dump.stdout, args.destination, file_name)
    else:
        outfile = open(args.destination, 'wb')
        print(f'Backing database up to locally as {outfile}')
        storage.local(dump.stdout, outfile)