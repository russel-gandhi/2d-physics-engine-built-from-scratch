"""2D Vector class backed by numpy for physics calculations."""
from __future__ import annotations
import math
import numpy as np


class Vec2:
    """2D vector representation with vector math operations."""

    def __init__(self, x: float | Vec2 | np.ndarray | tuple | list = 0.0, y: float | None = None) -> None:
        """Initialize a 2D vector from components, array, or another vector."""
        if y is None:
            if isinstance(x, Vec2):
                self.data = x.data.copy()
            elif isinstance(x, (np.ndarray, list, tuple)):
                arr = np.asarray(x, dtype=np.float64)
                if arr.shape != (2,):
                    raise ValueError(f"Expected array of shape (2,), got {arr.shape}")
                self.data = arr.copy()
            else:
                self.data = np.array([float(x), 0.0], dtype=np.float64)
        else:
            self.data = np.array([float(x), float(y)], dtype=np.float64)

    @property
    def x(self) -> float:
        """Get x component of vector."""
        return float(self.data[0])

    @x.setter
    def x(self, val: float) -> None:
        """Set x component of vector."""
        self.data[0] = float(val)

    @property
    def y(self) -> float:
        """Get y component of vector."""
        return float(self.data[1])

    @y.setter
    def y(self, val: float) -> None:
        """Set y component of vector."""
        self.data[1] = float(val)

    def __getitem__(self, idx: int) -> float:
        """Get component by index."""
        return float(self.data[idx])

    def __setitem__(self, idx: int, val: float) -> None:
        """Set component by index."""
        self.data[idx] = float(val)

    def __len__(self) -> int:
        """Return vector dimension (2)."""
        return 2

    def __iter__(self):
        """Iterate over vector components (x, y)."""
        yield float(self.data[0])
        yield float(self.data[1])

    def __add__(self, other: Vec2 | np.ndarray | tuple | list) -> Vec2:
        """Add two vectors."""
        if isinstance(other, Vec2):
            return Vec2(self.data + other.data)
        return Vec2(self.data + np.asarray(other, dtype=np.float64))

    def __radd__(self, other: Vec2 | np.ndarray | tuple | list) -> Vec2:
        """Right add two vectors."""
        return self.__add__(other)

    def __sub__(self, other: Vec2 | np.ndarray | tuple | list) -> Vec2:
        """Subtract vector from self."""
        if isinstance(other, Vec2):
            return Vec2(self.data - other.data)
        return Vec2(self.data - np.asarray(other, dtype=np.float64))

    def __rsub__(self, other: Vec2 | np.ndarray | tuple | list) -> Vec2:
        """Subtract self from vector."""
        if isinstance(other, Vec2):
            return Vec2(other.data - self.data)
        return Vec2(np.asarray(other, dtype=np.float64) - self.data)

    def __mul__(self, scalar: float) -> Vec2:
        """Multiply vector by a scalar."""
        return Vec2(self.data * float(scalar))

    def __rmul__(self, scalar: float) -> Vec2:
        """Right multiply vector by a scalar."""
        return Vec2(self.data * float(scalar))

    def __truediv__(self, scalar: float) -> Vec2:
        """Divide vector by a scalar."""
        return Vec2(self.data / float(scalar))

    def __neg__(self) -> Vec2:
        """Negate vector."""
        return Vec2(-self.data)

    def dot(self, other: Vec2 | np.ndarray | tuple | list) -> float:
        """Compute dot product with another vector."""
        if isinstance(other, Vec2):
            return float(np.dot(self.data, other.data))
        return float(np.dot(self.data, np.asarray(other, dtype=np.float64)))

    def cross(self, other: Vec2 | np.ndarray | tuple | list) -> float:
        """Compute 2D cross product scalar (a.x * b.y - a.y * b.x)."""
        if isinstance(other, Vec2):
            return float(self.x * other.y - self.y * other.x)
        arr = np.asarray(other, dtype=np.float64)
        return float(self.x * arr[1] - self.y * arr[0])

    def length(self) -> float:
        """Compute magnitude/length of vector."""
        return float(np.linalg.norm(self.data))

    def length_sq(self) -> float:
        """Compute squared length of vector."""
        return float(np.dot(self.data, self.data))

    def normalize(self) -> Vec2:
        """Return a unit vector in the same direction."""
        l = self.length()
        if l < 1e-12:
            return Vec2(0.0, 0.0)
        return Vec2(self.data / l)

    def rotate(self, angle: float) -> Vec2:
        """Rotate vector counter-clockwise by angle in radians."""
        c, s = math.cos(angle), math.sin(angle)
        x_new = c * self.x - s * self.y
        y_new = s * self.x + c * self.y
        return Vec2(x_new, y_new)

    def copy(self) -> Vec2:
        """Return a copy of the vector."""
        return Vec2(self.data.copy())

    def __repr__(self) -> str:
        """String representation of vector."""
        return f"Vec2({self.x:.4f}, {self.y:.4f})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another vector or array within numerical tolerance."""
        if isinstance(other, Vec2):
            return bool(np.allclose(self.data, other.data, atol=1e-9))
        if isinstance(other, (np.ndarray, tuple, list)):
            return bool(np.allclose(self.data, np.asarray(other, dtype=np.float64), atol=1e-9))
        return False
