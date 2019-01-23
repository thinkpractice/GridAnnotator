from DirectoryFilter import DirectoryFilter
from keras.applications import VGG16, imagenet_utils
from keras.models import Model
from keras.layers import GlobalAveragePooling2D, BatchNormalization, Dropout, Dense
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
import sys
import json
import os

model = None

def vgg16_model():
    base_model = VGG16(False, "imagenet")
    train_from_layer = -2
    for layer in base_model.layers[:train_from_layer]:
        layer.trainable = False
        print("{} is not trainable".format(layer.name))
    for layer in base_model.layers[train_from_layer:]:
        #layer.trainable = True
        layer.trainable = False
        print("{} is trainable".format(layer.name))
    last_conv_layer = base_model.get_layer("block5_conv3")
    x = GlobalAveragePooling2D()(last_conv_layer.output)
    x = Dense(512, activation="relu")(x)
    x = BatchNormalization(axis=-1)(x)
    x = Dropout(0.5)(x)
    predictions = Dense(1, activation="sigmoid")(x)
    return Model(base_model.input, predictions)


def get_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def get_files(directory):
    directory_filter = DirectoryFilter(directory)
    subdirectories = get_subdirectories(directory)
    if len(subdirectories) == 0:
        return directory_filter.rgb.images.paths
    return [directory_filter.dir(subdirectory).rgb.images.paths for subdirectory in subdirectories]


def load_model(weights_filename):
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    if not model:
        model = vgg16_model()
        model.load_weights(weights_filename)
    return model


def prepare_image(image, target):
    image = image.resize(target)
    image = img_to_array(image)
    image = image / 255
    return np.expand_dims(image, axis=0)


def classify_image(weights_filename, cut_off, image_file):
    cnn_model = load_model(weights_filename)
    image = load_img(image_file)
    pre_processed_image = prepare_image(image, target=(75, 75))
    predictions = cnn_model.predict(np.array(pre_processed_image))
    return pre_processed_image.shape, float(predictions[0][0]), bool(predictions[0][0] > cut_off)


def classify_images(weights_filename, cut_off, directory):
    classified_images = []
    image_files = get_files(directory)
    for i, image_file in enumerate(image_files):
        image_shape, prediction, image_classification = classify_image(weights_filename, cut_off, image_file)
        classified_images.append({
                                    "id": i,
                                    "width": image_shape[2],
                                    "height": image_shape[1],
                                    "annotation": image_classification,
                                    "prediction": prediction,
                                    "filename": image_file
                                  })
        if i % 100 == 0:
            print("Classified {} out of {} images".format(i, len(image_files)))
        if i > 0 and i % 300 == 0:
            break
    return classified_images


def write_json(filename, data):
    with open(filename, "w") as json_file:
        json.dump(data, json_file)


def main(argv):
    if len(argv) <= 4:
        print("usage: ClassifyPictures.py <weights> <cut_off> <directory> <outfile>")
        exit(0)
    weights_file = argv[1]
    cut_off = float(argv[2])
    directory = argv[3]
    outfile = argv[4]

    print("Classifying {} with model {} and cut_off {}, outfile: {}".format(directory, weights_file, cut_off, outfile))
    images = classify_images(weights_file, cut_off, directory)
    write_json(outfile, images)


if __name__ == "__main__":
    main(sys.argv)
