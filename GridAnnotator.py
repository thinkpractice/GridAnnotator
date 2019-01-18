from flask import Flask, render_template
from DirectoryFilter import DirectoryFilter
import math
import random

app = Flask(__name__)
directoryFilter = DirectoryFilter(r"/media/tim/Data/Work/CBS/DeepSolaris/Images/Tiles/Old/Heerlen_png")


def get_files():
    return directoryFilter.dir("2013").rgb.images.paths + \
           directoryFilter.dir("2014").rgb.images.paths + \
           directoryFilter.dir("2015").rgb.images.paths


image_files = get_files()


def paginate(images, images_per_page):
    all_images = []
    page_images = []
    for i, image in enumerate(images):
        if (i % images_per_page == 0 and i > 0) or i == len(images):
            images_to_return = page_images
            page_images = []
            all_images.append(images_to_return)
        border_color = "#00ff00" if bool(random.getrandbits(1)) else "#ff0000"
        page_images.append({"id": i, "url": image, "width": 75, "height": 75, "color": border_color })
    return all_images


all_images = paginate(image_files, 16)


def render_page(page_index):
    images_per_page = 16
    number_of_pages = math.ceil(len(image_files) / images_per_page)
    if page_index > number_of_pages:
        page_index = 0

    previous_page_number = page_index - 1 if page_index - 1 > 0 else 0
    next_page_number = page_index + 1 if page_index + 1 <= number_of_pages else 0

    images = {
        "success": True,
        "images": all_images[page_index],
        "paging_start_index": page_index,
        "paging_end_index": page_index + 10,
        "previous_page_number": previous_page_number,
        "next_page_number": next_page_number,
        "number_of_pages": number_of_pages
    }
    return render_template("view.html", **images)


@app.route("/")
def index():
    return render_page(0)


@app.route("/show/<int:page_index>")
def show(page_index):
    return render_page(page_index)


app.run()
