from Dataset import Dataset
import os


class DatasetFactory(object):
    def __init__(self, annotations_dir, images_per_page):
        self.__annotations_dir = annotations_dir
        self.__images_per_page = images_per_page
        self.__data_sets = []

    @property
    def annotations_dir(self):
        return self.__annotations_dir

    @property
    def images_per_page(self):
        return self.__images_per_page

    @property
    def data_sets(self):
        if not self.__data_sets:
            self.__data_sets = self.get_data_sets()
        return self.__data_sets

    def __getitem__(self, data_set_index):
        data_set = self.data_sets[data_set_index]
        data_set.open()
        return data_set

    def get_data_sets(self):
        return [Dataset(os.path.join(self.annotations_dir, filename), self.images_per_page)
                for filename in os.listdir(self.annotations_dir)
                if filename.endswith("json")]

    def save_all(self):
        for data_set in self.data_sets:
            if not data_set.is_open or not data_set.is_changed:
                continue
            data_set.save()

