from typing import Union, Callable


class BaseFont:
    FONT_ID = 0

    def __init__(self, font_name: str,
                 font_type: str = 'normal',
                 italic: bool = False,
                 bold: bool = False):

        self.font_id = BaseFont.FONT_ID
        BaseFont.FONT_ID += 1

        self.font_name = font_name
        self.font_type = font_type
        self.italic = italic
        self.bold = bold

    def __str__(self):
        return '%s(%s)' % (self.font_name, self.font_id)

    def d(self):
        pass

    def get_font_letter(self, letter):
        pass

    def get_pure_letter(self, letter):
        pass

    def set_bold(self, bold=True):
        self.bold = bold
        return self

    def set_italic(self, italic=True):
        self.italic = italic
        return self

    def normal(self):
        self.font_type = 'normal'
        return self

    def odd(self):
        self.font_type = 'odd'
        return self

    def flourish(self):
        self.font_type = 'flourish'
        return self

    def dot(self):
        self.font_type = 'dot'
        return self

    def double(self):
        self.font_type = 'double'
        return self

    def tiny(self):
        self.font_type = 'tiny'
        return self

    def void(self):
        self.font_type = 'void'
        return self


class LetterFont(BaseFont):
    @staticmethod
    def islower(letter):
        return 'z' >= letter >= 'a'

    @staticmethod
    def isupper(letter):
        return 'Z' >= letter >= 'A'

    def islower_font(self, letter):
        return self.lowercase[0] <= letter <= self.lowercase[-1]

    def isupper_font(self, letter):
        return self.uppercase[0] <= letter <= self.uppercase[-1]

    def get_font_letter(self, letter):
        if self.islower(letter):
            return self.lowercase[ord(letter) - ord('a')]
        elif self.isupper(letter):
            return self.uppercase[ord(letter) - ord('A')]
        return letter

    def get_pure_letter(self, letter):
        if self.islower_font(letter):
            return chr(ord(letter) - ord(self.lowercase[0]) + ord('a'))
        elif self.isupper_font(letter):
            return chr(ord(letter) - ord(self.uppercase[0]) + ord('A'))
        return letter

    def __init__(self, font_name: str, uppercase: str, lowercase: str):
        super(LetterFont, self).__init__(font_name)

        self.uppercase = uppercase
        self.lowercase = lowercase

        self.unsupported_letters = ''
        self.unsupported_font_letters = ''

    def unsupport(self, letters: str):
        self.unsupported_letters = ''
        self.unsupported_font_letters = ''
        for letter in letters:
            font_letter = self.get_font_letter(letter)
            if font_letter != letter:
                self.unsupported_font_letters += font_letter
                self.unsupported_letters += letter
        return self

    def supporting(self, sentence: str):
        for letter in sentence:
            if letter in self.unsupported_letters:
                return False
        return True

    def d(self):
        return dict(
            font_id=self.font_id,
            font_name=self.font_name,
            uppercase=self.uppercase,
            lowercase=self.lowercase,
            full_supported=not self.unsupported_letters,
            unsupported_letters=self.unsupported_letters,
        )

    def d_base(self):
        return dict(
            font_id=self.font_id,
            font_name=self.font_name,
        )

    def translate(self, sentence: str, unsupport_handler: Union[str, Callable] = 'default'):
        """
        将普通英文转变为字体英文
        :param sentence: 英文字符串
        :param unsupport_handler: 若字体不支持该字符的采取办法，ignore/force/default/callable
        """
        new_sentence = ''
        for letter in sentence:
            if letter in self.unsupported_letters:
                if unsupport_handler == 'default':
                    new_sentence += letter
                elif callable(unsupport_handler):
                    new_sentence += unsupport_handler(letter)
                if unsupport_handler != 'force':
                    continue
            new_sentence += self.get_font_letter(letter)
        return new_sentence


class DigitFont(BaseFont):
    @staticmethod
    def isdigit(digit):
        return '0' <= digit <= '9'

    def get_font_letter(self, digit):
        if self.isdigit(digit):
            return self.font[ord(digit) - ord('0')]
        return digit

    def get_pure_letter(self, digit):
        if self.font[0] <= digit <= self.font[-1]:
            return chr(ord(digit) - ord(self.font[0]) + ord('0'))
        return digit

    def __init__(self, font_name: str, font: str):
        super(DigitFont, self).__init__(font_name)
        self.font = font

    def d(self):
        return dict(
            font_id=self.font_id,
            font_name=self.font_name,
            font=self.font,
        )

    def d_base(self):
        return dict(
            font_id=self.font_id,
            font_name=self.font_name,
        )

    def translate(self, sentence: str):
        return ''.join(list(map(self.get_font_letter, sentence)))
