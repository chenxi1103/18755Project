## Sybil Attack and Defense Analysis on Social Media Networks

18755 project 
Team 9

### Activate
```
pip install requests
pip install networkx
pip install community
pip install matplotlib.pyplot
```

### Krama Network
- Node: Karma Points 
- Edges: Directed from post to its comments or comment to its sub-comments 

``
run python3 karma_network.py
``

### User Network

- Node: Reddit User

- Edges: Users who comment on the same parent nodes are connected indirectly

1. Numbered
2. List

### Filter honest users and generate fake accounts

```
run  python3 sybil_attack.py
```
### Attack

```
run python3 user_network.py attack

```

### Partition Defense
```
run python3 user_network.py partition
```

### Pruning Defense
```angular2
run python3 user_network.py pruning
```

### Practical Implementation
```
run python3 user_network.py practical
```
