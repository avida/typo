# Typo
Typo is a command line typing trainer game with multiplayer support and continiously adjusted game difficulty. 

## Game description 
Each player has its dynamically changing [Elo
rating](https://en.wikipedia.org/wiki/Elo_rating_system). Based on this points
it finds opponent to compete with.

## Game workflow description

### Authentification

User authentification should be performed over generated private/public keys.
On start application checks if those keys exist and try to send sign in request
to server.  If there is no such keys it should be generated and send
registration request on server.  In return server should perform verification
procedure and genrerate human readable username (user should be able to change
it).  After that it can move to initialization stage.

### User initializtion
After verification completed successfully 


### Game process

After passing verification and verifying user data gaming session started.
Client should maintain persistent websocket connection during the game.

