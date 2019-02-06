from flask import Flask, render_template, send_file, jsonify
from Dataset import Dataset
from PIL import Image
import io


app = Flask(__name__)
app.config.from_object('config.Config')

dataset = Dataset(app.config["CLASSIFICATION_FILE"], app.config["IMAGES_PER_PAGE"])
dataset.open()


def color_for_annotation(positive_annotation):
    return "#00ff00" if positive_annotation else "#ff0000"


def render_page(page_index):
    if page_index > dataset.number_of_pages:
        page_index = 0

    previous_page_number = page_index - 1 if page_index - 1 > 0 else 0
    next_page_number = page_index + 1 if page_index + 1 <= dataset.number_of_pages else 0

    images_for_page = dataset.get_images_for_page(page_index)
    for image in images_for_page:
        image["color"] = color_for_annotation(image["annotation"])
        image["url"] = "/get_image/{selected_dataset}/{id}".format(selected_dataset=1, id=image["id"])
        image["display_width"] = image["width"] * app.config["IMAGE_ZOOM_FACTOR"]
        image["display_height"] = image["height"] * app.config["IMAGE_ZOOM_FACTOR"]

    images = {
        "success": True,
        "images": images_for_page,
        "paging_start_index": page_index,
        "paging_end_index": page_index + 10,
        "previous_page_number": previous_page_number,
        "next_page_number": next_page_number,
        "number_of_pages": dataset.number_of_pages,
        "selected_dataset": 1
    }
    return render_template("view.html", **images)


@app.route("/")
def index():
    return render_page(dataset.current_page_index)


@app.route("/show/<int:data_set>/<int:page_index>")
def show(data_set, page_index):
    dataset.save()
    return render_page(page_index)


@app.route("/get_image/<int:data_set>/<int:image_id>")
def get_image(data_set, image_id):
    filename = dataset[image_id]["filename"]
    image_buffer = io.BytesIO()
    image = Image.open(filename)
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    return send_file(image_buffer,
                     mimetype='image/png',
                     as_attachment=False
                     )


@app.route("/annotate_image/<int:data_set>/<int:page_index>/<int:image_id>")
def annotate_image(data_set, page_index, image_id):
    image = dataset.annotate_image(image_id)
    image["color"] = color_for_annotation(image["annotation"])
    return show(data_set, page_index)


@app.route("/get_datasets")
def get_datasets():
    return jsonify([
        {"id": 1,
         "name": "annotations_2015.json"},
        {"id": 2,
         "name": "annotations_2016.json"}])


@app.route("/get_class_counts/<int:data_set>")
def get_class_counts(data_set):
    return jsonify(dataset.class_counts)


app.run()
dataset.save()
