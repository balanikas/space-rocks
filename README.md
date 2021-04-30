

# 2D arcade-style game in Python

This game is based on this tutorial https://realpython.com/asteroids-game-python/ 
and expanded into a more feature filled game 

## Running

* $ pip install -r requirements.txt
* $ python main.py

## Demo
youtube

## Features

### level editor
A level is any subfolder in the folder "levels" and a level is defined in a file called ".json"
### hot reload
Any change in a level subfolder will reload the current level. 
This is done to make the game testing loop faster.

### resizable window
### animations
Animations are based on sprite sheets. ".json" in the "anim" folder
defines properties for each animation


## Controls

* Left/A: rotate left  
* Right/D: rotate right  
* Up/A: accelerate  
* Space: fire   
* 1: switch between primary and secondary weapon
* Q: show debug info
* 7: start previous level
* 8: restart current level
* 9: start next level

## Future improvements:
* GUI for level editor
* improve performance, make the most out of the pygame apis (link)
* pixel perfect collision detection
* autogenerated levels


## Dependencies	
see [requirements.txt](requirements.txt)

## Contribution

Feel free to contribute in any way