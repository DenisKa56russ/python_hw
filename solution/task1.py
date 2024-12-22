def pull_def(n: int) -> tuple[int, int]:
    four_star_count = 0
    five_star_count = 0
    for i in range(1, n + 1):
        if i % 90 == 0:
            five_star_count += 1
            four_star_count+=1
        elif i % 10 == 0:
            four_star_count += 1

    return (four_star_count, five_star_count)
if __name__ == "__main__":
    try:
        n = int(input("Введите количество круток: "))
        if n < 0:
            print("Количество круток не может быть отрицательным.")
        else:
            four_star, five_star = pull_def(n)
            print(f"Минимальное количество 4* персонажей: {four_star}")
            print(f"Минимальное количество 5* персонажей: {five_star}")
    except ValueError:
        print("Некорректный ввод. Пожалуйста, введите целое число.")