"""
ID3 algo for building decision trees.

@author: vikash.madhow@gatech.edu
"""
from math import log2


class Attribute:
    def __init__(self, name, *values):
        self.name = name
        self.values = set(values)

    def type_check(self, value):
        if value not in self.values:
            raise TypeError("{} is not in the acceptable list of values {} for attribute {}".format(value, str(self.values), self.name))

    def __str__(self):
        return self.name


class Dataset:
    def __init__(self, attributes, classification_attribute, rows=None):
        self.attributes = attributes
        self.attribute_by_name = {attr.name:index for index, attr in attributes.items()}

        # A cache of datasets produced by selecting part of this dataset
        self._sub_dataset_cache = {}

        self.rows = []
        self.class_attr = classification_attribute
        self.class_attr_index = self.attribute_by_name[self.class_attr.name]
        self.attr_values_count = {index:{value:0 for value in attr.values} for index, attr in self.attributes.items()}
        self.rows_by_attr_value = {index:{value:[] for value in attr.values} for index, attr in self.attributes.items()}

        if rows is not None:
            self.add(*rows)

    def add(self, *rows):
        # type-check and increment counts for each value
        value_counts = {index:{value:0 for value in attr.values} for index, attr in self.attributes.items()}
        rows_by_attr_value = {index:{value:[] for value in attr.values} for index, attr in self.attributes.items()}

        for row in rows:
            for attr_index, attr in self.attributes.items():
                # attr = self.attributes[attr_index]
                attr_value = row[attr_index]
                attr.type_check(attr_value)
                value_counts[attr_index][attr_value] += 1
                rows_by_attr_value[attr_index][attr_value].append(row)

        # update counts
        for attr_index, value_count in value_counts.items():
            for value, count in value_count.items():
                self.attr_values_count[attr_index][value] += count

        # update rows by attribute values
        for attr_index, rows_by_value in rows_by_attr_value.items():
            for value, rs in rows_by_value.items():
                self.rows_by_attr_value[attr_index][value] += rs

        self.rows += rows


    def non_classifying_attributes(self):
        """Returns a map of all attributes of the dataset minus the classifying one."""
        return {index:attr for index, attr in self.attributes.items() if index != self.class_attr_index}

    def __len__(self):
        return len(self.rows)

    def entropy(self):
        ent = 0.0
        for value in self.class_attr.values:
            if len(self.rows) != 0:
                proportion = self.attr_values_count[self.class_attr_index][value] / len(self.rows)
                if proportion != 0:
                    ent -= proportion * log2(proportion)
        return ent

    def information_gain(self, attribute):
        if len(self.rows) == 0:
            return 0

        else:
            ent = 0.0
            for value in attribute.values:
                dataset = self.select(attribute, value)
                ent += len(dataset) / len(self.rows) * dataset.entropy()
            return self.entropy() - ent

    def select(self, attribute, value):
        """Returns a subset of the dataset for which the attribute has the specified value."""
        attr_index = self.attribute_by_name[attribute.name]
        sub_datasets = self._sub_dataset_cache.setdefault(attr_index, dict())
        selected = sub_datasets.setdefault(value, None)
        if selected is None:
            rows = self.rows_by_attr_value[attr_index][value]
            selected = Dataset(self.attributes, self.class_attr, rows)
            sub_datasets[value] = selected

        return selected

    def decision_tree(self):
        # if all examples has the same classification value, return that value as the target node value
        number_of_rows = len(self.rows)
        for value in self.attributes[self.class_attr_index].values:
            if self.attr_values_count[self.class_attr_index][value] == number_of_rows:
                return Leaf(value)

        # if there are no more attributes, simply return the most common value of the classification
        # attribute as the classification value
        attributes = self.non_classifying_attributes()
        value_counts = self.attr_values_count[self.class_attr_index]
        most_common_classifying_value = max(value_counts.keys(), key=lambda k: value_counts[k])
        if len(attributes) == 0:
            return Leaf(most_common_classifying_value)

        else:
            attr_gain = {index:self.information_gain(attr) for index, attr in attributes.items()}
            attr_index_max_gain = max(attr_gain.keys(), key=(lambda k: attr_gain[k]))

            attribute = attributes[attr_index_max_gain]
            value_to_node = dict()
            for value in attribute.values:
                selected_rows = self.select(attribute, value)
                if len(selected_rows) == 0:
                    value_to_node[value] = Leaf(most_common_classifying_value)
                else:
                    if attr_index_max_gain in selected_rows.attributes:
                        del selected_rows.attributes[attr_index_max_gain]

                    if attribute.name in selected_rows.attribute_by_name:
                        del selected_rows.attribute_by_name[attribute.name]

                    if attr_index_max_gain in selected_rows.attr_values_count:
                        del selected_rows.attr_values_count[attr_index_max_gain]

                    value_to_node[value] = selected_rows.decision_tree()

            return Decision(attribute, value_to_node)

    def classify(self, row):
        pass


class Node:
    pass


class Decision(Node):
    def __init__(self, attribute, value_to_node):
        self.attribute = attribute
        self.value_to_node = value_to_node


class Leaf(Node):
    def __init__(self, value):
        self.value = value


def main():
    outlook     = Attribute('outlook', 'sunny', 'overcast', 'rain')
    temperature = Attribute('temperature', 'cool', 'mild', 'hot')
    humidity    = Attribute('humidity', 'normal', 'high')
    wind        = Attribute('wind', 'weak', 'strong')
    play_tennis = Attribute('play_tennis', 'yes', 'no')

    dataset = Dataset(
        {0:outlook, 1:temperature, 2:humidity, 3:wind, 4:play_tennis},
        classification_attribute=play_tennis,
        rows=[
            ('sunny',    'hot',  'high',   'weak',   'no'),
            ('sunny',    'hot',  'high',   'strong', 'no'),
            ('overcast', 'hot',  'high',   'weak',   'yes'),
            ('rain',     'mild', 'high',   'weak',   'yes'),
            ('rain',     'cool', 'normal', 'weak',   'yes'),
            ('rain',     'cool', 'normal', 'strong', 'no'),
            ('overcast', 'cool', 'normal', 'strong', 'yes'),
            ('sunny',    'mild', 'high',   'weak',   'no'),
            ('sunny',    'cool', 'normal', 'weak',   'yes'),
            ('rain',     'mild', 'normal', 'weak',   'yes'),
            ('sunny',    'mild', 'normal', 'strong', 'yes'),
            ('overcast', 'mild', 'high',   'strong', 'yes'),
            ('overcast', 'hot',  'normal', 'weak',   'yes'),
            ('rain',     'mild', 'high',   'strong', 'no')
        ])

    print(dataset.entropy())
    print(dataset.information_gain(outlook))
    print(dataset.information_gain(humidity))
    print(dataset.information_gain(wind))
    print(dataset.information_gain(temperature))

    tree = dataset.decision_tree()
    print(tree)

if __name__ == "__main__":
    main()