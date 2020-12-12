# flake8: noqa
import uuid
from random import choice


class NameMixin(object):

    UUID = 'uuid'

    RUSSIAN = 'russian'

    ENGLISH = 'english'

    MIXED = 'mixed'

    ZALGO = 'zalgo'

    TYPES = (
        UUID,
        RUSSIAN,
        ENGLISH,
        MIXED,
        ZALGO,
    )

    ENGLISH_ABC = [
        'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
        'z', 'x', 'c', 'v', 'b', 'n', 'm', ' ',
    ]

    RUSSIAN_ABC = [
        'й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л',
        'д', 'ж', '', 'э', 'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю', ' ',
    ]

    def __init__(self, generator_name: str, length=10):
        self.length = length
        self.generator_name = generator_name

    def uuid(self):
        return f'{uuid.uuid4()}'

    def russian(self):
        return ''.join([choice(self.RUSSIAN_ABC) for _ in range(self.length)])

    def english(self):
        return ''.join([choice(self.ENGLISH_ABC) for _ in range(self.length)])

    def mixed(self, join=''):
        abc = self.RUSSIAN_ABC
        abc.extend(self.ENGLISH_ABC)
        return join.join([choice(abc) for _ in range(self.length)])

    def zalgo(self):
        marks = list(map(chr, range(768, 879)))
        string = self.mixed(join=' ')
        words = string.split()
        return ' '.join(''.join(c + ''.join(choice(marks) for _ in range(i // 2 + 1)) * c.isalnum() for c in word) for i, word in enumerate(words))

    def get_generator(self):
        if self.generator_name == self.UUID:
            return self.uuid
        elif self.generator_name == self.RUSSIAN:
            return self.russian
        elif self.generator_name == self.ENGLISH:
            return self.english
        elif self.generator_name == self.MIXED:
            return self.mixed
        elif self.generator_name == self.ZALGO:
            return self.zalgo
        raise ValueError(f'Unknown generator type {self.generator_name}')
