import sys
from pathlib import Path

root = Path(__file__).parent.parent
sys.path.append(str(root))

from src.client.client import Client

if __name__ == "__main__":
    app = Client(root / "test")
    app.start()