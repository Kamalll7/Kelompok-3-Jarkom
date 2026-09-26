VOWELS = set("aeiouAEIOU")


def count_char(text):
    return len(text)


def count_word(text):
    return len(text.split())


def reverse_string(text):
    return text[::-1]


def remove_vowel(text):
    # TODO: masih pakai cara manual, belum dioptimasi
    result = ""
    for ch in text:
        if ch not in VOWELS:
            result += ch
    return result


def matrix_determinant(m):
    # TODO: baru support cara umum, belum ditest untuk semua kasus
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def matrix_inverse(m, det):
    # TODO: belum diimplementasi, nyusul
    if det == 0:
        return None
    
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]

    # matriks kofaktor, lalu invers = transpose(kofaktor) / det
    cof = [
        [e * i - f * h, -(d * i - f * g), d * h - e * g],
        [-(b * i - c * h), a * i - c * g, -(a * h - b * g)],
        [b * f - c * e, -(a * f - c * d), a * e - b * d],
    ]
    return [[round(cof[c_][r] / det, 4) for c_ in range(3)] for r in range(3)]


def matrix_det_inv(m):
    # TODO: belum menggabungkan determinant + inverse
    det = matrix_determinant(m)
    return det, matrix_inverse(m, det)