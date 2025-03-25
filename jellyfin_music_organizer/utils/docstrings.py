from typing import TypeVar, Type, get_type_hints
import inspect

T = TypeVar('T')

def document_class(cls: Type[T]) -> Type[T]:
    """Class decorator to validate and enhance docstrings."""
    
    # Validate class docstring
    if not cls.__doc__:
        raise ValueError(f"Missing docstring for class {cls.__name__}")

    # Validate method docstrings
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):  # Skip private methods
            if not method.__doc__:
                raise ValueError(
                    f"Missing docstring for method {cls.__name__}.{name}"
                )

    return cls

def validate_docstrings() -> None:
    """Validate docstrings across the codebase."""
    import jellyfin_music_organizer
    
    def validate_module(module: Any) -> None:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                document_class(obj)
            elif inspect.isfunction(obj):
                if not obj.__doc__:
                    raise ValueError(
                        f"Missing docstring for function {module.__name__}.{name}"
                    )

    # Validate all modules
    for module in jellyfin_music_organizer.__all__:
        validate_module(module) 