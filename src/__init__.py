from dotenv import load_dotenv
load_dotenv()

from src.utils import *
embedder = Embedder()
data = Data()
twitch = Twitch(os.environ['TWITCH_CLIENT_ID'], os.environ['TWITCH_SECRET'])

from src.cogs import *
