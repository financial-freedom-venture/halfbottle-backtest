class Singleton(type):
    _instance = None

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

    def Instance(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
