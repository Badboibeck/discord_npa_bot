import unicodedata


def to_string(c):
    digit = f"{ord(c):x}"
    name = unicodedata.name(c, "Name not found.")
    return f"`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"
