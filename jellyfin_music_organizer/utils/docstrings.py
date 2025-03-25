"""Utilities for docstring validation and processing."""

import inspect
import logging
from typing import Any, Callable, Dict, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Add TypeVar definition


def validate_docstring(func: Callable[..., Any]) -> None:
    """
    Validate that a function has proper docstring documentation.

    Args:
        func: The function to validate

    Raises:
        ValueError: If docstring is missing or invalid
    """
    docstring = inspect.getdoc(func)

    if not docstring:
        raise ValueError(f"Missing docstring for function {func.__name__}")

    # Check for empty docstring
    if not docstring.strip():
        raise ValueError(f"Empty docstring for function {func.__name__}")

    # Check for description
    lines = docstring.split("\n")
    if len(lines) < 1:
        raise ValueError(f"Missing description in docstring for {func.__name__}")

    # Check for Args section if function has parameters
    sig = inspect.signature(func)
    if sig.parameters and "Args:" not in docstring:
        raise ValueError(f"Missing Args section in docstring for {func.__name__}")

    # Check for Returns section if function returns something
    if sig.return_annotation != inspect.Signature.empty and "Returns:" not in docstring:
        raise ValueError(f"Missing Returns section in docstring for {func.__name__}")


def extract_docstring_sections(docstring: str) -> Dict[str, str]:
    """
    Extract sections from a docstring.

    Args:
        docstring: The docstring to process

    Returns:
        Dict mapping section names to their content
    """
    sections: Dict[str, str] = {}
    current_section = "description"
    current_content: list[str] = []

    for line in docstring.split("\n"):
        line = line.strip()

        # Check for section headers
        if line.endswith(":") and not line.startswith(" "):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[:-1].lower()
            current_content = []
        else:
            current_content.append(line)

    # Add the last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def format_docstring(sections: Dict[str, str]) -> str:
    """
    Format docstring sections into a proper docstring.

    Args:
        sections: Dictionary of section names and content

    Returns:
        Formatted docstring
    """
    parts = []

    # Add description
    if "description" in sections:
        parts.append(sections["description"])
        parts.append("")

    # Add Args section
    if "args" in sections:
        parts.append("Args:")
        parts.append(f"    {sections['args']}")
        parts.append("")

    # Add Returns section
    if "returns" in sections:
        parts.append("Returns:")
        parts.append(f"    {sections['returns']}")
        parts.append("")

    # Add Raises section
    if "raises" in sections:
        parts.append("Raises:")
        parts.append(f"    {sections['raises']}")

    return "\n".join(parts).strip()


def document_class(cls: Type[T]) -> Type[T]:
    """Class decorator to validate and enhance docstrings."""

    # Validate class docstring
    if not cls.__doc__:
        raise ValueError(f"Missing docstring for class {cls.__name__}")

    # Validate method docstrings
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith("_"):  # Skip private methods
            if not method.__doc__:
                raise ValueError(f"Missing docstring for method {cls.__name__}.{name}")

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
                    raise ValueError(f"Missing docstring for function {module.__name__}.{name}")

    # Validate all modules
    for module in jellyfin_music_organizer.__all__:
        validate_module(module)
