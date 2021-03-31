import sys

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} gridFile")
        return
    
    fileName = sys.argv[1]
    
    with open(fileName, "r") as f:
        lines = [ line.strip() for line in f.readlines() ]

        for x in range(len(lines)):
            for y in range(len(lines[x])):
                if lines[x][y] == 'X':
                    print(f"{x},{y}")
            
    
main()