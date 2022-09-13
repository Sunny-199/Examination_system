import boto3
from botocore.exceptions import NoCredentialsError


# ACCESS_KEY = os.environ.get('ACCESS_KEY')
# SECRET_KEY = os.environ.get('SECRET_KEY')
# bucket_name = os.environ.get('bucket_name')
ACCESS_KEY = "AKIAQUSEYW7ZJKXATXP3"
bucket_name = "exam-answer-bucket"
SECRET_KEY = "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"
# image_file = "/Users/zestgeek26/PycharmProjects/testingProject/Dark-Minimalist.jpeg"
# user_id = 6
# answer_sheet = 5
# question_id = 1
# page_number = 1

# def create_bucket(ACCESS_KEY, SECRET_KEY):
#     s3 = boto3.client('s3',
#                       aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)
#     s3.create_bucket(Bucket='exam-answer-bucket')
#
#
# # print(create_bucket(ACCESS_KEY, SECRET_KEY))
#
#
# def get_bucket_list(ACCESS_KEY, SECRET_KEY):
#     import boto3
#
#     # Create an S3 client
#     s3 = boto3.client('s3',
#                       aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)
#     # Call S3 to list current buckets
#     response = s3.list_buckets()
#     # Get a list of all bucket names from the response
#     buckets = [bucket['Name'] for bucket in response['Buckets']]
#     # Print out the region name
#     region_name = s3.meta.region_name
#     print("region_name", region_name)
#     return buckets, region_name
#
#
# print(get_bucket_list(ACCESS_KEY, SECRET_KEY))


def get_file_name(local_file, user_id, topic_id, question_id, page_number):
    ext = local_file.split("/")[-1].split(".")[-1]
    name = f"{user_id}/{topic_id}/{question_id}-{page_number}.{ext}"
    return name


def upload_to_aws(local_file, user_id, topic_id, question_id, page_number):
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    try:
        file_name = get_file_name(local_file, user_id, topic_id, question_id, page_number)
        print(local_file, file_name, bucket_name, '************************8')
        s3.upload_file(local_file, bucket_name, file_name)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_name
            }
        )
        print("Upload Successful", url)
        url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        print(url)
        return True, url
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
# uploaded = upload_to_aws(image_file, bucket_name)