#!/usr/bin/python3

import requests

UPLOAD_URL = "http://localhost:4000/upload"

def download_image(url):
    print("downloading", url, "...")
    return requests.get(url).content


def read_image_data(path):
    with open(str(path), 'rb') as image_blob:
        return image_blob.read()


def read_images(csv):
    from pathlib import Path

    path = Path(__file__).parent / csv

    images = []

    with open(str(path), 'r') as fin:
        for line in fin.readlines():
            parts = line.strip().split(';')

            image = {}

            image["name"] = Path(parts[0]).name
            image["description"] = parts[1]
            image["taken_date"] = parts[2]
            image["tags"] = parts[3]

            if parts[0].startswith("http://") or parts[0].startswith("https://"):
                image["content"] = download_image(parts[0])

            else:
                image_path = path.parent / parts[0]
                image["content"] = read_image_data(image_path)

            images.append(image)


    return images


def upload(image):
    form = {
        "takenDate": image["taken_date"],
        "description": image["description"],
        "tags": image["tags"],
    }
    files = {"formFile": (image["name"], image["content"], "image/jpeg")}

    res = requests.post(UPLOAD_URL, data=form, files=files)

    print("uploaded", image["name"], ":", res.status_code)


def main():
    try:
        for image in read_images("./example-data.csv"):
            upload(image)

    except requests.exceptions.ConnectionError:
        print("ERROR: connection to image service failed. is it running?")


if __name__ == "__main__":
    main()
