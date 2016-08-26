#!/usr/bin/env python3


class Concept:

    ALL = '*'
    NONE = '∅'          # Empty set: unicode u'\u2205'

    def __init__(self, attributes_count):
        self.attributes_count = attributes_count
        self._hypothesis = [Concept.NONE for _ in range(attributes_count)]

    def __call__(self, *instance):
        self._check_attributes(*instance)
        for i in range(len(instance)):
            if self._hypothesis[i] == Concept.NONE:
                return False
            elif self._hypothesis[i] != Concept.ALL and self._hypothesis[i] != instance[i]:
                return False
        return True

    def positive_example(self, *attributes):
        """
        Find-S algorithm for finding the maximally specific hypothesis,
        one positive instance at a time.
        :param attributes: The attributes of the +ve example.
        """
        raise NotImplementedError()

    def negative_example(self, *attributes):
        """This implementation does nothing for negative examples."""
        raise NotImplementedError()

    def _check_attributes(self, *attributes):
        if len(attributes) != self.attributes_count:
            raise ValueError("This concept requires {} concept(s) but {} was provided".format(self.attributes_count, len(attributes)))


class MaximallySpecificConcept(Concept):

    def positive_example(self, *attributes):
        """
        Find-S algorithm for finding the maximally specific hypothesis,
        one positive instance at a time.
        :param attributes: The attributes of the +ve example.
        """
        self._check_attributes(*attributes)
        for i in range(len(attributes)):
            if self._hypothesis[i] == Concept.NONE:
                self._hypothesis[i] = attributes[i]
            elif self._hypothesis[i] != attributes[i]:
                self._hypothesis[i] = Concept.ALL

    def negative_example(self, *attributes):
        """This implementation does nothing for negative examples."""
        self._check_attributes(*attributes)


class VersionSpace(Concept):
    def __init__(self, attributes_count):
        super().__init__(attributes_count)
        self._general = [Concept.ALL for _ in range(attributes_count)]
        self._specific = self._hypothesis

    def positive_example(self, *attributes):
        self._check_attributes(*attributes)

def main():
    eatOutside = MaximallySpecificConcept(5)

    print(eatOutside._hypothesis)

    eatOutside.positive_example('Sunny', 'Warm', 'High', 'Hungry', 'Hot')
    print(eatOutside._hypothesis)

    eatOutside.positive_example('Sunny', 'Cold', 'Medium', 'Hungry', 'Hot')
    print(eatOutside._hypothesis)

    print(eatOutside('Sunny', 'Cold', 'Medium', 'Hungry', 'Hot'))
    print(eatOutside('Sunny', 'Warm', 'Medium', 'Not hungry', 'Hot'))

if __name__ == "__main__":
    main()
