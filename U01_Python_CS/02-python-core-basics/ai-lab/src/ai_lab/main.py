from ai_lab.helper.python_core import flatten


def main() -> None:
    output = flatten([1, [2, 3], 4])
    print(output)


if __name__ == "__main__":
    main()
