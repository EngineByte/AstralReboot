from __future__ import annotations

from dataclasses import dataclass


ENTITY_INDEX_BITS = 32
GENERATION_BITS = 32

ENTITY_INDEX_MASK = (1 << ENTITY_INDEX_BITS) - 1
GENERATION_MASK = (1 << GENERATION_BITS) - 1

MAX_ENTITY_INDEX = ENTITY_INDEX_MASK
MAX_GENERATION = GENERATION_MASK


@dataclass(frozen=True, slots=True)
class EntityHandle:
    '''
    Utility class for packing and unpacking ECS entity identifiers.

    An entity in this ECS is represented externally as a single integer (`eid`)
    that encodes two pieces of information:

        - index: the slot into ECS storage arrays
        - generation: a version number used to detect stale references

    Layout of packed entity ID (64-bit):

        [ generation (high 32 bits) | index (low 32 bits) ]

    ------------------------------------------------------------------------
    Design goals:
    ------------------------------------------------------------------------

    - Compact representation (single integer)
    - Fast extraction of index for array access
    - Generation-based safety against stale handles
    - Compatible with dense storage ECS patterns

    ------------------------------------------------------------------------
    Usage:
    ------------------------------------------------------------------------

    Create packed ID:

        eid = EntityHandle.pack(index=5, generation=2)

    Unpack:

        index, generation = EntityHandle.unpack(eid)

    Extract parts directly:

        index = EntityHandle.get_index(eid)
        generation = EntityHandle.get_generation(eid)

    Optional object form:

        handle = EntityHandle.make(index, generation)
        eid = int(handle)
    '''

    index: int
    generation: int

    def __post_init__(self) -> None:
        '''
        Validate index and generation bounds.
        '''
        if self.index < 0:
            raise ValueError(f'Entity index must be non-negative, got {self.index}')

        if self.generation < 0:
            raise ValueError(
                f'Entity generation must be non-negative, got {self.generation}'
            )

        if self.index > MAX_ENTITY_INDEX:
            raise ValueError(
                f'Entity index {self.index} exceeds {ENTITY_INDEX_BITS}-bit limit '
                f'({MAX_ENTITY_INDEX})'
            )

        if self.generation > MAX_GENERATION:
            raise ValueError(
                f'Entity generation {self.generation} exceeds {GENERATION_BITS}-bit limit '
                f'({MAX_GENERATION})'
            )

    @property
    def id(self) -> int:
        '''
        Alias for index (useful for compatibility with APIs expecting `.id`).
        '''
        return self.index

    @property
    def gen(self) -> int:
        '''
        Alias for generation.
        '''
        return self.generation

    def to_int(self) -> int:
        '''
        Pack this handle into a single integer.

        Returns:
            int: Packed entity ID.
        '''
        return (self.generation << ENTITY_INDEX_BITS) | self.index

    def __int__(self) -> int:
        '''
        Allow implicit conversion to packed integer.
        '''
        return self.to_int()

    @classmethod
    def pack(cls, index: int, generation: int) -> int:
        '''
        Pack raw entity parts into a single integer.

        Args:
            index (int): Entity storage index.
            generation (int): Generation/version.

        Returns:
            int: Packed entity ID.

        Raises:
            ValueError: If values are out of bounds.
        '''
        if index < 0:
            raise ValueError(f'Entity index must be non-negative, got {index}')

        if generation < 0:
            raise ValueError(f'Entity generation must be non-negative, got {generation}')

        if index > MAX_ENTITY_INDEX:
            raise ValueError(
                f'Entity index {index} exceeds {ENTITY_INDEX_BITS}-bit limit '
                f'({MAX_ENTITY_INDEX})'
            )

        if generation > MAX_GENERATION:
            raise ValueError(
                f'Entity generation {generation} exceeds {GENERATION_BITS}-bit limit '
                f'({MAX_GENERATION})'
            )

        return (generation << ENTITY_INDEX_BITS) | index

    @classmethod
    def unpack(cls, eid: int) -> tuple[int, int]:
        '''
        Unpack a packed entity ID into its components.

        Args:
            eid (int): Packed entity ID.

        Returns:
            tuple[int, int]:
                (index, generation)

        Raises:
            ValueError: If eid is negative.
        '''
        if eid < 0:
            raise ValueError(f'Packed entity id must be non-negative, got {eid}')

        index = eid & ENTITY_INDEX_MASK
        generation = (eid >> ENTITY_INDEX_BITS) & GENERATION_MASK
        return index, generation

    @classmethod
    def get_index(cls, eid: int) -> int:
        '''
        Extract entity index from packed ID.

        Args:
            eid (int): Packed entity ID.

        Returns:
            int: Entity index.
        '''
        if eid < 0:
            raise ValueError(f'Packed entity id must be non-negative, got {eid}')
        return eid & ENTITY_INDEX_MASK

    @classmethod
    def get_generation(cls, eid: int) -> int:
        '''
        Extract generation from packed ID.

        Args:
            eid (int): Packed entity ID.

        Returns:
            int: Generation value.
        '''
        if eid < 0:
            raise ValueError(f'Packed entity id must be non-negative, got {eid}')
        return (eid >> ENTITY_INDEX_BITS) & GENERATION_MASK

    @classmethod
    def make(cls, index: int, generation: int) -> EntityHandle:
        '''
        Create an EntityHandle object from raw parts.

        Useful when working in object form instead of packed ints.
        '''
        return cls(index=index, generation=generation)

    @classmethod
    def from_int(cls, eid: int) -> EntityHandle:
        '''
        Convert a packed entity ID into an EntityHandle object.

        Args:
            eid (int): Packed entity ID.

        Returns:
            EntityHandle
        '''
        index, generation = cls.unpack(eid)
        return cls(index=index, generation=generation)

    def __iter__(self):
        '''
        Allow tuple unpacking:

            index, generation = EntityHandle.make(...)
        '''
        yield self.index
        yield self.generation

    def __repr__(self) -> str:
        return (
            f'EntityHandle(index={self.index}, '
            f'generation={self.generation}, '
            f'packed={self.to_int()})'
        )