import json
import math


class Dataset(object):
    def __init__(self, filename, images_per_page, current_page_index=0):
        self.__filename = filename
        self.__images_per_page = images_per_page
        self.__current_page_index = current_page_index
        self.__images = []
        self.__paginated_images = []

    @property
    def filename(self):
        return self.__filename

    @property
    def images_per_page(self):
        return self.__images_per_page

    @property
    def current_page_index(self):
        return self.__current_page_index

    @current_page_index.setter
    def current_page_index(self, value):
        self.__current_page_index = value
    
    @property
    def number_of_pages(self):
        return math.ceil(len(self.images) / self.images_per_page)

    @property
    def class_counts(self):
        return [
            {"label": "Positives", "count": 10},
            {"label": "Negatives", "count": 20}
        ]

    @property
    def images(self):
        return self.__images

    @property
    def paginated_images(self):
        if not self.__paginated_images:
            self.__paginated_images = self.paginate(self.images, self.images_per_page)
        return self.__paginated_images

    def __getitem__(self, item_index):
        return self.images[item_index]

    def open(self):
        if not self.__images:
            self.__current_page_index, self.__images = self.get_images(self.filename)

    def save(self):
        with open(self.filename, "w") as json_file:
            data = {"current_page_index": self.current_page_index,
                    "images": self.images
                    }
            json.dump(data, json_file)

    def annotate_image(self, image_id):
        image = self.images[image_id]
        image["annotation"] = not image["annotation"]
        return image

    def get_images_for_page(self, page_index):
        return self.paginated_images[page_index]

    def paginate(self, images, images_per_page):
        paginated_images = []
        page_images = []
        for i, image in enumerate(images):
            if (i % images_per_page == 0 and i > 0) or i == len(images):
                images_to_return = page_images
                page_images = []
                paginated_images.append(images_to_return)
            page_images.append(image)
        return paginated_images

    def get_images(self, annotation_filename):
        with open(annotation_filename, "r") as json_file:
            json_data = json.load(json_file)
            current_page_index = json_data["current_page_index"]
            return current_page_index, json_data["images"]
