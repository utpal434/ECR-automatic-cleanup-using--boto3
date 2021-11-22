import boto3
import time

client = boto3.client('ecr')

images_to_keep = 1


def intialize():

    # fetching repositories
    repositories = client.describe_repositories()

    repository_name_list = []
    for repos in repositories['repositories']:
        repository_name_list.append(repos['repositoryName'])

    # listing the images
    for name in repository_name_list:
        print("list of images in "+name+" respository")
        for image in client.list_images(repositoryName=name)['imageIds']:
            print(image)
        print("\n")

    for name in repository_name_list:
        images = client.describe_images(repositoryName=name)
        image_details = []
        for image in images['imageDetails']:
            image_details.append(image)

        if(len(images['imageDetails']) > images_to_keep):
            sorted_images = sort_images_by_timestamp(image_details, name)
            delete_images(sorted_images, name)

        else:
            print("good to go")


def delete_images(sorted_images, name):
    imageId_list = []

    n = len(sorted_images)

    for i in range(0, n-images_to_keep):

        imageId_list.append(
            {
                'imageDigest': sorted_images[i]['imageDigest'],
                'imageTag': sorted_images[i]['imageTags'][0]
            }
        )

    print("images before deletion in repository in " + name+": ", len(
        client.describe_images(repositoryName=name)['imageDetails']))
    print("\n")

    # deleting images
    response = client.batch_delete_image(
        repositoryName=name,
        imageIds=imageId_list
    )

    time.sleep(15)

    print_details(response, name)


def sort_images_by_timestamp(image_details, name):
    sorted_images = sorted(image_details, key=lambda k: k['imagePushedAt'])

    # printing filtered images by time
    print("printing sorted images in repository"+name)
    for image in sorted_images:
        print(image['imagePushedAt'])
    print("\n")

    return sorted_images


def print_details(response, name):
    print("number of deleted images in repository " +
          name, len(response['imageIds']))
    # for rs in response['imageIds']:
    #     print(rs['imageDigest'])
    print("images after deletion in repository "+name, len(
        client.describe_images(repositoryName=name)['imageDetails']))


if __name__ == "__main__":
    intialize()
