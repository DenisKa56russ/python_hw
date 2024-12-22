import random


def learn(dataset):


    markov_chain = {}


    for text in dataset:
        words = text.split()
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i + 1]

            if current_word not in markov_chain:
                markov_chain[current_word] = {}
            if next_word not in markov_chain[current_word]:
                markov_chain[current_word][next_word] = 0
            markov_chain[current_word][next_word] += 1

    for current_word in markov_chain:
        total_count = sum(markov_chain[current_word].values())
        if total_count > 0:
            for next_word in markov_chain[current_word]:
                markov_chain[current_word][next_word] /= total_count
    return markov_chain


def generate(state):


    if not state:
        return ""

    current_word = random.choice(list(state.keys()))
    generated_text = [current_word]

    while True:
        next_word_probabilities = state.get(current_word)
        if next_word_probabilities:
            next_word = \
            random.choices(list(next_word_probabilities.keys()), weights=list(next_word_probabilities.values()))[0]
            generated_text.append(next_word)
            current_word = next_word
        else:
            break
    return " ".join(generated_text)



dataset = []
while True:
    text_input = input("Введите текст для обучения модели (или 'done' для завершения): ")
    if text_input.lower() == 'done':
        break
    dataset.append(text_input.lower())

if len(dataset) > 0:
    state = learn(dataset)
    generated_text = generate(state)
    print("Сгенерированный текст:")
    print(generated_text)
else:
    print("Не было введено текста для обучения.")