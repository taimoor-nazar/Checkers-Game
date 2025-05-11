# Checkers-Game
Created a 10 x 10 checkers game using python's pygame module for my Artificial Intelligence course project. Applied minimax with alpha beta pruning and used evaluation function to calculate moves.

Features:
1) 10x10 Checkers 
2) AI opponent with intelligent move decisions
3) King promotion with special crown visual
4) Turn indicator and visual move hints
5) Game over screen with winner display
6) Custom evaluation function for better AI strategy

Requirements:
1) Python 3.7+
2) Pygame
Install Pygame using pip:
pip install pygame

How to Run:
python main.py

AI Logic:
The game includes an AI opponent that uses a smart decision-making process called Minimax with alpha-beta pruning. This helps the AI pick the best move by looking ahead at possible future moves.

The AI decides based on:
1) How many pieces each player has
2) How many kings each player has
3) Controlling the center of the board
4) How far the pieces have moved forward
5) How many move options are available

Game Rules:
1) Red goes first
2) Normal pieces move diagonally and capture opponents
3) Kings can move and capture in both directions
4) Multiple jumps allowed (and required when possible)
5) Game ends when a player has no moves or no pieces
   
   [Project Proposal.pdf](https://github.com/user-attachments/files/20149827/Project.Proposal.pdf)
   [AI project report.pdf](https://github.com/user-attachments/files/20149833/AI.project.report.pdf)
   


