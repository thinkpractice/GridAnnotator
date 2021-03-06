from flask import Flask, render_template, send_file, jsonify
from DatasetFactory import DatasetFactory
from PIL import Image
import io


app = Flask(__name__)
app.config.from_object('config.Config')

data_set_factory = DatasetFactory(app.config["CLASSIFICATION_DIR"], app.config["IMAGES_PER_PAGE"])


def color_for_annotation(positive_annotation):
    return "#00ff00" if positive_annotation else "#ff0000"


def render_page(data_set, page_index):
    dataset = data_set_factory[data_set]
    if page_index > dataset.number_of_pages:
        page_index = 0

    previous_page_number = page_index - 1 if page_index - 1 > 0 else 0
    next_page_number = page_index + 1 if page_index + 1 <= dataset.number_of_pages else 0

    images_for_page = dataset.get_images_for_page(page_index)
    for image in images_for_page:
        image["color"] = color_for_annotation(image["annotation"])
        image["url"] = "/get_image/{selected_dataset}/{id}".format(selected_dataset=data_set, id=image["id"])
        image["display_width"] = image["width"] * app.config["IMAGE_ZOOM_FACTOR"]
        image["display_height"] = image["height"] * app.config["IMAGE_ZOOM_FACTOR"]

    page_end_index = page_index + 10 if page_index + 10 < dataset.number_of_pages else dataset.number_of_pages
    images = {
        "success": True,
        "images": images_for_page,
        "paging_start_index": page_index,
        "paging_end_index": page_end_index,
        "previous_page_number": previous_page_number,
        "next_page_number": next_page_number,
        "number_of_pages": dataset.number_of_pages - 1,
        "selected_dataset": data_set
    }
    return render_template("view.html", **images)


@app.route("/")
def index():
    app.config["CURRENT_DATASET"] = 0
    return render_page(0, data_set_factory[0].current_page_index)


@app.route("/show/<int:data_set_index>/<int:page_index>")
def show(data_set_index, page_index):
    data_set_changed = data_set_index != app.config["CURRENT_DATASET"]

    data_set = data_set_factory[data_set_index]
    data_set.save()

    page_index = page_index if not data_set_changed else data_set.current_page_index
    if data_set_changed:
        app.config["CURRENT_DATASET"] = data_set_index
    return render_page(data_set_index, page_index)


@app.route("/get_image/<int:data_set>/<int:image_id>")
def get_image(data_set, image_id):
    filename = data_set_factory[data_set][image_id]["filename"]
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
    image = data_set_factory[data_set].annotate_image(image_id)
    image["color"] = color_for_annotation(image["annotation"])
    return show(data_set, page_index)


@app.route("/get_data_sets/<int:current_data_set>")
def get_data_sets(current_data_set):
    return jsonify([{
                     "id": data_set_index,
                     "name": data_set.name,
                     "selected": data_set_index == current_data_set
                    }
                    for data_set_index, data_set in enumerate(data_set_factory.data_sets)])


@app.route("/get_class_counts/<int:data_set>")
def get_class_counts(data_set):
    return jsonify(data_set_factory[data_set].class_counts)


@app.teardown_appcontext
def teardown_factory(e):
    data_set_factory.save_all()


app.run()
