# flake8: noqa
import uuid
from random import choice, randint


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
        'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o',
        'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k',
        'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ' ',
    ]

    RUSSIAN_ABC = [
        'й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'ю', ' ',
        'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'т', 'ь'
        'о', 'л', 'д', 'ж', 'э', 'я', 'ч', 'с', 'м', 'и', 'б',
    ]

    def __init__(self, generator_name: str, length=10):
        self.length = length
        self.generator_name = generator_name
        self.generators = {
            self.UUID: self.uuid,
            self.RUSSIAN: self.russian,
            self.ENGLISH: self.english,
            self.MIXED: self.mixed,
            self.ZALGO: self.zalgo,
        }

    def uuid(self):
        return f'{uuid.uuid4()}'

    def russian(self):
        return ''.join([choice(self.RUSSIAN_ABC) for _ in range(self.length)])

    def english(self):
        return ''.join([choice(self.ENGLISH_ABC) for _ in range(self.length)])

    def mixed(self):
        abc = self.RUSSIAN_ABC
        abc.extend(self.ENGLISH_ABC)
        return ''.join([choice(abc) for _ in range(self.length)])

    def zalgo(self):
        marks = list(map(chr, range(358, 989)))
        rnd_marks = marks[:randint(5, self.length)]
        return ''.join(''.join(c + ''.join(choice(marks) for _ in range(randint(5, 20))) for c in rnd_marks))

    def get_generator(self):
        generator = self.generators.get(self.generator_name, None)
        if generator is None:
            raise ValueError(f'Unknown generator type {self.generator_name}')
        return generator
