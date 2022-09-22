from omtool.core.tasks import DataType


def extract_action(data: DataType, keep_old: bool = True, **kwargs):
    result: DataType = {}

    for target, source in kwargs.items():
        source_path = source.split(".")
        res = data[source_path[0]]

        for attr in source_path[1:]:
            res = getattr(res, attr)

        result[target] = res

    if keep_old:
        result.update(data)

    return result
