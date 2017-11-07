def logout(socket, token):
    socket.emit("logout", {"tp-session-token": token})
    return socket.get_received()
