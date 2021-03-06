from __future__ import print_function
import numpy as np
import pathlib
import torch.utils.data as data
from collections import defaultdict, OrderedDict
from itertools import repeat

DATASET_PATH = pathlib.Path('path_to_dataset')

processed = False


class Cub(data.Dataset):
    # class 100 (50 test, 50 val), images per class variable, images size 84x84, channels 3
    def __init__(self, data, labels, train=True, all=False):
        data = data.transpose(0, 3, 1, 2).astype(np.float32) / 255.
        labels = np.asarray(labels).astype(np.int64)
        sorted_indices = np.argsort(labels)
        sorted_data = []
        sorted_true_labels = []
        for index in sorted_indices:
            sorted_data.append(data[index])
            sorted_true_labels.append(labels[index])
        sorted_data = np.asarray(sorted_data)
        sorted_true_labels = np.asarray(sorted_true_labels)

        self.data = list(sorted_data)
        self.targets = list(sorted_true_labels)

        self.data2 = []
        self.targets2 = []

        for a in range(int(len(self.targets) / 20)):
            start = a * 20
            if train:
                for b in range(start, start + 15):
                    self.data2.append(self.data[b])
                    self.targets2.append(self.targets[b])
            else:
                for b in range(start + 15, start + 20):
                    self.data2.append(self.data[b])
                    self.targets2.append(self.targets[b])
        self.targets = self.targets2
        self.data = self.data2

        print("Total classes = ", len(np.unique(self.targets)))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target character class.
        """
        image = self.data[index]
        target = self.targets[index]
        return image, target


class CubUnsupervised(data.Dataset):
    def __init__(self, data, partition, train=True, all=False):
        crop = 84
        start = data.shape[2] // 2 - crop // 2
        data = data[:, :, start:start + crop, start:start + crop]

        partition = OrderedDict(sorted(partition.items(), key=lambda t: t[0]))
        new_partition = defaultdict(list)
        for key, values in partition.items():
            for index in values:
                new_partition[key].append(data[index])

        self.data = []
        self.data2 = []
        self.targets = []
        self.targets2 = []
        for key, values in new_partition.items():
            key = key.astype(np.int64)
            train_partition = int(0.75 * len(values))
            self.data.extend(values)
            self.targets.extend(repeat(key, len(values)))
            if train:
                self.data2.extend(values[:train_partition])
                self.targets2.extend(repeat(key, train_partition))
            else:
                self.data2.extend(values[train_partition:])
                self.targets2.extend(repeat(key, (len(values)-train_partition)))

        self.targets = self.targets2
        self.data = self.data2

        print("Total classes = ", len(np.unique(self.targets)))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target character class.
        """
        image = self.data[index]
        target = self.targets[index]
        return image, target


if __name__ == '__main__':
    Cub(train=True)

