"""
XML-based repository implementation for Todo persistence.

This module provides a concrete implementation of the TodoRepository
interface using XML files for data storage with lxml. It handles XML
serialization, deserialization, and file I/O operations while maintaining
the domain contract.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from lxml import etree

from src.domain.models import TodoItem
from src.domain.exceptions import TodoNotFoundError, TodoDomainError
from src.infrastructure.persistence.repository import TodoRepository


class XMLTodoRepository(TodoRepository):
    """
    XML file-based implementation of TodoRepository using lxml.

    This repository stores todo items in an XML file, providing persistent
    storage with structured format. It handles XML serialization of
    complex types like UUID and datetime objects using lxml for parsing
    and generation.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the XML repository with a file path.

        Args:
            file_path: Path to the XML file for data storage

        Raises:
            TodoDomainError: If the file path is invalid or inaccessible
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """
        Ensure the XML file exists and is properly initialized.

        Creates an empty XML document with root element if the file doesn't exist.

        Raises:
            TodoDomainError: If file creation fails
        """
        try:
            if not self.file_path.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                self._create_empty_xml()
            elif self.file_path.stat().st_size == 0:
                # Handle empty file
                self._create_empty_xml()
        except (OSError, IOError) as e:
            raise TodoDomainError(f"Failed to initialize XML file: {e}") from e

    def _create_empty_xml(self) -> None:
        """
        Create an empty XML file with root element.

        Raises:
            TodoDomainError: If XML creation fails
        """
        try:
            root = etree.Element("todos")
            tree = etree.ElementTree(root)
            tree.write(
                str(self.file_path),
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True
            )
        except (OSError, IOError) as e:
            raise TodoDomainError(f"Failed to create XML file: {e}") from e

    def _load_xml_tree(self) -> etree._ElementTree:
        """
        Load XML tree from file.

        Returns:
            XML ElementTree

        Raises:
            TodoDomainError: If file reading or XML parsing fails
        """
        try:
            return etree.parse(str(self.file_path))
        except (OSError, IOError) as e:
            raise TodoDomainError(f"Failed to read XML file: {e}") from e
        except etree.XMLSyntaxError as e:
            raise TodoDomainError(f"Invalid XML format: {e}") from e

    def _save_xml_tree(self, tree: etree._ElementTree) -> None:
        """
        Save XML tree to file.

        Args:
            tree: XML ElementTree to save

        Raises:
            TodoDomainError: If file writing fails
        """
        try:
            tree.write(
                str(self.file_path),
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True
            )
        except (OSError, IOError) as e:
            raise TodoDomainError(f"Failed to write XML file: {e}") from e

    def _todo_to_xml_element(self, todo: TodoItem) -> etree._Element:
        """
        Convert TodoItem to XML element.

        Args:
            todo: TodoItem to convert

        Returns:
            XML element representation of the todo
        """
        todo_elem = etree.Element("todo")
        
        # Add required fields
        etree.SubElement(todo_elem, "id").text = str(todo.id)
        etree.SubElement(todo_elem, "title").text = todo.title
        etree.SubElement(todo_elem, "completed").text = str(todo.completed).lower()
        etree.SubElement(todo_elem, "created_at").text = todo.created_at.isoformat()
        etree.SubElement(todo_elem, "updated_at").text = todo.updated_at.isoformat()
        
        # Add optional fields
        if todo.description is not None:
            etree.SubElement(todo_elem, "description").text = todo.description
        
        if todo.due_date is not None:
            etree.SubElement(todo_elem, "due_date").text = todo.due_date.isoformat()
        
        return todo_elem

    def _xml_element_to_todo(self, todo_elem: etree._Element) -> TodoItem:
        """
        Convert XML element to TodoItem.

        Args:
            todo_elem: XML element representation of todo

        Returns:
            TodoItem instance

        Raises:
            TodoDomainError: If data conversion fails
        """
        try:
            # Extract required fields
            id_elem = todo_elem.find("id")
            title_elem = todo_elem.find("title")
            completed_elem = todo_elem.find("completed")
            created_at_elem = todo_elem.find("created_at")
            updated_at_elem = todo_elem.find("updated_at")
            
            if any(elem is None for elem in [id_elem, title_elem, completed_elem, created_at_elem, updated_at_elem]):
                raise ValueError("Missing required XML elements")
            
            # Extract optional fields
            description_elem = todo_elem.find("description")
            due_date_elem = todo_elem.find("due_date")
            
            return TodoItem(
                id=UUID(id_elem.text),
                title=title_elem.text,
                description=description_elem.text if description_elem is not None else None,
                due_date=datetime.fromisoformat(due_date_elem.text) if due_date_elem is not None else None,
                completed=completed_elem.text.lower() == "true",
                created_at=datetime.fromisoformat(created_at_elem.text),
                updated_at=datetime.fromisoformat(updated_at_elem.text)
            )
        except (ValueError, TypeError, AttributeError) as e:
            raise TodoDomainError(f"Failed to convert XML element to TodoItem: {e}") from e

    def _find_todo_element_by_id(self, root: etree._Element, todo_id: UUID) -> Optional[etree._Element]:
        """
        Find todo XML element by ID.

        Args:
            root: Root XML element
            todo_id: UUID of the todo to find

        Returns:
            XML element if found, None otherwise
        """
        for todo_elem in root.findall("todo"):
            id_elem = todo_elem.find("id")
            if id_elem is not None and id_elem.text == str(todo_id):
                return todo_elem
        return None

    def save(self, todo: TodoItem) -> None:
        """
        Save a todo item to the XML repository.

        This method handles both create and update scenarios by checking
        if the todo already exists and replacing it if found.

        Args:
            todo: The TodoItem to save

        Raises:
            TodoDomainError: If the save operation fails
        """
        tree = self._load_xml_tree()
        root = tree.getroot()
        
        # Find existing todo element by ID and replace, or append if new
        existing_elem = self._find_todo_element_by_id(root, todo.id)
        new_elem = self._todo_to_xml_element(todo)
        
        if existing_elem is not None:
            # Replace existing element
            parent = existing_elem.getparent()
            parent.replace(existing_elem, new_elem)
        else:
            # Append new element
            root.append(new_elem)
        
        self._save_xml_tree(tree)

    def find_by_id(self, todo_id: UUID) -> Optional[TodoItem]:
        """
        Find a todo item by its unique identifier.

        Args:
            todo_id: The unique identifier of the todo item

        Returns:
            The TodoItem if found, None otherwise

        Raises:
            TodoDomainError: If the find operation fails
        """
        tree = self._load_xml_tree()
        root = tree.getroot()
        
        todo_elem = self._find_todo_element_by_id(root, todo_id)
        if todo_elem is not None:
            return self._xml_element_to_todo(todo_elem)
        
        return None

    def find_all(self) -> List[TodoItem]:
        """
        Retrieve all todo items from the repository.

        Returns:
            A list of all TodoItem instances, empty list if none exist

        Raises:
            TodoDomainError: If the retrieval operation fails
        """
        tree = self._load_xml_tree()
        root = tree.getroot()
        
        todos = []
        for todo_elem in root.findall("todo"):
            todos.append(self._xml_element_to_todo(todo_elem))
        
        return todos

    def update(self, todo: TodoItem) -> None:
        """
        Update an existing todo item in the repository.

        Args:
            todo: The TodoItem with updated information

        Raises:
            TodoNotFoundError: If the todo item doesn't exist
            TodoDomainError: If the update operation fails
        """
        tree = self._load_xml_tree()
        root = tree.getroot()
        
        existing_elem = self._find_todo_element_by_id(root, todo.id)
        if existing_elem is None:
            raise TodoNotFoundError(f"Todo with ID {todo.id} not found")
        
        # Replace existing element with updated one
        new_elem = self._todo_to_xml_element(todo)
        parent = existing_elem.getparent()
        parent.replace(existing_elem, new_elem)
        
        self._save_xml_tree(tree)

    def delete(self, todo_id: UUID) -> None:
        """
        Delete a todo item from the repository.

        Args:
            todo_id: The unique identifier of the todo item to delete

        Raises:
            TodoNotFoundError: If the todo item doesn't exist
            TodoDomainError: If the delete operation fails
        """
        tree = self._load_xml_tree()
        root = tree.getroot()
        
        todo_elem = self._find_todo_element_by_id(root, todo_id)
        if todo_elem is None:
            raise TodoNotFoundError(f"Todo with ID {todo_id} not found")
        
        # Remove element from parent
        parent = todo_elem.getparent()
        parent.remove(todo_elem)
        
        self._save_xml_tree(tree)

    def exists(self, todo_id: UUID) -> bool:
        """
        Check if a todo item exists in the repository.

        Args:
            todo_id: The unique identifier of the todo item

        Returns:
            True if the todo item exists, False otherwise

        Raises:
            TodoDomainError: If the existence check fails
        """
        tree = self._load_xml_tree()
        root = tree.getroot()
        
        return self._find_todo_element_by_id(root, todo_id) is not None