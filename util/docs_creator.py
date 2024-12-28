from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
import pickle
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents',
]
OWNER_EMAIL = os.getenv('OWNER_EMAIL')  # C

def get_credentials():
    """Get valid user credentials from storage or user."""
    creds = None
    token_path = os.path.join('util', 'token.pickle')
    
    if(os.path.exists(token_path)):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if(not creds or not creds.valid):
        if(creds and creds.expired and creds.refresh_token):
            creds.refresh(Request())
        else:
            creds_path = os.path.join('util', 'credentials.json')
            if(not os.path.exists(creds_path)):
                raise FileNotFoundError(
                    "Missing credentials.json - please place your OAuth credentials in util/credentials.json"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_docs_from_chapters(chapters_dir='chapters'):
    """Create Google Docs from chapter files and return their links."""
    if(not OWNER_EMAIL):
        raise ValueError("OWNER_EMAIL not set in environment variables")
        
    try:
        creds = get_credentials()
    except Exception as e:
        print(f"Error getting credentials: {str(e)}")
        return {}
        
    service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    chapter_links = {}
    
    chapter_files = sorted([f for f in os.listdir(chapters_dir) 
                          if f.endswith('.txt') and not f == 'chapter_list.txt'])
    
    for chapter_file in chapter_files:
        try:
            with open(os.path.join(chapters_dir, chapter_file), 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"Creating doc for {chapter_file}...")
            
            doc = service.documents().create(
                body={'title': chapter_file[:-4]}  # Remove .txt extension
            ).execute()
            
            service.documents().batchUpdate(
                documentId=doc['documentId'],
                body={
                    'requests': [{
                        'insertText': {
                            'location': {'index': 1},
                            'text': content
                        }
                    }]
                }
            ).execute()

            drive_service.permissions().create(
                fileId=doc['documentId'],
                body={
                    'type': 'user',
                    'role': 'owner',
                    'emailAddress': OWNER_EMAIL
                },
                transferOwnership=True
            ).execute()
            
            doc_link = f"https://docs.google.com/document/d/{doc['documentId']}/edit"
            chapter_links[chapter_file] = doc_link
            print(f"Created: {doc_link}")
            
        except Exception as e:
            print(f"Error processing {chapter_file}: {str(e)}")
            continue
    
    if(chapter_links):
        with open(os.path.join(chapters_dir, 'chapter_links.json'), 'w') as f:
            json.dump(chapter_links, f, indent=2)
    
    return chapter_links

if(__name__ == "__main__"):
    links = create_docs_from_chapters()
    if(links):
        print("\nCreated documents with links:")
        for chapter, link in links.items():
            print(f"{chapter}: {link}")
    else:
        print("\nNo documents were created")
