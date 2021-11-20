cython3 --embed -o main.c main.py
gcc -Os -I /usr/include/python3.9  main.c -lpython3.9 -o main

