from chat_foldre import app, socketio
import os
from socketio.server import SocketIOServer
#socketio.run(app)
port = int(os.environ.get('PORT', 5000))
SocketIOServer(('',port),app,resource="socket.io").serve_forever()