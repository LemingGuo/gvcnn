import numpy as np
import cv2
import os
import random

import tensorflow as tf


class Data(object):

    def __init__(self, dataset_dir, h_w):
        self.dataset_dir = dataset_dir
        self.resize_h = h_w[0]
        self.resize_w = h_w[1]

        self.images, self.labels = self._prepare_data()
        self.shuffle()


    def _prepare_data(self):
        classes = os.listdir(self.dataset_dir)
        classes.sort()
        tf.logging.info("classes: %s", classes)

        images = []
        labels = []
        for cls in classes:
            l_train_path = os.path.join(self.dataset_dir, cls, 'train')
            imgs = os.listdir(l_train_path)

            for img in imgs:
                views_path = os.path.join(l_train_path, img)
                views = os.listdir(views_path)
                vs = []
                for v in views:
                    v_path = os.path.join(views_path, v)
                    vs.append(v_path)

                images.append(vs)
                labels.append(cls)

        return images, labels


    def shuffle(self):
        combined = list(zip(self.images, self.labels))
        random.shuffle(combined)
        self.images, self.labels = zip(*combined)


    def _parse_function(self, start, end):

        images = []
        batch_img = self.images[start:end]
        for views_path in batch_img:
            views = []
            views_path.sort()
            for view in views_path:
                image_string = tf.read_file(view)
                # image_decoded = tf.image.decode_png(image_string, channels=3)
                image_decoded = tf.image.decode_png(image_string, channels=3)
                # cropped_image = tf.image.central_crop(image_decoded, 0.7)
                # rotated_image = tf.image.rot90(image_decoded, 1)
                resized_image = tf.image.resize_images(image_decoded, [self.resize_h, self.resize_w])
                # image = tf.cast(image_decoded, tf.float32)
                # image = tf.image.convert_image_dtype(resized_image, dtype=tf.float32)
                # Finally, rescale to [-1,1] instead of [0, 1)
                # image = tf.subtract(image, 0.5)
                # image = tf.multiply(image, 2.0)
                views.append(resized_image)

            images.append(views)

            labels = tf.convert_to_tensor(self.labels, dtype=tf.string)

        return tf.parallel_stack(images), labels


    def next_batch(self, start, end):
        return self._parse_function(start, end)

