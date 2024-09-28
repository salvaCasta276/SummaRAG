from os import DirectoryLoader, TextLoader

class DocumentLoader:
    def __init__(self):
        # Reads custom data from local file
        self.loader = DirectoryLoader(path="docs", glob="*.txt", loader_cls=TextLoader)  # Loader class to use for loading files

    def load(self, path):
        return self.loader.load(path)  # Load the document from the path

def main():
    loader = DocumentLoader()
    document = loader.load("example.txt")
    print(document)