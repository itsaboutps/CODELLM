"""
Advanced Text Chunker - Intelligent text splitting for optimal RAG performance

Implements multiple chunking strategies including semantic, recursive character,
and sentence-based splitting with overlap for context preservation.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChunkType(Enum):
    """Types of text chunks for different content."""
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    SEMANTIC = "semantic"
    CODE = "code"
    TABLE = "table"

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    content: str
    start_index: int
    end_index: int
    chunk_id: str
    content_type: ChunkType
    metadata: Dict[str, Any]

class AdvancedTextChunker:
    """
    Advanced text chunking with multiple strategies:
    1. Semantic chunking based on content structure
    2. Recursive character splitting with smart boundaries
    3. Sentence-aware splitting
    4. Overlap preservation for context continuity
    """
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 min_chunk_size: int = 100):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum chunk size to avoid tiny fragments
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Sentence boundary patterns
        self.sentence_endings = re.compile(r'[.!?]+[\s\n]')
        self.paragraph_separator = re.compile(r'\n\s*\n')
        
        # Code detection patterns
        self.code_patterns = [
            re.compile(r'```[\s\S]*?```'),  # Markdown code blocks
            re.compile(r'def\s+\w+\(.*?\):'),  # Python functions
            re.compile(r'class\s+\w+.*?:'),  # Python classes
            re.compile(r'function\s+\w+\(.*?\)'),  # JavaScript functions
            re.compile(r'<[^>]+>'),  # HTML tags
        ]
        
        # Table detection patterns
        self.table_patterns = [
            re.compile(r'\|.*\|.*\|'),  # Markdown tables
            re.compile(r'\t.*\t.*\t'),  # Tab-separated values
        ]
        
        logger.info(f"Text chunker initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_text(self, text: str, document_name: str = "unknown") -> List[TextChunk]:
        """
        Split text into chunks using the best strategy based on content.
        
        Args:
            text: Input text to chunk
            document_name: Name of source document for metadata
            
        Returns:
            List of TextChunk objects
        """
        if not text or len(text) < self.min_chunk_size:
            return []
        
        try:
            # First, identify different content types in the text
            content_regions = self._identify_content_regions(text)
            
            # Chunk each region using appropriate strategy
            all_chunks = []
            for region in content_regions:
                region_chunks = self._chunk_region(region, document_name)
                all_chunks.extend(region_chunks)
            
            # If no regions identified, use default chunking
            if not all_chunks:
                all_chunks = self._recursive_character_split(text, document_name)
            
            # Post-process chunks
            final_chunks = self._post_process_chunks(all_chunks)
            
            logger.info(f"Created {len(final_chunks)} chunks from {len(text)} characters")
            return final_chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            # Fallback to simple splitting
            return self._simple_split(text, document_name)
    
    def _identify_content_regions(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify different content regions in the text.
        
        Args:
            text: Input text
            
        Returns:
            List of content regions with type and boundaries
        """
        regions = []
        
        # Find code blocks
        for pattern in self.code_patterns:
            for match in pattern.finditer(text):
                regions.append({
                    'type': ChunkType.CODE,
                    'start': match.start(),
                    'end': match.end(),
                    'content': match.group()
                })
        
        # Find tables
        lines = text.split('\n')
        current_table = []
        table_start = None
        
        for i, line in enumerate(lines):
            if any(pattern.search(line) for pattern in self.table_patterns):
                if table_start is None:
                    table_start = text.find(line)
                current_table.append(line)
            else:
                if current_table:
                    # End of table
                    table_content = '\n'.join(current_table)
                    table_end = table_start + len(table_content)
                    regions.append({
                        'type': ChunkType.TABLE,
                        'start': table_start,
                        'end': table_end,
                        'content': table_content
                    })
                    current_table = []
                    table_start = None
        
        # Handle remaining table
        if current_table:
            table_content = '\n'.join(current_table)
            table_end = table_start + len(table_content)
            regions.append({
                'type': ChunkType.TABLE,
                'start': table_start,
                'end': table_end,
                'content': table_content
            })
        
        # Sort regions by start position and merge overlapping ones
        regions.sort(key=lambda x: x['start'])
        
        # Fill gaps with regular text regions
        filled_regions = []
        last_end = 0
        
        for region in regions:
            # Add text region before special region
            if region['start'] > last_end:
                filled_regions.append({
                    'type': ChunkType.PARAGRAPH,
                    'start': last_end,
                    'end': region['start'],
                    'content': text[last_end:region['start']]
                })
            
            filled_regions.append(region)
            last_end = region['end']
        
        # Add final text region
        if last_end < len(text):
            filled_regions.append({
                'type': ChunkType.PARAGRAPH,
                'start': last_end,
                'end': len(text),
                'content': text[last_end:]
            })
        
        return filled_regions
    
    def _chunk_region(self, region: Dict[str, Any], document_name: str) -> List[TextChunk]:
        """
        Chunk a specific content region using appropriate strategy.
        
        Args:
            region: Content region with type and boundaries
            document_name: Source document name
            
        Returns:
            List of TextChunk objects
        """
        content = region['content'].strip()
        if not content or len(content) < self.min_chunk_size:
            return []
        
        chunk_type = region['type']
        start_offset = region['start']
        
        if chunk_type == ChunkType.CODE:
            return self._chunk_code(content, start_offset, document_name)
        elif chunk_type == ChunkType.TABLE:
            return self._chunk_table(content, start_offset, document_name)
        else:
            return self._chunk_paragraph(content, start_offset, document_name)
    
    def _chunk_code(self, content: str, start_offset: int, document_name: str) -> List[TextChunk]:
        """Chunk code content preserving structure."""
        # For code, prefer to keep logical blocks together
        if len(content) <= self.chunk_size:
            return [TextChunk(
                content=content,
                start_index=start_offset,
                end_index=start_offset + len(content),
                chunk_id=f"{document_name}_code_0",
                content_type=ChunkType.CODE,
                metadata={"document": document_name}
            )]
        
        # Split by lines but try to keep functions/classes together
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_idx = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > self.chunk_size and current_chunk:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunk_start = start_offset + content.find(current_chunk[0])
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_index=chunk_start,
                    end_index=chunk_start + len(chunk_content),
                    chunk_id=f"{document_name}_code_{chunk_idx}",
                    content_type=ChunkType.CODE,
                    metadata={"document": document_name}
                ))
                
                current_chunk = [line]
                current_size = line_size
                chunk_idx += 1
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk_start = start_offset + content.rfind(current_chunk[0])
            chunks.append(TextChunk(
                content=chunk_content,
                start_index=chunk_start,
                end_index=chunk_start + len(chunk_content),
                chunk_id=f"{document_name}_code_{chunk_idx}",
                content_type=ChunkType.CODE,
                metadata={"document": document_name}
            ))
        
        return chunks
    
    def _chunk_table(self, content: str, start_offset: int, document_name: str) -> List[TextChunk]:
        """Chunk table content preserving structure."""
        # Tables should generally be kept together if possible
        if len(content) <= self.chunk_size * 1.5:  # Allow tables to be slightly larger
            return [TextChunk(
                content=content,
                start_index=start_offset,
                end_index=start_offset + len(content),
                chunk_id=f"{document_name}_table_0",
                content_type=ChunkType.TABLE,
                metadata={"document": document_name}
            )]
        
        # Split large tables by rows
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_idx = 0
        
        # Keep header row if it exists
        header_row = None
        if lines and any(pattern.search(lines[0]) for pattern in self.table_patterns):
            header_row = lines[0]
        
        for line in lines:
            line_size = len(line) + 1
            
            if current_size + line_size > self.chunk_size and current_chunk:
                # Add header to each chunk if exists
                chunk_lines = [header_row] + current_chunk if header_row and current_chunk[0] != header_row else current_chunk
                chunk_content = '\n'.join(chunk_lines)
                chunk_start = start_offset + content.find(current_chunk[0])
                
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_index=chunk_start,
                    end_index=chunk_start + len(chunk_content),
                    chunk_id=f"{document_name}_table_{chunk_idx}",
                    content_type=ChunkType.TABLE,
                    metadata={"document": document_name}
                ))
                
                current_chunk = [line]
                current_size = line_size
                chunk_idx += 1
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunk_lines = [header_row] + current_chunk if header_row and current_chunk[0] != header_row else current_chunk
            chunk_content = '\n'.join(chunk_lines)
            chunk_start = start_offset + content.rfind(current_chunk[0])
            
            chunks.append(TextChunk(
                content=chunk_content,
                start_index=chunk_start,
                end_index=chunk_start + len(chunk_content),
                chunk_id=f"{document_name}_table_{chunk_idx}",
                content_type=ChunkType.TABLE,
                metadata={"document": document_name}
            ))
        
        return chunks
    
    def _chunk_paragraph(self, content: str, start_offset: int, document_name: str) -> List[TextChunk]:
        """Chunk paragraph content using semantic and sentence boundaries."""
        # Split by paragraphs first
        paragraphs = self.paragraph_separator.split(content)
        
        chunks = []
        chunk_idx = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph or len(paragraph) < self.min_chunk_size:
                continue
            
            # If paragraph fits in chunk size, keep it as one chunk
            if len(paragraph) <= self.chunk_size:
                para_start = start_offset + content.find(paragraph)
                chunks.append(TextChunk(
                    content=paragraph,
                    start_index=para_start,
                    end_index=para_start + len(paragraph),
                    chunk_id=f"{document_name}_para_{chunk_idx}",
                    content_type=ChunkType.PARAGRAPH,
                    metadata={"document": document_name}
                ))
                chunk_idx += 1
            else:
                # Split large paragraph by sentences
                para_chunks = self._split_by_sentences(paragraph, start_offset + content.find(paragraph), document_name, chunk_idx)
                chunks.extend(para_chunks)
                chunk_idx += len(para_chunks)
        
        return chunks
    
    def _split_by_sentences(self, text: str, start_offset: int, document_name: str, start_idx: int) -> List[TextChunk]:
        """Split text by sentences while respecting chunk size limits."""
        sentences = self.sentence_endings.split(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_idx = start_idx
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Create chunk with overlap
                chunk_content = ' '.join(current_chunk)
                chunk_start = start_offset + text.find(current_chunk[0])
                
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_index=chunk_start,
                    end_index=chunk_start + len(chunk_content),
                    chunk_id=f"{document_name}_sent_{chunk_idx}",
                    content_type=ChunkType.SENTENCE,
                    metadata={"document": document_name}
                ))
                
                # Start new chunk with overlap
                overlap_text = chunk_content[-self.chunk_overlap:] if len(chunk_content) > self.chunk_overlap else chunk_content
                current_chunk = [overlap_text, sentence] if overlap_text != sentence else [sentence]
                current_size = len(' '.join(current_chunk))
                chunk_idx += 1
            else:
                current_chunk.append(sentence)
                current_size += sentence_size + 1  # +1 for space
        
        # Add final chunk
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk_start = start_offset + text.rfind(current_chunk[-1])
            
            chunks.append(TextChunk(
                content=chunk_content,
                start_index=chunk_start,
                end_index=chunk_start + len(chunk_content),
                chunk_id=f"{document_name}_sent_{chunk_idx}",
                content_type=ChunkType.SENTENCE,
                metadata={"document": document_name}
            ))
        
        return chunks
    
    def _recursive_character_split(self, text: str, document_name: str) -> List[TextChunk]:
        """Fallback recursive character splitting with smart boundaries."""
        chunks = []
        chunk_idx = 0
        
        # Split points in order of preference
        split_chars = ['\n\n', '\n', '. ', ', ', ' ']
        
        def split_text(content: str, start_pos: int) -> List[TextChunk]:
            if len(content) <= self.chunk_size:
                return [TextChunk(
                    content=content,
                    start_index=start_pos,
                    end_index=start_pos + len(content),
                    chunk_id=f"{document_name}_{chunk_idx}",
                    content_type=ChunkType.PARAGRAPH,
                    metadata={"document": document_name}
                )]
            
            # Find best split point
            best_split = self.chunk_size
            for split_char in split_chars:
                split_pos = content.rfind(split_char, 0, self.chunk_size)
                if split_pos > self.min_chunk_size:
                    best_split = split_pos + len(split_char)
                    break
            
            # Create first chunk
            first_chunk = content[:best_split]
            first_chunk_obj = TextChunk(
                content=first_chunk,
                start_index=start_pos,
                end_index=start_pos + len(first_chunk),
                chunk_id=f"{document_name}_{chunk_idx}",
                content_type=ChunkType.PARAGRAPH,
                metadata={"document": document_name}
            )
            
            # Create overlap for next chunk
            overlap_start = max(0, best_split - self.chunk_overlap)
            remaining_content = content[overlap_start:]
            
            return [first_chunk_obj] + split_text(remaining_content, start_pos + overlap_start)
        
        return split_text(text, 0)
    
    def _simple_split(self, text: str, document_name: str) -> List[TextChunk]:
        """Simple fallback splitting method."""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_content = text[i:i + self.chunk_size]
            if len(chunk_content) >= self.min_chunk_size:
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_index=i,
                    end_index=i + len(chunk_content),
                    chunk_id=f"{document_name}_simple_{len(chunks)}",
                    content_type=ChunkType.PARAGRAPH,
                    metadata={"document": document_name}
                ))
        return chunks
    
    def _post_process_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """Post-process chunks to ensure quality and consistency."""
        if not chunks:
            return []
        
        processed_chunks = []
        
        for chunk in chunks:
            # Skip chunks that are too small
            if len(chunk.content.strip()) < self.min_chunk_size:
                continue
            
            # Clean up content
            cleaned_content = chunk.content.strip()
            
            # Update chunk with cleaned content
            processed_chunk = TextChunk(
                content=cleaned_content,
                start_index=chunk.start_index,
                end_index=chunk.start_index + len(cleaned_content),
                chunk_id=chunk.chunk_id,
                content_type=chunk.content_type,
                metadata=chunk.metadata
            )
            
            processed_chunks.append(processed_chunk)
        
        logger.info(f"Post-processed {len(chunks)} chunks to {len(processed_chunks)} final chunks")
        return processed_chunks