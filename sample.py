import dotenv

import sample_prep
from wiz import server

sample_prep.prep()
dotenv.load_dotenv()
server.start()
