from smartify import E


@E.register(id_processor=E.idp_cls_prefix())
class ParserError:
    TRANSFER = E("以转义字符结尾")
    EMPTY = E("空的参数名")
    QUOTE = E("引号不匹配")
    QUOTE_AROUND = E("引号不在子串两端")


class Parser:
    @staticmethod
    def split(command):
        command = command + ' '
        splits = []
        index = 0
        split_start = 0
        quote = None

        while index < len(command):
            if command[index] == ' ':
                if not quote:
                    split = command[split_start: index]
                    if split:
                        splits.append(split)
                    split_start = index + 1
            elif command[index] == '\\':
                if index + 1 == len(command):
                    raise ParserError.TRANSFER
                else:
                    index += 1
            elif command[index] in '"\'':
                if quote:
                    quote = None
                    split = command[split_start: index+1]
                    splits.append(split)
                    split_start = index + 1
                else:
                    quote = command[index]

            index += 1

        if quote:
            raise ParserError.QUOTE

        return splits

    @staticmethod
    def find_all(s: str, c: str):
        index_list = []
        index = s.find(c)
        while index != -1:
            index_list.append(index)
            index = s.find(c, index + 1)
        return index_list

    @classmethod
    def remove_quote(cls, s: str):
        if not s:
            return s

        if s[-1] in '"\'':
            if s[0] != s[-1]:
                raise ParserError.QUOTE_AROUND
            return bytes(s[1:-1], "utf-8").decode("unicode_escape")

        quote_indexes = cls.find_all(s, '"')
        quote_indexes.extend(cls.find_all(s, "'"))

        for quote_index in quote_indexes:
            if s[quote_index - 1] != '\\':
                raise ParserError.QUOTE_AROUND

        return s

    @classmethod
    def combine(cls, splits: list):
        combines = []

        index = 0
        while index < len(splits):
            split = splits[index]  # type: str
            if split.startswith('--'):  # long
                split = split[2:]
                if not split:
                    raise ParserError.EMPTY
                if '=' in split:
                    key, value = split.split('=', maxsplit=2)
                else:
                    key, value = split, None
                combines.append((key, value))
            elif split.startswith('-'):  # short
                split = split[1:]
                if not split:
                    raise ParserError.EMPTY

                key, value = split[0], split[1:]
                if len(split) == 1:
                    if index < len(splits) - 1 and not splits[index+1].startswith('-'):
                        key, value = split, splits[index+1]
                        index += 1
                combines.append((key, value))
            else:
                combines.append(split)

            index += 1

        for index in range(len(combines)):
            if isinstance(combines[index], tuple):
                combines[index] = (cls.remove_quote(combines[index][0]),
                                   cls.remove_quote(combines[index][1]))
            else:
                combines[index] = cls.remove_quote(combines[index])

        return combines

    @classmethod
    def parse(cls, command=None):
        splits = cls.split(command)
        combines = cls.combine(splits)
        kwargs = {}
        args = []

        for combine in combines:
            if isinstance(combine, tuple):
                kwargs[combine[0]] = combine[1]
            else:
                args.append(combine)
