def luhn_algorithm_validation(card_number_digits):
    digits = [int(x) for x in card_number_digits[::-1]]
    doubled_digits = [(2 * digit) if i % 2 else digit for i, digit in enumerate(digits)]
    subtracted_digits = [(digit - 9) if digit > 9 else digit for digit in doubled_digits]
    total = sum(subtracted_digits)
    return total % 10 == 0