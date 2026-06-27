import logging
from typing import List, Optional
from dataclasses import dataclass
import tree_sitter_python
import tree_sitter_java
from tree_sitter import Language, Parser

logger = logging.getLogger(__name__)

# Load languages
PYTHON_LANGUAGE = Language(tree_sitter_python.language())
JAVA_LANGUAGE = Language(tree_sitter_java.language())

@dataclass
class CodeChunk:
    file_path: str
    start_line: int
    end_line: int
    content: str
    node_type: str  # e.g., 'function_definition', 'method_declaration'

class ASTChunker:
    """
    A chunker that uses Tree-sitter to extract logical blocks of code
    (functions, classes, methods) across multiple languages like Python and Java.
    """
    
    def __init__(self):
        pass

    def get_logical_chunks(self, file_path: str, source_code: str, modified_lines: Optional[List[int]] = None) -> List[CodeChunk]:
        """
        Parses the source code into an AST and extracts logical chunks that intersect with the modified lines.
        """
        parser = Parser()
        
        if file_path.endswith('.py'):
            parser.language = PYTHON_LANGUAGE
            target_node_types = {'function_definition', 'class_definition'}
        elif file_path.endswith('.java'):
            parser.language = JAVA_LANGUAGE
            target_node_types = {'method_declaration', 'class_declaration', 'constructor_declaration'}
        else:
            # Fallback for unsupported languages
            return [CodeChunk(file_path, 1, len(source_code.splitlines()), source_code, 'Unknown')]

        tree = parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node

        chunks = []
        source_lines = source_code.splitlines()

        # Traverse the tree to find target nodes
        def traverse(node):
            if node.type in target_node_types:
                start_line = node.start_point.row + 1
                end_line = node.end_point.row + 1
                
                # Check if this node overlaps with modified lines (if provided)
                if modified_lines:
                    if not any(start_line <= line <= end_line for line in modified_lines):
                        # Even if this parent node doesn't match, check children (like nested classes)
                        for child in node.children:
                            traverse(child)
                        return
                        
                chunk_content = "\n".join(source_lines[start_line - 1:end_line])
                chunks.append(CodeChunk(
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    content=chunk_content,
                    node_type=node.type
                ))
            else:
                for child in node.children:
                    traverse(child)

        traverse(root_node)

        # If no specific functions/classes match, fallback to the entire file
        if not chunks:
             chunks.append(CodeChunk(
                 file_path=file_path,
                 start_line=1,
                 end_line=len(source_lines),
                 content=source_code,
                 node_type='Module'
             ))

        return chunks
