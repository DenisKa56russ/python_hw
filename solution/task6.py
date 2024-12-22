import re


def serialize(data: list[dict[str, int | str]], path: str):

    with open(path, 'w') as f:
        for record in data:
            serialized_record = []
            for key, value in record.items():
                if isinstance(value, str):
                    serialized_record.append(f'{key}: "{value}"')
                else:
                    serialized_record.append(f'{key}: {value}')
            f.write(', '.join(serialized_record) + '\n')


def deserialize(path: str) -> list[dict[str, int | str]]:

    result = []
    with open(path, 'r') as f:
        for line in f:
            record = {}
            line = line.strip()
            if not line:
                continue
            pairs = re.split(r'\s*,\s*', line)
            for pair in pairs:
                key, value = pair.split(':', 1)
                key = key.strip()
                value = value.strip()

                if value.startswith('"') and value.endswith('"'):
                    record[key] = value[1:-1]
                else:
                    try:
                        record[key] = int(value)
                    except ValueError:
                        record[key] = value
            result.append(record)
    return result

