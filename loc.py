import csv

all = []
with open("data.csv", mode="r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)
        sanitized_row = ",".join(row)
        print(type(sanitized_row))
        all.append(sanitized_row)
    print(all)