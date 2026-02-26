from __future__ import annotations
from typing import TYPE_CHECKING

from collections.abc import Sequence


class Validators:
    """
    Validation functions for checking inputs

    """

    @staticmethod
    def validate_numeric_sequence(
        seq: Sequence | None,
        name: str,
        allow_none: bool = False,
        min_value: float | None = None,
        required_length: int | None = None,
        allow_none_elements = False,
    ) -> None:
        """Validate that a sequence is non-None, numeric, and meets optional constraints.

        Raises TypeError or ValueError if the sequence is invalid.
        """
        if not allow_none and seq is None:
            raise ValueError(f"{name} cannot be None.")
        
        if seq is not None:
            if not isinstance(seq, Sequence):
                raise TypeError(f"{name} must be a tuple or list.")
            if isinstance(seq, (str, bytes)):
                raise TypeError(f"{name} must be a tuple or list.")
            if allow_none_elements:
                if not all(isinstance(val, (int, float, type(None))) for val in seq):
                    raise TypeError(f"{name} can only contain numeric values or None.")
            elif not all(isinstance(val, (int, float)) for val in seq):
                raise TypeError(f"{name} can only contain numeric values.")
            if min_value is not None and any(min_value > val for val in seq):
                raise ValueError(f"{name} cannot contain values smaller than {min_value}.")
            if required_length is not None and len(seq) != required_length:
                raise ValueError(f"{name} must be of length {required_length}.")       
            
    @staticmethod
    def validate_number(
        num: float | int | None,
        name: str,
        allow_none: bool = False,
        min_value: float | None = None,
        only_integer: bool = False,
    ) -> None:
        """Validate that a value is non-None, numeric, and meets optional constraints.

        Raises TypeError or ValueError if the value is invalid.
        """
        if not allow_none and num is None:
            raise ValueError(f"{name} cannot be None.")
        
        if num is not None:
            if min_value is not None:
                if min_value > num:
                    raise ValueError(f"{name} must be equal or larger than {min_value}.")
            if only_integer:
                if not isinstance(num, int):
                    raise TypeError(f"{name} must be an integer.")
            else:
                if not isinstance(num, (int, float)):
                    raise TypeError(f"{name} must be an integer or float.")
                
    @staticmethod
    def validate_string_sequence(
        seq: Sequence | None,
        name: str,
        allow_none: bool = False,
        required_length: int | None = None
    ) -> None:
        """Validate that a sequence is non-None, contains strings, and meets optional constraints.

        Raises TypeError or ValueError if the sequence is invalid.
        """
        if not allow_none and seq is None:
            raise ValueError(f"{name} cannot be None.")
        
        if seq is not None:
            if not isinstance(seq, Sequence):
                raise TypeError(f"{name} must be a tuple or list.")
            if isinstance(seq, (str, bytes)):
                raise TypeError(f"{name} must be a tuple or list.")
            if not all(isinstance(val, (str)) for val in seq):
                raise TypeError(f"{name} can only contain strings.")
            if required_length is not None and len(seq) != required_length:
                raise ValueError(f"{name} must be of length {required_length}.")      
    
