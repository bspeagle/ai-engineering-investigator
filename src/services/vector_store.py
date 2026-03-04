from typing import List, Dict
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.code_collection = self._get_or_create_collection("code_files")
        self.issues_collection = self._get_or_create_collection("historical_issues")
    
    def _get_or_create_collection(self, name: str):
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(name)
    
    def index_code_files(self, code_files: List[Dict[str, str]], project_id: str):
        if not code_files:
            logger.warning("No code files to index")
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for i, file_data in enumerate(code_files):
            file_path = file_data['path']
            content = file_data['content']
            
            documents.append(content)
            metadatas.append({
                'path': file_path,
                'project_id': str(project_id),
                'size_kb': file_data.get('size_kb', 0)
            })
            ids.append(f"{project_id}_{file_path}_{i}")
        
        try:
            self.code_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} code files for project {project_id}")
        except Exception as e:
            logger.error(f"Error indexing code files: {e}")
    
    def search_relevant_code(self, query: str, project_id: str, n_results: int = None) -> List[Dict]:
        if n_results is None:
            n_results = settings.max_context_files
        
        try:
            results = self.code_collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"project_id": str(project_id)}
            )
            
            relevant_files = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    
                    if distance < (1 - settings.similarity_threshold):
                        relevant_files.append({
                            'path': metadata['path'],
                            'content': doc,
                            'similarity': 1 - distance
                        })
            
            logger.info(f"Found {len(relevant_files)} relevant code files")
            return relevant_files
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return []
    
    def index_issue(self, issue_id: str, title: str, description: str, project_id: str):
        combined_text = f"{title}\n\n{description}"
        
        try:
            self.issues_collection.upsert(
                documents=[combined_text],
                metadatas=[{
                    'issue_id': str(issue_id),
                    'project_id': str(project_id),
                    'title': title
                }],
                ids=[f"{project_id}_{issue_id}"]
            )
            logger.info(f"Indexed issue #{issue_id}")
        except Exception as e:
            logger.error(f"Error indexing issue: {e}")
    
    def search_similar_issues(self, query: str, project_id: str, n_results: int = None) -> List[Dict]:
        if n_results is None:
            n_results = settings.max_historical_issues
        
        try:
            results = self.issues_collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"project_id": str(project_id)}
            )
            
            similar_issues = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    
                    if distance < (1 - settings.similarity_threshold):
                        similar_issues.append({
                            'issue_id': metadata['issue_id'],
                            'title': metadata['title'],
                            'similarity': 1 - distance
                        })
            
            logger.info(f"Found {len(similar_issues)} similar historical issues")
            return similar_issues
        except Exception as e:
            logger.error(f"Error searching issues: {e}")
            return []
