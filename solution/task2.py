def play():

    try:
        word_input = input("Введите слова через пробел: ").lower().split()
        words = [word for word in word_input if word.isalpha()]

        if not words:
            print("Введены некорректные данные, или нет ни одного слова.")
            return []

        errors = []
        used_words = set()
        last_char = ''

        for i, word in enumerate(words):
            if i == 0:
                used_words.add(word)
                last_char = word[-1]
                continue

            if word in used_words or not word[0] == last_char:
                errors.append(i + 1)
            elif len(words) > 1:
                used_words.add(word)
                last_char = word[-1]

        return errors

    except Exception as e:
        print(f"Ошибка ввода: {e}")
        return []


if __name__ == "__main__":
    errors = play()
    if errors:
        print("Список номеров слов с ошибками:", errors)
    else:
        print("Игра пройдена без ошибок.")