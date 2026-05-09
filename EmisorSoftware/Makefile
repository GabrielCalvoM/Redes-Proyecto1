# Variables
## Compilacion
CC			:= g++
PROGRAM		:= app.exe
SRC			:= $(wildcard ./*.cpp)
OBJ			:= $(patsubst ./%.cpp, ./bin/%.o, $(SRC))

## Directorios
APP-RED		:= CapaAplicacionRed
ENLACE		:= CapaEnlace
INTERFAZ	:= InterfazRedEnlace

INCLUDE 	:= -I$(APP-RED) -I$(ENLACE) -I$(INTERFAZ)
LIBS		:= 

# Comandos
all: $(PROGRAM)

$(PROGRAM): $(OBJ) | build
	$(CC) $(OBJ) $(LIBS) $(INCLUDE) -o ./build/$(PROGRAM)

./bin/%.o: ./%.cpp | bin
	$(CC) -c $< $(LIBS) -o $@

bin build:
	$(shell mkdir -p $@)

clean:
	rm -f $(PROGRAM) $(OBJ)