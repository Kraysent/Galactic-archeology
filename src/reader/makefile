unsio_path = ../../deps/unsio

all: reader compile

clean:
	rm -rf *.o result

reader: reader.cpp
	g++ -c -I${unsio_path}/inc/ -L${unsio_path}/lib/ reader.cpp -lunsio

compile: reader.o
	g++ -o result reader.o -I${unsio}/inc/ -L${unsio_path}/lib/ -lunsio

