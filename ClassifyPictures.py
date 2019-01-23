from DirectoryFilter import DirectoryFilter
import sys
import random
import json
import os


def get_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def get_files(directory):
    directory_filter = DirectoryFilter(directory)
    subdirectories = get_subdirectories(directory)
    if len(subdirectories) == 0:
        return directory_filter.rgb.images.paths
    return [directory_filter.dir(subdirectory).rgb.images.paths for subdirectory in subdirectories]


def classify_images(directory):
    classified_images = []
    image_files = get_files(directory)
    for i, image_file in enumerate(image_files):
        positive_annotation = bool(random.getrandbits(1))
        classified_images.append({
                                    "id": i,
                                    "width": 150,
                                    "height": 150,
                                    "annotation": positive_annotation,
                                    "filename": image_file
                                  })
    return classified_images


def write_json(filename, data):
    with open(filename, "w") as json_file:
        json.dump(data, json_file)


def main(argv):
    if len(argv) <= 2:
        print("usage: ClassifyPictures.py <directory> <outfile>")
        exit(0)
    directory = argv[1]
    outfile = argv[2]
    images = classify_images(directory)
    write_json(outfile, images)


if __name__ == "__main__":
    main(sys.argv)
