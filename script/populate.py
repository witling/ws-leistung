#!/usr/bin/python3

UPLOAD_URL = "http://localhost:4000/upload"

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

            image_path = path.parent / parts[0]

            with open(str(image_path), 'rb') as image_blob:
                image["content"] = image_blob.read()
            
            images.append(image)


    return images


def upload(image):
    import requests

    form = {
        "takenDate": image["taken_date"],
        "description": image["description"],
        "tags": image["tags"],
    }
    files = {"formFile": (image["name"], image["content"], "image/jpeg")}

    res = requests.post(UPLOAD_URL, data=form, files=files)

    print("uploaded", image["name"], ":", res.status_code)


def main():
    for image in read_images("./example-data.csv"):
        upload(image)


if __name__ == "__main__":
    main()
