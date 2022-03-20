def concat(*word, separator=''):
    """An efficient method to concatenate MANY strings.

    Returns:
        str: A concatenated string from strings.
    """
    return f'{separator}'.join(list(word))
