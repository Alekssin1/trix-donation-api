def get_errors_as_string(serializer):
    return "\n".join(
        [el.title() for values in serializer.errors.values() for el in values]
    )