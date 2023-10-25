import os

def count_lines_with_time_interval(file_path, interval_seconds):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    count = 0
    for line in lines:
        parts = line.split('\t')
        if len(parts) == 5:
            interval = float(parts[-1])
            if interval == interval_seconds:
                count += 1
    return count

def main():
    centris_dir = 'res'
    intervals = {
        '0.0': 0,
        '15552000.0': 0,  # 6 months in seconds
        '31536000.0': 0,  # 1 year in seconds
        '63072000.0': 0,  # 2 years in seconds
    }
    total_0 = 0
    total_6 = 0
    total_12 = 0
    total_24 = 0
    total_36 = 0
    total_36plus = 0
    total_lines = 0

    for dir_path in [centris_dir]:
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    total_lines += len(lines)
                    for line in lines:
                        parts = line.split('\t')
                        interval = float(parts[-1])
                        if interval == 0.0:
                            total_0 += 1
                        elif 0.0 < interval <= 15552000.0:
                            total_6 += 1
                        elif 15552000.0 < interval <= 31536000.0:
                            total_12 += 1
                        elif 31536000.0 < interval <= 63072000.0:
                            total_24 += 1
                        elif 63072000.0 < interval <= 94608000.0:
                            total_36 += 1
                        elif 94608000.0 < interval:
                            total_36plus += 1
                        else:
                            print(interval)


    print(f"Total lines in all files: {total_lines}")

    print(total_0,total_6,total_12,total_24,total_36,total_36plus)

if __name__ == "__main__":
    main()
