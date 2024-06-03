"""from VideoServer import VideoServer

my_socket = VideoServer("10.0.0.16",9999)
my_socket.main()"""

"""from ChatServer import ChatServer
server = ChatServer("10.0.0.16",9999,"9/11")
server.main()"""
"""from Server import Server
server = Server("10.0.0.16","9/11",9999,9990,9995)
server.main()"""
from AudioServer import AudioServer
server = AudioServer("10.0.0.16",9999)
server.main()
