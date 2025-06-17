# Catpocalypse

A survival defense shooter game inspired by "The Last Stand" where you defend against waves of cat enemies.

## Game Description

In Catpocalypse, you play as a survivor in a world overrun by mutant cats. Your goal is to survive as many waves as possible by shooting the approaching cat enemies before they destroy your defensive wall.

## Game Features

- Wave-based survival gameplay
- Shooting mechanics with reloading system
- Defensive wall that stretches vertically across the screen
- Player movement behind the wall
- Three different enemy types with unique characteristics
- Enemies that get stuck at the wall and attack it
- Increasing difficulty with each wave
- Score tracking and kill counting
- Power-up system with various effects
- Visual effects and animations
- Sound effects for game actions
- Difficulty settings
- Pause menu and settings menu

## Enemy Types

- **Normal Enemy (Red)**: Medium speed, medium health (3 hits to kill)
- **Fast Enemy (Orange)**: High speed, low health (2 hits to kill)
- **Tank Enemy (Purple)**: Low speed, high health (5 hits to kill)

## Power-up Types

- **Health (Red)**: Restores 25 health points to the player
- **Ammo (Blue)**: Instantly refills player's ammo
- **Speed (Green)**: Increases player movement speed for 5 seconds
- **Damage (Orange)**: Doubles bullet damage for 5 seconds
- **Wall Repair (Brown)**: Repairs the wall by 25 health points

## Controls

- **WASD or Arrow Keys**: Move player
- **Mouse Movement**: Aim
- **Left Mouse Button**: Shoot
- **R Key**: Reload weapon
- **P or ESC Key**: Pause game
- **Enter Key**: Start game/Continue

## Game Mechanics

- You are positioned behind a defensive wall
- Enemies approach from the left side of the screen
- Enemies cannot pass through the wall - they get stuck and attack it
- The wall has health points that vary based on difficulty
- Each enemy attack reduces the wall's health
- The game ends when the wall is destroyed
- Survive as many waves as possible to achieve a high score
- Enemies have a chance to drop power-ups when defeated

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed
2. Install Pygame: `pip install pygame`
3. Run the game: `python game_enhanced.py`

## Game Tips

- Move around to get better shooting angles
- Prioritize fast enemies as they can reach your wall quickly
- Focus on tank enemies once they reach the wall as they take more hits to kill
- Don't forget to reload when you have a moment of safety
- Collect power-ups to gain temporary advantages
- Wall repair power-ups are especially valuable in later waves
- Try different difficulty settings for varied gameplay experiences

## Credits

Created by Lance using Pygame
Inspired by "The Last Stand" game

## Version History

- v1.0: Basic game with wall defense and enemy waves
- v2.0: Added power-ups, animations, sound effects, and difficulty settings
