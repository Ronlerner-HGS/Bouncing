# FOR IMPROVED GAME GO to [See README2.md](README2.md)


# Object Bounce Simulation

This project is a simple **object bounce simulation game** built using **Pygame**. The goal of the project was to demonstrate the use of **mutable lists** in Python by allowing users to spawn multiple bouncing objects that persist and interact in real-time.

## Project Overview
- **You start with a menu screen** that lets you choose different objects to spawn (Square, Circle, Triangle).
- Each object has random movement and color, and bounces off the walls.
- The objects are stored in a **mutable list** (`objects[]`), allowing the game to dynamically add new objects as the user chooses.
- You can keep opening the menu by pressing **M** and adding more objects.

## Purpose of the Project
The primary goal of this project was to explore **mutable lists in Python**. Mutable lists allow you to:
- **Dynamically add objects** to the game by appending them to the list (`objects.append()`).
- Continuously update and draw each object from the list (`for obj in objects`).
- Easily manipulate the list by adding, removing, or modifying objects.

This is a practical example of **list mutability** since the list grows or shrinks based on user input.

## How It Works
### Menu System
- When you start the game, you see a menu with options to spawn objects:
  - **Press 1** to spawn a Square.
  - **Press 2** to spawn a Circle.
  - **Press 3** to spawn a Triangle.
- The chosen object is appended to the `objects[]` list.
- You can press **M** at any time to open the menu again and add more objects.

### Object Behavior
- Each object has random movement speed and random colors.
- When objects hit the wall, they change color and bounce back.
- The game loop continuously iterates through the `objects[]` list and updates/draws each object.

## Source Documentation
The project is built using **Pygame** and basic Python structures.
Here are the primary resources referenced:
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Pygame object Documentation](https://www.pygame.org/docs/tut/tom_games4.html?highlight=dx)
- [Python List Documentation](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)

## Key Code Sections
### Mutable List Usage
The most important part of the project is how the `objects[]` list works:
```python
objects = []

# Append new objects
objects.append(MovingObject('square'))

# Continuously update objects
for obj in objects:
    obj.update()
    obj.draw(screen)
```
This demonstrates **list mutability** because the list can grow, shrink, or modify based on user input.

### Menu Interaction
The menu uses key events to append objects to the list:
```python
if event.key == pygame.K_1:
    objects.append(MovingObject('square'))
```

## Future Improvements
- **Object Deletion**: Allow users to click objects to delete them from the list.
- **Collision Destruction**: If two objects collide, one gets destroyed (removed from the list).
- **Object Counter**: Display the current number of objects in the game.

## Running the Project
1. Make sure Python 3 and Pygame are installed.
2. Run the Python file:
```bash
python game.py
```
3. Follow on-screen instructions to add objects.
