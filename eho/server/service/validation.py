def validate_cluster_create(values):
    #Reguired fields checks
    check_required_field(values, 'name')
    check_required_field(values, 'base_image_id')
    check_required_field(values, 'tenant_id')
    check_required_field(values, 'templates')

    #Non empty fields checking
    check_not_empty_fields(values)
    check_not_empty_fields(values['templates'])


def check_required_field(values, field):
    if field not in values:
        raise RequiredFieldException(field)


def check_not_empty_fields(values):
    for val in values:
        if not is_not_null(values[val]):
            raise EmptyFieldException(val)


def is_not_null(value):
    return value is not None and len(value) > 0


class RequiredFieldException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Field %s is required" % self.value)


class EmptyFieldException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Field %s should not be empty" % self.value)
