from .exceptions import InvalidInputArgumentsError


def with_arguments(*args, **defaults):
    def decorator(func):
        def wrapper(obj, **kwargs):
            missing_args = []

            for arg in args:
                if arg not in kwargs:
                    missing_args.append(arg)

            if missing_args:
                raise InvalidInputArgumentsError(
                    obj.type,
                    func.__name__,
                    missing_args
                )

            for k, v in defaults.iteritems():
                if k not in kwargs:
                    kwargs[k] = v

            obj.log(
                'info',
                'Operation "{0}" started with input parameters: {1}',
                func.__name__,
                kwargs
            )

            result = func(obj, **kwargs)

            obj.log(
                'info',
                'Operation "{0}" ended successfully {1}',
                func.__name__,
                'with result: {0}'.format(result) if result else ''
            )

            return result

        return wrapper

    return decorator
