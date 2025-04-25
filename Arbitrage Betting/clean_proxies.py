def clean_google_passed_proxies(input_file="proxy-list-raw.txt", output_file="http_proxies.txt"):
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            parts = line.strip().split()
            if len(parts) > 1 and parts[-1] == '+':
                ip_port = parts[0]
                outfile.write(f"{ip_port}\n")

if __name__ == "__main__":
    clean_google_passed_proxies()