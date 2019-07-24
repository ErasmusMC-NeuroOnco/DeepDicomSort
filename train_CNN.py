import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard, ReduceLROnPlateau, EarlyStopping
import numpy as np
import yaml
import Tools.data_IO as data_IO
import CNN_model.CNN_models as models
import os
import datetime

with open('./config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

train_label_file = cfg['training']['train_label_file']
x_image_size = cfg['data_preparation']['image_size_x']
y_image_size = cfg['data_preparation']['image_size_y']
output_folder = cfg['training']['output_folder']
batch_size = cfg['network']['batch_size']
nb_epoch = cfg['network']['nb_epoch']

now = str(datetime.datetime.now()).replace(' ', '_')
model_name = 'DDS_model_epochs' + str(nb_epoch) + '_time_' + now


def get_one_hot(targets, nb_classes):
    res = np.eye(nb_classes)[np.array(targets).reshape(-1)]
    return res.reshape(list(targets.shape)+[nb_classes])


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

    one_hot_labels = get_one_hot(label_values, N_classes)

    return label_IDs, one_hot_labels, N_classes, extra_inputs


train_image_IDs, train_image_labels, N_train_classes, extra_inputs = load_labels(train_label_file)

print("Detected %d classes in training data" % N_train_classes)

print(extra_inputs)


NiftiGenerator_train = data_IO.NiftiGenerator2D_ExtraInput(batch_size,
                                                           train_image_IDs,
                                                           train_image_labels,
                                                           [x_image_size, y_image_size],
                                                           extra_inputs)

steps_per_epoch = int(np.floor(len(train_image_IDs)/float(batch_size)))
print("%d steps per epoch" % steps_per_epoch)


optimizer = tf.keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-7, decay=0.0, amsgrad=False)
lr_callback = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=3, min_lr=0.000001, verbose=1)
stopping_callback = EarlyStopping(monitor='loss', patience=6, verbose=1)

model_args = {'img_rows': x_image_size, 'img_cols': y_image_size, 'img_channels': 1}
model = models.DDS_model(**model_args)

tensorboard_log_dir = os.path.join(output_folder, 'tensorboard', model_name)
if not os.path.exists(tensorboard_log_dir):
    os.makedirs(tensorboard_log_dir)

tensorboard_log = TensorBoard(log_dir=tensorboard_log_dir)

callbacks = [tensorboard_log, lr_callback, stopping_callback]

model.compile(loss='categorical_crossentropy',
              optimizer=optimizer,
              metrics=['categorical_accuracy'])

model.fit_generator(NiftiGenerator_train,
                    epochs=nb_epoch,
                    steps_per_epoch=steps_per_epoch,
                    callbacks=callbacks,
                    use_multiprocessing=False,
                    workers=4)

model.save(os.path.join(output_folder, model_name + '.hdf5'))
