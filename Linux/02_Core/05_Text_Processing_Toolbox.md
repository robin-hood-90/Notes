---
tags: [linux, text, core, grep, sed, awk, cut, sort, jq, regex, text-processing]
aliases: ["Text Processing", "Text Processing Toolbox", "Command-Line Text Tools"]
status: stable
updated: 2026-04-26
---

# Text Processing Toolbox

## Overview

Linux text processing tools enable inspection, extraction, transformation, and analysis of text data directly from the command line. These tools follow the Unix philosophy: do one thing well and compose via pipes.

> [!summary] Key Concepts
> - **Pipe (`|`)**: Pass output of one command as input to another
> - **Filter**: Programs that read stdin, transform, write to stdout
> - **Regular Expressions**: Pattern matching language for text
> - **Stream Processing**: Process text line-by-line without loading entire file
> - **Field Separator**: Character delimiting columns (space, comma, tab)

---

## Text Processing Philosophy

```mermaid
graph LR
    A[Raw Text File] --> B[cat/head/tail]
    B --> C[grep/rg]
    C --> D[cut/awk]
    D --> E[sort]
    E --> F[uniq]
    F --> G[wc/head/tail]
    G --> H[Final Output]
    
    style A fill:#ff9999
    style H fill:#99ff99
```

**Unix Pipeline Approach**:
```bash
# Problem: Find top 10 most common error types in logs
cat error.log | \
  grep "ERROR" | \
  awk '{print $5}' | \
  sort | \
  uniq -c | \
  sort -nr | \
  head -10
```

**Breakdown**:
1. `cat error.log` - Read file
2. `grep "ERROR"` - Keep only ERROR lines
3. `awk '{print $5}'` - Extract 5th field (error type)
4. `sort` - Sort alphabetically
5. `uniq -c` - Count unique occurrences
6. `sort -nr` - Sort numerically, reverse (highest first)
7. `head -10` - Show top 10

---

## Viewing and Inspecting

### cat (Concatenate)

```bash
# Display file contents
cat file.txt

# Concatenate multiple files
cat file1.txt file2.txt

# Number lines
cat -n file.txt

# Number non-blank lines
cat -b file.txt

# Show non-printing characters
cat -A file.txt  # Tabs as ^I, EOL as $

# Create file (here-document)
cat > newfile.txt <<EOF
Line 1
Line 2
EOF
```

### head / tail

```bash
# First 10 lines (default)
head file.txt

# First N lines
head -n 20 file.txt
head -20 file.txt

# First N bytes
head -c 100 file.txt

# Last 10 lines (default)
tail file.txt

# Last N lines
tail -n 50 file.txt
tail -50 file.txt

# Follow file (real-time updates)
tail -f /var/log/syslog

# Follow with retry (file may not exist yet)
tail -F /var/log/app.log

# Follow multiple files
tail -f /var/log/nginx/*.log

# Show last N lines and follow
tail -n 100 -f /var/log/syslog
```

### less / more

```bash
# Paginate output
less file.txt

# Search forward: /pattern
# Search backward: ?pattern
# Next occurrence: n
# Previous occurrence: N
# Quit: q

# Start at end of file
less +G file.txt

# Start at specific line
less +50 file.txt

# Follow mode (like tail -f)
less +F /var/log/syslog
# Press Ctrl+C to stop following, F to resume
```

### wc (Word Count)

```bash
# Count lines, words, characters
wc file.txt

# Count lines only
wc -l file.txt

# Count words only
wc -w file.txt

# Count characters
wc -m file.txt

# Count bytes
wc -c file.txt

# Multiple files (shows totals)
wc -l *.txt
```

---

## Searching and Filtering

### grep (Global Regular Expression Print)

```bash
# Search for pattern
grep "error" file.txt

# Case-insensitive search
grep -i "error" file.txt

# Invert match (lines NOT matching)
grep -v "debug" file.txt

# Count matching lines
grep -c "error" file.txt

# Show line numbers
grep -n "error" file.txt

# Show only matching part
grep -o "error" file.txt

# Recursive search in directory
grep -r "TODO" /path/to/code

# Search in specific file types
grep -r --include="*.py" "import" /path/to/code
grep -r --exclude="*.log" "error" /path/to/logs

# Show context (lines before/after match)
grep -C 3 "error" file.txt   # 3 lines before and after
grep -A 5 "error" file.txt   # 5 lines after
grep -B 2 "error" file.txt   # 2 lines before

# Multiple patterns (OR)
grep -E "error|warning" file.txt
grep -e "error" -e "warning" file.txt

# Extended regex (ERE)
grep -E "^[0-9]{3}-[0-9]{4}$" file.txt

# Perl-compatible regex (PCRE)
grep -P "\d{3}-\d{4}" file.txt

# Quiet mode (exit status only)
grep -q "error" file.txt && echo "Errors found"

# List files with matches
grep -l "error" *.log

# List files without matches
grep -L "error" *.log
```

### ripgrep (rg - Modern grep alternative)

```bash
# Basic search
rg "error"

# Search specific file type
rg "TODO" -t py         # Python files
rg "import" -t js       # JavaScript files

# Case-insensitive
rg -i "error"

# Smart case (case-insensitive if pattern is lowercase)
rg -S "Error"

# Show context
rg -C 3 "error"

# Search hidden files
rg --hidden "config"

# Follow symlinks
rg --follow "pattern"

# Search file names
rg --files | rg "test"

# JSON output
rg "error" --json

# Replace (preview)
rg "old" -r "new"

# Multiline search
rg -U "class.*\n.*def" -t py
```

---

## Extracting and Transforming

### cut (Extract Columns)

```bash
# Extract field by delimiter
cut -d',' -f1 data.csv           # 1st field, comma delimiter
cut -d',' -f1,3 data.csv         # 1st and 3rd fields
cut -d',' -f1-3 data.csv         # Fields 1 through 3

# Tab delimiter (default)
cut -f1 data.tsv

# Character positions
cut -c1-10 file.txt              # Characters 1-10
cut -c1,5,10 file.txt            # Characters 1, 5, 10

# Complement (everything except)
cut -d',' -f2 --complement data.csv  # All fields except 2nd

# Custom output delimiter
cut -d',' -f1,2 --output-delimiter=';' data.csv
```

### awk (Pattern Scanning and Processing)

```bash
# Print specific field
awk '{print $1}' file.txt        # 1st field (space-delimited)
awk '{print $1, $3}' file.txt    # 1st and 3rd fields

# Custom delimiter
awk -F',' '{print $1}' data.csv  # Comma delimiter
awk -F':' '{print $1}' /etc/passwd  # Colon delimiter

# Print with formatting
awk '{print "User:", $1, "ID:", $3}' data.txt

# Field separator in output
awk -F',' '{print $1 ";" $2}' data.csv

# Pattern matching
awk '/error/ {print}' file.txt   # Print lines matching "error"
awk '!/debug/ {print}' file.txt  # Print lines NOT matching "debug"

# Conditional processing
awk '$3 > 100 {print $1, $3}' data.txt  # Print if 3rd field > 100

# BEGIN and END blocks
awk 'BEGIN {print "Start"} {print $1} END {print "End"}' file.txt

# Built-in variables
awk '{print NR, $0}' file.txt    # NR = line number
awk '{print NF, $0}' file.txt    # NF = number of fields
awk 'NR==5 {print}' file.txt     # Print line 5

# Sum values
awk '{sum += $1} END {print sum}' numbers.txt

# Calculate average
awk '{sum += $1} END {print sum/NR}' numbers.txt

# Count occurrences
awk '{count[$1]++} END {for (word in count) print word, count[word]}' file.txt
```

**AWK Use Cases**:
```bash
# Extract usernames from /etc/passwd
awk -F':' '{print $1}' /etc/passwd

# Find processes using > 1GB RAM
ps aux | awk '$6 > 1000000 {print $11, $6/1024 "MB"}'

# Parse Apache access logs
awk '{print $1, $7}' access.log  # IP address and requested path

# CSV to JSON (simple)
awk -F',' '{print "{\"name\":\""$1"\",\"age\":"$2"}"}' data.csv
```

### sed (Stream Editor)

```bash
# Substitute (replace first occurrence per line)
sed 's/old/new/' file.txt

# Substitute all occurrences
sed 's/old/new/g' file.txt

# Case-insensitive substitution
sed 's/old/new/gi' file.txt

# Substitute only on lines matching pattern
sed '/error/s/old/new/g' file.txt

# Delete lines
sed '/debug/d' file.txt          # Delete lines containing "debug"
sed '5d' file.txt                # Delete line 5
sed '10,20d' file.txt            # Delete lines 10-20
sed '/^$/d' file.txt             # Delete blank lines

# Insert/append lines
sed '5i\New line here' file.txt  # Insert before line 5
sed '5a\New line here' file.txt  # Append after line 5

# Change line
sed '5c\Replacement line' file.txt

# Print specific lines
sed -n '10,20p' file.txt         # Print lines 10-20
sed -n '/error/p' file.txt       # Print lines matching "error"

# In-place editing
sed -i 's/old/new/g' file.txt    # Modify file directly
sed -i.bak 's/old/new/g' file.txt  # Create backup before editing

# Multiple commands
sed -e 's/old/new/g' -e 's/foo/bar/g' file.txt
sed 's/old/new/g; s/foo/bar/g' file.txt

# Use different delimiter
sed 's|/old/path|/new/path|g' file.txt
```

**SED Use Cases**:
```bash
# Remove comments from config file
sed '/^#/d; /^$/d' config.txt

# Extract URLs from HTML
sed -n 's/.*href="\([^"]*\)".*/\1/p' index.html

# Remove trailing whitespace
sed 's/[[:space:]]*$//' file.txt

# Convert DOS line endings to Unix
sed 's/\r$//' dosfile.txt

# Add prefix to each line
sed 's/^/PREFIX: /' file.txt
```

### tr (Translate Characters)

```bash
# Replace characters
tr 'a-z' 'A-Z' < file.txt        # Lowercase to uppercase
tr 'A-Z' 'a-z' < file.txt        # Uppercase to lowercase

# Delete characters
tr -d '0-9' < file.txt           # Delete digits
tr -d '\r' < dosfile.txt         # Remove carriage returns

# Squeeze repeats
tr -s ' ' < file.txt             # Squeeze multiple spaces to single
tr -s '\n' < file.txt            # Squeeze multiple newlines

# Complement
tr -cd '0-9\n' < file.txt        # Keep only digits and newlines

# Character classes
tr '[:lower:]' '[:upper:]' < file.txt
tr -d '[:punct:]' < file.txt     # Delete punctuation
```

---

## Sorting and Deduplication

### sort

```bash
# Alphabetical sort
sort file.txt

# Reverse sort
sort -r file.txt

# Numeric sort
sort -n numbers.txt

# Human-readable numeric sort (1K, 2M, 3G)
sort -h sizes.txt

# Sort by specific field
sort -t',' -k2 data.csv          # Sort by 2nd field, comma-delimited
sort -t',' -k2,2 data.csv        # Sort by 2nd field only

# Sort numerically by specific field
sort -t',' -k3n data.csv         # Sort numerically by 3rd field

# Case-insensitive sort
sort -f file.txt

# Unique sort (remove duplicates)
sort -u file.txt

# Sort in place
sort -o file.txt file.txt

# Check if sorted
sort -c file.txt

# Merge sorted files
sort -m sorted1.txt sorted2.txt
```

**Sort Keys**:
```bash
# Complex example: Sort by 2nd field numerically, then 3rd field alphabetically
sort -t',' -k2n -k3 data.csv

# Sort by month
sort -M months.txt  # Jan, Feb, Mar, ...
```

### uniq (Remove Duplicates)

```bash
# Remove consecutive duplicates (requires sorted input)
sort file.txt | uniq

# Count occurrences
sort file.txt | uniq -c

# Show only duplicates
sort file.txt | uniq -d

# Show only unique lines (no duplicates)
sort file.txt | uniq -u

# Ignore case
sort file.txt | uniq -i

# Compare only N characters
uniq -w 5 file.txt

# Skip N characters before comparing
uniq -s 5 file.txt
```

**Common Pattern**:
```bash
# Top 10 most common entries
sort file.txt | uniq -c | sort -nr | head -10
```

---

## Column Manipulation

### paste (Merge Lines)

```bash
# Merge files side-by-side
paste file1.txt file2.txt

# Custom delimiter
paste -d',' file1.txt file2.txt

# Transpose (columns to rows)
paste -s file.txt

# Transpose with custom delimiter
paste -sd',' file.txt
```

### column (Format into Columns)

```bash
# Automatic column formatting
column -t data.txt

# Specify delimiter
column -t -s',' data.csv

# JSON table
echo '{"a":1,"b":2}\n{"a":3,"b":4}' | column -t
```

### join (Join Files by Common Field)

```bash
# Join on 1st field (files must be sorted)
join file1.txt file2.txt

# Join on specific fields
join -1 2 -2 1 file1.txt file2.txt  # file1 field 2, file2 field 1

# Custom delimiter
join -t',' file1.csv file2.csv

# Outer join (include unmatched lines)
join -a 1 file1.txt file2.txt  # Left outer join
join -a 2 file1.txt file2.txt  # Right outer join
join -a 1 -a 2 file1.txt file2.txt  # Full outer join
```

---

## JSON Processing

### jq (JSON Query Language)

```bash
# Pretty print
jq '.' data.json

# Extract field
jq '.name' data.json

# Extract nested field
jq '.user.email' data.json

# Array indexing
jq '.items[0]' data.json

# All array elements
jq '.items[]' data.json

# Filter array
jq '.items[] | select(.price > 100)' data.json

# Map array
jq '.items[] | {id, name}' data.json

# Array length
jq '.items | length' data.json

# Sort array
jq '.items | sort_by(.price)' data.json

# Group by
jq 'group_by(.category)' data.json

# Aggregate
jq '[.items[].price] | add' data.json       # Sum
jq '[.items[].price] | add / length' data.json  # Average

# Combine queries
jq '.users[] | select(.active == true) | {name, email}' data.json

# Modify field
jq '.price = .price * 1.1' data.json

# Add field
jq '. + {tax: .price * 0.2}' data.json

# Delete field
jq 'del(.password)' data.json

# Raw output (no quotes)
jq -r '.name' data.json

# Compact output
jq -c '.' data.json

# Multiple inputs
jq -s '.' file1.json file2.json  # Combine into array

# Read from stdin
curl -s https://api.example.com/data | jq '.results[]'
```

**jq Examples**:
```bash
# Extract all email addresses
jq -r '.users[].email' users.json

# Filter and format
jq -r '.users[] | select(.age > 18) | "\(.name) (\(.email))"' users.json

# Build CSV from JSON
jq -r '.[] | [.id, .name, .price] | @csv' data.json

# Count items by category
jq 'group_by(.category) | map({category: .[0].category, count: length})' data.json
```

### yq (YAML Query - Similar to jq)

```bash
# Convert YAML to JSON
yq eval -o=json data.yaml

# Extract field
yq eval '.name' data.yaml

# Modify YAML
yq eval '.version = "2.0"' -i config.yaml
```

---

## Advanced Text Processing

### Regular Expressions

**Basic Regex**:
| Pattern | Meaning |
|---------|---------|
| `.` | Any single character |
| `*` | Zero or more of previous |
| `+` | One or more of previous (ERE) |
| `?` | Zero or one of previous (ERE) |
| `^` | Start of line |
| `$` | End of line |
| `[abc]` | Character class (a, b, or c) |
| `[^abc]` | Negated class (not a, b, or c) |
| `[a-z]` | Range (any lowercase letter) |
| `\d` | Digit (PCRE) |
| `\w` | Word character (PCRE) |
| `\s` | Whitespace (PCRE) |

**Examples**:
```bash
# Match email addresses
grep -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' file.txt

# Match IP addresses
grep -E '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' file.txt

# Match phone numbers (US)
grep -E '\b[0-9]{3}-[0-9]{3}-[0-9]{4}\b' file.txt

# Match URLs
grep -E 'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' file.txt
```

### Combining Tools

```bash
# Extract unique IP addresses from logs
grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' access.log | sort -u

# Top 10 most common user agents
awk -F'"' '{print $6}' access.log | sort | uniq -c | sort -nr | head -10

# Find error types and count
grep "ERROR" app.log | awk '{print $5}' | sort | uniq -c | sort -nr

# Parse CSV, filter, format
cut -d',' -f1,3 data.csv | awk -F',' '$2 > 100 {print $1}'

# JSON API to formatted table
curl -s 'https://api.example.com/users' | \
  jq -r '.[] | [.id, .name, .email] | @tsv' | \
  column -t
```

---

## Real-World Examples

### Log Analysis

```bash
# Find all ERROR logs today
journalctl --since today | grep ERROR

# Count errors by hour
grep "ERROR" app.log | cut -d' ' -f1 | cut -d':' -f1 | sort | uniq -c

# Top 10 error messages
grep "ERROR" app.log | awk '{print $5,$6,$7}' | sort | uniq -c | sort -nr | head -10

# Find slow requests (> 1000ms)
awk '$NF > 1000 {print}' access.log
```

### System Administration

```bash
# List users with UID > 1000
awk -F':' '$3 > 1000 {print $1}' /etc/passwd

# Find large files in /var/log
find /var/log -type f -exec du -h {} + | sort -h | tail -20

# Check disk usage by directory
du -sh /var/* | sort -h

# Find listening ports with processes
ss -tulpen | grep LISTEN | awk '{print $5, $7}' | sort -u
```

### Data Processing

```bash
# Convert CSV to JSON
awk -F',' 'NR>1 {print "{\"name\":\""$1"\",\"age\":"$2",\"city\":\""$3"\"}"}' data.csv

# Pivot data
awk '{a[$1]+=$2} END {for (i in a) print i, a[i]}' data.txt

# Merge columns from multiple files
paste -d',' file1.csv file2.csv file3.csv
```

---

## Common Pitfalls

> [!warning] Forgetting to Sort Before uniq
> **Problem**: `uniq` only removes consecutive duplicates  
> **Wrong**: `cat file.txt | uniq`  
> **Correct**: `sort file.txt | uniq`

> [!warning] Using cat Unnecessarily (UUOC - Useless Use of Cat)
> **Problem**: Inefficient piping  
> **Wrong**: `cat file.txt | grep "error"`  
> **Correct**: `grep "error" file.txt`

> [!warning] Not Quoting Variables in Scripts
> **Problem**: Word splitting and globbing  
> **Wrong**: `grep $pattern file.txt`  
> **Correct**: `grep "$pattern" file.txt`

> [!warning] Modifying File While Reading
> **Problem**: `sed -i 's/old/new/g' file.txt` can cause issues in pipelines  
> **Solution**: Use temporary file or redirect to new file

> [!warning] Assuming Default Field Separator
> **Problem**: `awk '{print $2}'` on comma-delimited file prints entire line  
> **Solution**: Specify delimiter: `awk -F',' '{print $2}'`

> [!warning] Regex Greediness
> **Problem**: `sed 's/.*error.*/REDACTED/'` matches entire line  
> **Solution**: Use non-greedy patterns or be more specific

---

## Interview Corner

> [!question]- How do you find the top 10 most common IP addresses in an access log?
> ```bash
> awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10
> ```
> 
> **Breakdown**:
> 1. `awk '{print $1}'` - Extract 1st field (IP address)
> 2. `sort` - Sort IPs alphabetically
> 3. `uniq -c` - Count occurrences of each unique IP
> 4. `sort -nr` - Sort numerically, reverse (highest first)
> 5. `head -10` - Show top 10

> [!question]- Explain the difference between grep, sed, and awk
> - **grep**: Search/filter - finds lines matching pattern. Read-only.
> - **sed**: Stream editor - search and replace, delete lines, insert lines. Line-oriented.
> - **awk**: Pattern scanning and processing language - field extraction, calculations, complex logic. Field-oriented.
> 
> **When to use**:
> - **grep**: "Find all ERROR lines" → `grep ERROR log`
> - **sed**: "Replace all 'old' with 'new'" → `sed 's/old/new/g'`
> - **awk**: "Sum column 3 values" → `awk '{sum+=$3} END {print sum}'`

> [!question]- How do you remove duplicate lines from a file while preserving order?
> **Problem**: `sort | uniq` changes order
> 
> **Solutions**:
> ```bash
> # Method 1: awk (preserves order)
> awk '!seen[$0]++' file.txt
> 
> # Method 2: nl + sort + cut
> nl file.txt | sort -k2 -u | sort -n | cut -f2-
> ```

> [!question]- How do you extract the 2nd field from a CSV file that contains commas within quoted fields?
> **Problem**: Simple `cut -d',' -f2` breaks on `"Smith, John",42`
> 
> **Solution**: Use a proper CSV parser
> ```bash
> # Python one-liner
> python3 -c "import csv, sys; [print(row[1]) for row in csv.reader(sys.stdin)]" < data.csv
> 
> # Or use csvkit
> csvcut -c 2 data.csv
> ```

> [!question]- How would you find all files containing a specific string and replace it?
> ```bash
> # Method 1: grep + sed
> grep -rl "old_string" /path | xargs sed -i 's/old_string/new_string/g'
> 
> # Method 2: find + sed
> find /path -type f -exec sed -i 's/old_string/new_string/g' {} +
> 
> # Method 3: ripgrep + sd
> rg "old_string" --files-with-matches | xargs sd "old_string" "new_string"
> ```

> [!question]- Explain how to calculate the average of numbers in a column
> ```bash
> # Using awk
> awk '{sum+=$1} END {print sum/NR}' numbers.txt
> 
> # Breakdown:
> # sum+=$1 - Add each 1st field to sum
> # NR - Built-in variable: Number of Records (lines)
> # END - Execute after processing all lines
> ```

---

## Cheat Sheet

### Viewing
```bash
head -n 20 file.txt              # First 20 lines
tail -n 50 file.txt              # Last 50 lines
tail -f /var/log/syslog          # Follow file
less +F /var/log/syslog          # Follow in less
wc -l file.txt                   # Count lines
```

### Searching
```bash
grep "pattern" file.txt          # Search for pattern
grep -i "pattern" file.txt       # Case-insensitive
grep -r "pattern" /path          # Recursive search
grep -v "pattern" file.txt       # Invert match
rg "pattern"                     # Modern grep (ripgrep)
```

### Extracting
```bash
cut -d',' -f1,3 data.csv         # Extract CSV columns
awk '{print $1, $3}' file.txt    # Extract fields
awk -F',' '{print $2}' data.csv  # Custom delimiter
```

### Transforming
```bash
sed 's/old/new/g' file.txt       # Replace all
tr 'a-z' 'A-Z' < file.txt        # Uppercase
tr -s ' ' < file.txt             # Squeeze spaces
```

### Sorting
```bash
sort file.txt                    # Alphabetical sort
sort -n numbers.txt              # Numeric sort
sort -r file.txt                 # Reverse sort
sort -u file.txt                 # Unique sort
sort | uniq -c | sort -nr        # Count and sort
```

### JSON
```bash
jq '.' data.json                 # Pretty print
jq '.field' data.json            # Extract field
jq '.items[]' data.json          # Array elements
jq '.items[] | select(.price > 100)' data.json  # Filter
```

---

## References

### Official Documentation
- [grep(1) Manual](https://man7.org/linux/man-pages/man1/grep.1.html)
- [sed(1) Manual](https://man7.org/linux/man-pages/man1/sed.1.html)
- [awk(1) Manual](https://man7.org/linux/man-pages/man1/awk.1p.html)
- [jq Manual](https://stedolan.github.io/jq/manual/)

### Tutorials and Guides
- [The AWK Programming Language](https://www.amazon.com/AWK-Programming-Language-Alfred-Aho/dp/020107981X)
- [Sed & awk (O'Reilly)](https://www.amazon.com/sed-awk-Dale-Dougherty/dp/1565922255)
- [Regular-Expressions.info](https://www.regular-expressions.info/)
- [Regex101](https://regex101.com/) - Online regex tester

### Modern Alternatives
- [ripgrep](https://github.com/BurntSushi/ripgrep) - Fast grep alternative
- [sd](https://github.com/chmln/sd) - Intuitive sed alternative
- [fd](https://github.com/sharkdp/fd) - Fast find alternative
- [bat](https://github.com/sharkdp/bat) - Cat with syntax highlighting

---

## Related Notes

- [[01_Linux_Command_Line]] - Shell basics and piping
- [[03_Processes_and_Jobs]] - Process management for text processing tasks
- [[03_Networking_Tools]] - Parsing network logs and output
- [[01_Performance_Tuning]] - Optimizing text processing performance

---

> [!tip] Best Practices
> 1. **Avoid UUOC**: Don't use `cat file | grep` when `grep file` works
> 2. **Quote variables**: Always use `"$var"` not `$var` in scripts
> 3. **Sort before uniq**: `uniq` only removes consecutive duplicates
> 4. **Test regex**: Use online tools like regex101.com to test patterns
> 5. **Use specific tools**: grep for searching, sed for replacing, awk for field processing
> 6. **Backup before in-place edits**: `sed -i.bak` creates backup
> 7. **Prefer modern tools**: ripgrep > grep, jq > manual JSON parsing
> 8. **Keep raw data**: Pipe into tools rather than modifying original files
