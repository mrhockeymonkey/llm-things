from typing import List, Dict, Any
from pydantic import BaseModel
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, TransformComponent, Node, TextNode
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
import uuid

class RAGChunk(BaseModel):
    id_: str
    text: str
    metadata: Dict[str, Any] = {}

class RawTextChunkingStratedgy:
    def __init__(self, size: int, overlap: int):
        self.size = size
        self.overlap = overlap
        self.splitter = SentenceSplitter(chunk_size=size, chunk_overlap=overlap)

    def process(self, text: str, metadata: Dict | None = None) -> List[RAGChunk]:
        metadata = metadata if metadata else {'source': 'raw_text'}
        
        document: Document = Document(text=text, metadata=metadata)
        
        nodes: List[BaseNode] = self.splitter.get_nodes_from_documents([document])
        
        unique_id: str = str(uuid.uuid4())
        
        # Convert to RAGChunk objects
        chunks: List[RAGChunk] = []

        for i, node in enumerate(nodes):
            rag_chunk: RAGChunk = RAGChunk(
                id_=node.node_id or f"text_chunk_{i}_{unique_id}",
                text=node.text,
                metadata={ **node.metadata, **metadata }
            )

            chunks.append(rag_chunk)
        
        return chunks
    
class MarkDownDirectoryChunkingStratedgy:
    def __init__(self, input_dir: str, size: int, overlap: int):
        self.input_dir = input_dir
        self.size = size
        self.overlap = overlap
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self) -> IngestionPipeline:
        return IngestionPipeline(transformations=[
            SentenceSplitter(chunk_size=self.size, chunk_overlap=self.overlap)
        ])

    def load_documents(self) -> List[Document]:
        # If you're using a different type of file besides md, you'll want to change this. 
        return SimpleDirectoryReader(
            input_dir=self.input_dir, 
            recursive=True,
            required_exts=['.md']
        ).load_data()
    
    def to_ragchunks(self, nodes: List[TextNode]) -> List[RAGChunk]:
        return [
            RAGChunk(
                id_=node.node_id,
                text=node.text,
                metadata={
                    **node.metadata
                }
            )
            for node in nodes
        ]
    
    def process(self) -> List[RAGChunk]:
        documents: List[Document] = self.load_documents()
        nodes: List[TextNode] = self.pipeline.run(documents=documents) # type: ignore
        chunks: List[RAGChunk]  = self.to_ragchunks(nodes) # type: ignore
        return chunks