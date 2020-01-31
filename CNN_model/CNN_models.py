from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import PReLU


def DDS_model(img_rows, img_cols, img_channels):
    model = Model()
    image_input = Input(shape=(img_rows, img_cols, img_channels), dtype='float32')

    dicom_tag_input = Input(shape=(1, ), dtype='float32')
    dicom_tag_dropped = Dropout(0.25)(dicom_tag_input)

    conv1 = Conv2D(32, (5, 5))(image_input)
    batch1 = BatchNormalization(axis=-1)(conv1)
    relu1 = PReLU()(batch1)
    conv2 = Conv2D(32, (5, 5))(relu1)
    batch2 = BatchNormalization(axis=-1)(conv2)
    relu2 = PReLU()(batch2)
    pooling1 = MaxPooling2D(pool_size=(3, 3))(relu2)

    conv3 = Conv2D(64, (5, 5))(pooling1)
    batch3 = BatchNormalization(axis=-1)(conv3)
    relu3 = PReLU()(batch3)
    conv4 = Conv2D(64, (5, 5))(relu3)
    batch4 = BatchNormalization(axis=-1)(conv4)
    relu4 = PReLU()(batch4)
    pooling2 = MaxPooling2D(pool_size=(3, 3))(relu4)

    conv5 = Conv2D(64, (5, 5))(pooling2)
    batch5 = BatchNormalization(axis=-1)(conv5)
    relu5 = PReLU()(batch5)
    conv6 = Conv2D(64, (5, 5))(relu5)
    batch6 = BatchNormalization(axis=-1)(conv6)
    relu6 = PReLU()(batch6)
    pooling3 = MaxPooling2D(pool_size=(3, 3))(relu6)

    flattened_CNN_output = Flatten()(pooling3)

    merged_inputs = concatenate([flattened_CNN_output, dicom_tag_dropped])

    dropout_inputs = Dropout(0.4)(merged_inputs)
    dense = Dense(1024, activation='relu')(dropout_inputs)

    dropout_dense = Dropout(0.4)(dense)

    predictions = Dense(8, activation='softmax')(dropout_dense)

    model = Model(inputs=[image_input, dicom_tag_input], outputs=predictions)

    return model
