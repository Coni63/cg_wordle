run:
	poetry run python script.py

profile:
	poetry run python -m cProfile -o profile.txt -s cumtime -e 'main' -m script

stats:
	gprof2dot -f pstats profile.txt | dot -Tpng -o profile.png
	poetry run python stats.py