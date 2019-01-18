from flask import Flask, render_template, send_file
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
    paginated_images = []
    page_images = []
    for i, image in enumerate(images):
        if (i % images_per_page == 0 and i > 0) or i == len(images):
            images_to_return = page_images
            page_images = []
            paginated_images.append(images_to_return)
        positive_annotation = bool(random.getrandbits(1))
        page_images.append({"id": i, "url": "/get_image/{}".format(i),
                            "width": 75, "height": 75,
                            "annotation": positive_annotation,
                            "color": color_for_annotation(positive_annotation)})
    return paginated_images


def color_for_annotation(positive_annotation):
    return "#00ff00" if positive_annotation else "#ff0000"


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


@app.route("/get_image/<int:image_id>")
def get_image(image_id):
    return send_file(image_files[image_id],
                     mimetype='image/png',
                     as_attachment=False
                     )


@app.route("/annotate_image/<int:page_index>/<int:image_id>")
def annotate_image(page_index, image_id):
    image = all_images[page_index][image_id-page_index*16]
    image["annotation"] = not image["annotation"]
    image["color"] = color_for_annotation(image["annotation"])
    return show(page_index)


app.run()
