from tensorflow.keras.models import load_model
import numpy as np
import Tools.data_IO as data_IO
import tensorflow as tf
import yaml
import os

model_file = './Trained_Models/model_all_brain_tumor_data.hdf5'
batch_size = 1

with open('./config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

test_label_file = cfg['testing']['test_label_file']
output_folder = cfg['testing']['output_folder']
x_image_size = cfg['data_preparation']['image_size_x']
y_image_size = cfg['data_preparation']['image_size_y']

model_name = os.path.basename(os.path.normpath(model_file)).split('.hdf5')[0]
out_file = os.path.join(output_folder, 'Predictions_' + model_name + '.csv')


def load_labels(label_file):
    labels = np.genfromtxt(label_file, dtype='str')
    label_IDs = labels[:, 0]
    label_IDs = np.asarray(label_IDs)
    label_values = labels[:, 1].astype(np.int)
    extra_inputs = labels[:, 2:].astype(np.float)
    np.round(extra_inputs, 2)

    N_classes = len(np.unique(label_values))

    # Make sure that minimum of labels is 0
    label_values = label_values - np.min(label_values)

    return label_IDs, label_values, N_classes, extra_inputs


test_image_IDs, test_image_labels, _, extra_inputs = load_labels(test_label_file)


optimizer = tf.keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-7, decay=0.0, amsgrad=False)

model = load_model(model_file)
model.compile(
        loss='categorical_crossentropy',
        optimizer=optimizer,
        metrics=['categorical_accuracy']
)

NiftiGenerator_test = data_IO.NiftiGenerator2D_ExtraInput(batch_size,
                                                           test_image_IDs,
                                                           test_image_labels,
                                                           [x_image_size, y_image_size],
                                                           extra_inputs)

with open(out_file, 'w') as the_file:
    for i_file, i_label, i_extra_input in zip(test_image_IDs, test_image_labels, extra_inputs):
        print(i_file)

        image = NiftiGenerator_test.get_single_image(i_file)

        supplied_extra_input = np.zeros([1, 1])
        supplied_extra_input[0, :] = i_extra_input
        prediction = model.predict([image, supplied_extra_input])
        the_file.write(i_file + '\t' + str(np.argmax(prediction) + 1) + '\t' + str(i_label) + '\n')
