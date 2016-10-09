Carrom_rl
=========
A Carrom Simulator testbed for artificial intelligence .

[![Gitter](https://badges.gitter.im/Carrom_rl/Lobby.svg)](https://gitter.im/Carrom_rl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=body_badge)

## Introduction

This is the 0.1 release of Carrom_rl - A Carrom Simulator, which provides an interface, that allows you to design agents that play single player, and two player carrom. This was built as a course project for [CS 747 - Foundations of Intelligent and Learning Agents](https://www.cse.iitb.ac.in/~shivaram/teaching/cs747-a2016/index.html), taught by Prof. Shivaram Kalyanakrishnan.

Feedback/suggestions/bug reports are welcome, please contact me at:

## Carrom

Whoever plays first, or breaks, is always white. The object of the game is to sink all of your pieces, using the heavier 'striker', in any of the pockets before your opponent. Your turn continues as long as you keep sinking your pieces - luck shots count and all combinations are permitted.


### Why Carrom? 

It is a challenging domain in the artificial intelligence context:

- The state space  is continious
- The action space is continious, with added noise
- The agent must adhere to the rules of carrom
- In the two player case, the agent must plan a strategy against an adversary, making it a multi agent system

Also, Carrom is uniquely Indian!

## Rules
Rules are slightly tweaked in the interest of making the domain suitable for learning? For a full list: go to. The specific rules which are implemented are as follows:

### 1 Player Server
The goal of the 1 Player server is to clear the board as fast as possible.

### 2 Player Server

## Quick Start

## Sample Agents

## What to submit?

## To Do


Samiran

- Fix Theta 
- Handle exceptions on closing the connection
- Add Gitter
- Save Visualization to a file
- Running experiments in parallel
- An improved agent
- Refactoring and cleaning up code
- Ensuring that it runs on SL-2 Machines

## License

[![GNU GPL v3.0](http://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl.html)
