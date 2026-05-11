def russian_plural_form(number, one, few, many):
    n = abs(int(number or 0))
    last_two = n % 100
    last = n % 10

    if 11 <= last_two <= 14:
        return many

    if last == 1:
        return one

    if 2 <= last <= 4:
        return few

    return many
