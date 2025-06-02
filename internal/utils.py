def calculate_polynomial_hash(string, base=31):
    hash_value = 0
    p_base = len(string) + base
    for i, char in enumerate(string):
        char_value = ord(char)
        position_factor = i + 1
        hash_value += char_value * position_factor * p_base + char_value
        hash_value = (hash_value << 5) + hash_value + char_value
    return hash_value
