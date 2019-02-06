from flask import Flask, render_template, send_file, jsonify
from PIL import Image
import io
import math
import json


app = Flask(__name__)
app.config.from_object('config.Config')


def get_files():
    classification_file = app.config["CLASSIFICATION_FILE"]
    with open(classification_file, "r") as json_file:
        json_data = json.load(json_file)
        app.config["CURRENT_PAGE_INDEX"] = json_data["current_page_index"]
        return json_data["images"]



image_files = get_files()


def paginate(images, images_per_page):
    paginated_images = []
    page_images = []
    for i, image in enumerate(images):
        if (i % images_per_page == 0 and i > 0) or i == len(images):
            images_to_return = page_images
            page_images = []
            paginated_images.append(images_to_return)
        image["url"] = "/get_image/{}".format(i)
        image["display_width"] = image["width"] * app.config["IMAGE_ZOOM_FACTOR"]
        image["display_height"] = image["height"] * app.config["IMAGE_ZOOM_FACTOR"]
        image["color"] = color_for_annotation(image["annotation"])
        page_images.append(image)
    return paginated_images


def unpaginate(paginated_images):
    return [image for page in paginated_images for image in page]


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


def save_annotations(filename, annotations, current_page_index):
    with open(filename, "w") as json_file:
        data = {"current_page_index": current_page_index,
                "images": annotations
                }
        json.dump(data, json_file)


@app.route("/")
def index():
    return render_page(app.config["CURRENT_PAGE_INDEX"])


@app.route("/show/<int:page_index>")
def show(page_index):
    app.config["CURRENT_PAGE_INDEX"] = page_index
    save_annotations(app.config["CLASSIFICATION_FILE"], unpaginate(all_images), page_index)
    return render_page(page_index)


@app.route("/get_image/<int:image_id>")
def get_image(image_id):
    filename = image_files[image_id]["filename"]
    image_buffer = io.BytesIO()
    image = Image.open(filename)
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    return send_file(image_buffer,
                     mimetype='image/png',
                     as_attachment=False
                     )


@app.route("/annotate_image/<int:page_index>/<int:image_id>")
def annotate_image(page_index, image_id):
    image = all_images[page_index][image_id-page_index*16]
    image["annotation"] = not image["annotation"]
    image["color"] = color_for_annotation(image["annotation"])
    return show(page_index)


@app.route("/get_datasets")
def get_datasets():
    return jsonify([
        {"id": 1,
         "name": "annotations_2015.json"},
        {"id": 2,
         "name": "annotations_2016.json"}])


@app.route("/get_class_counts")
def get_class_counts():
    return jsonify([
        {"label": "Positives", "count": 10},
        {"label": "Negatives", "count": 20}
        ]
    )


app.run()
save_annotations(app.config["CLASSIFICATION_FILE"], unpaginate(all_images), app.config["CURRENT_PAGE_INDEX"])
