import threading
import numpy as np
import SimpleITK as sitk


class NiftiGenerator2D_ExtraInput(object):

    def __init__(self, batch_size, image_locations,
                 labels, image_size, extra_inputs, random_shuffle=True):
        self.n = len(image_locations)
        self.batch_size = batch_size
        self.batch_index = 0
        self.total_batches_seen = 0
        self.lock = threading.Lock()
        self.index_array = None
        self.index_generator = self._flow_index()
        self.image_locations = image_locations
        self.labels = labels
        self.image_size = image_size
        self.random_shuffle = random_shuffle
        self.extra_inputs = extra_inputs

    def _set_index_array(self):
        if self.random_shuffle:
            self.index_array = np.random.permutation(self.n)
        else:
            self.index_array = np.arange(self.n)

    def __iter__(self):
        return self

    def __next__(self, *args, **kwargs):
        return self.next(*args, **kwargs)

    def reset(self):
        self.batch_index = 0
        self.total_batches_seen = 0
        self._set_index_array()

    def _flow_index(self):
        self.reset()
        while 1:
            if self.batch_index == 0:
                self._set_index_array()

            current_index = (self.batch_index * self.batch_size) % self.n
            if self.n > current_index + self.batch_size:
                self.batch_index += 1
            else:
                self.batch_index = 0
            self.total_batches_seen += 1

            if current_index + self.batch_size > self.n:
                N_missing_samples = (current_index + self.batch_size) - self.n
                batch_indices_leftover = self.index_array[current_index:]
                self.reset()
                batch_indices_filler = self.index_array[0:N_missing_samples]
                batch_indices = np.concatenate((batch_indices_leftover, batch_indices_filler))
            else:
                batch_indices = self.index_array[current_index:
                                            current_index + self.batch_size]
            yield batch_indices

    def on_epoch_end(self):
        self.reset()

    def _get_batch_of_samples(self, index_array):
        image_tensor = np.zeros((self.batch_size,
                                 self.image_size[0],
                                 self.image_size[1],
                                 1))

        out_labels = self.labels[index_array, :]
        out_extra_inputs = self.extra_inputs[index_array, :]

        image_locations = self.image_locations[index_array]

        for i_sample, i_image_location in enumerate(image_locations):
            i_image = sitk.ReadImage(i_image_location, sitk.sitkFloat32)
            i_image_array = sitk.GetArrayFromImage(i_image)
            image_tensor[i_sample, :, :, 0] = i_image_array[:, :]

        return [image_tensor, out_extra_inputs], out_labels

    def next(self):
        with self.lock:
            index_array = next(self.index_generator)

        return self._get_batch_of_samples(index_array)

    def get_single_image(self, image_path):
        full_sample_tensor = np.zeros((1,
                                       self.image_size[0],
                                       self.image_size[1],
                                       1))
        i_image = sitk.ReadImage(image_path, sitk.sitkFloat32)
        i_image_array = sitk.GetArrayFromImage(i_image)
        full_sample_tensor[0, :, :, 0] = i_image_array
        return full_sample_tensor
