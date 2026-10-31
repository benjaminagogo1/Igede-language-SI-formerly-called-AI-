import pathlib
import pgserver

server = pgserver.get_server(pathlib.Path("pgdata"), cleanup_mode=None) #type: ignore[assignment]
print(server.get_uri())