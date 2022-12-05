"""
Module handling the compilation unit
"""
import uuid
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Set

from crytic_compile.compiler.compiler import CompilerVersion
from crytic_compile.source_unit import SourceUnit
from crytic_compile.utils.naming import Filename

# Cycle dependency
if TYPE_CHECKING:
    from crytic_compile import CryticCompile

# pylint: disable=too-many-instance-attributes
class CompilationUnit:
    """CompilationUnit class"""

    def __init__(self, crytic_compile: "CryticCompile", unique_id: str):
        """Init the object

        Args:
            crytic_compile (CryticCompile): Associated CryticCompile object
            unique_id (str): Unique ID used to identify the compilation unit
        """

        # mapping from filename to contract name
        self._filename_to_contracts: Dict[Filename, Set[str]] = defaultdict(set)

        # mapping from filename to source unit
        self._source_units: Dict[Filename, SourceUnit] = {}

        # set containing all the filenames of this compilation unit
        self._filenames: Set[Filename] = set()

        # compiler.compiler
        self._compiler_version: CompilerVersion = CompilerVersion(
            compiler="N/A", version="N/A", optimized=False
        )

        self._crytic_compile: "CryticCompile" = crytic_compile

        if unique_id == ".":
            unique_id = str(uuid.uuid4())

        crytic_compile.compilation_units[unique_id] = self  # type: ignore

        self._unique_id = unique_id

    @property
    def unique_id(self) -> str:
        """Return the compilation unit ID

        Returns:
            str: Compilation unit unique ID
        """
        return self._unique_id

    @property
    def crytic_compile(self) -> "CryticCompile":
        """Return the CryticCompile object

        Returns:
            CryticCompile: Associated CryticCompile object
        """
        return self._crytic_compile

    @property
    def source_units(self) -> Dict[Filename, SourceUnit]:
        """
        Return the dict of the source units
        Returns:
            Dict[Filename, SourceUnit]: the source units
        """
        return self._source_units

    def source_unit(self, filename: Filename) -> SourceUnit:
        """
        Return the source unit associated to the filename.
        The source unit must have been created by create_source_units

        Args:
            filename: filename of the source unit

        Returns:
            SourceUnit: the source unit
        """
        return self._source_units[filename]

    @property
    def asts(self) -> Dict[str, Dict]:
        """
        Return all the asts from the compilation unit
        Returns:
            Dict[str, Dict]: absolute path -> ast
        """
        return {
            source_unit.filename.absolute: source_unit.ast
            for source_unit in self.source_units.values()
        }

    def create_source_units(self, filename: Filename) -> SourceUnit:
        """
        Create the source unit associated with the filename
        Add the relevant info in the compilation unit/crytic compile
        If the source unit already exist, return it

        Args:
            filename Filename: filename of the source unit

        Returns:
            SourceUnit: the source unit
        """
        if not filename in self._source_units:
            source_unit = SourceUnit(self, filename)  # type: ignore
            self.filenames.add(filename)
            self.crytic_compile.filenames.add(filename)
            self._source_units[filename] = source_unit
        return self._source_units[filename]

    # endregion
    ###################################################################################
    ###################################################################################
    # region Filenames
    ###################################################################################
    ###################################################################################

    @property
    def filenames(self) -> Set[Filename]:
        """Return the filenames used by the compilation unit

        Returns:
            Set[Filename]: Filenames used by the compilation units
        """
        return self._filenames

    @filenames.setter
    def filenames(self, all_filenames: Set[Filename]) -> None:
        """Set the filenames

        Args:
            all_filenames (Set[Filename]): new filenames
        """
        self._filenames = all_filenames

    @property
    def filename_to_contracts(self) -> Dict[Filename, Set[str]]:
        """Return a dict mapping the filename to a list of contract declared

        Returns:
            Dict[Filename, List[str]]: Filename -> List[contract_name]
        """
        return self._filename_to_contracts

    def find_absolute_filename_from_used_filename(self, used_filename: str) -> str:
        """Return the absolute filename based on the used one

        Args:
            used_filename (str): Used filename

        Raises:
            ValueError: If the filename is not found

        Returns:
            str: Absolute filename
        """
        # Note: we could memoize this function if the third party end up using it heavily
        # If used_filename is already an absolute pathn no need to lookup
        if used_filename in self._crytic_compile.filenames:
            return used_filename
        d_file = {f.used: f.absolute for f in self._filenames}
        if used_filename not in d_file:
            raise ValueError("f{filename} does not exist in {d}")
        return d_file[used_filename]

    def relative_filename_from_absolute_filename(self, absolute_filename: str) -> str:
        """Return the relative file based on the absolute name

        Args:
            absolute_filename (str): Absolute filename

        Raises:
            ValueError: If the filename is not found

        Returns:
            str: Absolute filename
        """
        d_file = {f.absolute: f.relative for f in self._filenames}
        if absolute_filename not in d_file:
            raise ValueError("f{absolute_filename} does not exist in {d}")
        return d_file[absolute_filename]

    # endregion
    ###################################################################################
    ###################################################################################
    # region Compiler information
    ###################################################################################
    ###################################################################################

    @property
    def compiler_version(self) -> "CompilerVersion":
        """Return the compiler info

        Returns:
            CompilerVersion: compiler info
        """
        return self._compiler_version

    @compiler_version.setter
    def compiler_version(self, compiler: CompilerVersion) -> None:
        """Set the compiler version

        Args:
            compiler (CompilerVersion): New compiler version
        """
        self._compiler_version = compiler

    # endregion
    ###################################################################################
    ###################################################################################
