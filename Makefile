all: bchoc

bchoc:
	cp bchoc.py bchoc
	chmod +x bchoc

clean:
	rm -rf pycache
	rm bchoc
	rm *.bin
	rm *.txt