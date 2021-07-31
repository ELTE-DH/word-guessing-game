all: download filter count ballance venv sample

download:
	# about 26 minutes
	mkdir -p orig && cd orig && ../download.sh && sha256sum -c sha256sums

filter:
	# Filter sentences which are at least 11 and maximum 50 words long
	# Do not contain words longer than 25 character
	# Do not contain three or more consecutive words starting with uppercase letter (proper names)
	# Do not contain two at least four character long words fully uppercased in any position (shouting)
	# Do not contain three consecutive non-alphanumeric words (single line pattern)
	# Do not contain three consecutive one-letter word (typewriter style)
	# Do not contain three or more backslash (\) character (bad escaping)
	# Do not contain replacement character (�)
	# Do not contain o with tilde (õ) instead ő and u with circumflex (û) instead of ű (encoding problem)
	# Do not contain HTML escapes (&lt;,&gt;&#12345;)
	./filter_corpus.sh
	echo "172c600756626b619b37391ceff1438b4da488925c4e83c3d3caa7def2bf5dba filter_final.txt.gz" | sha256sum -c - || exit 1
	# about 213 minutes
	# Sentences: 199 627 769
	# Words: 4 036 428 503

count: filter_final.txt.gz
	# Count lines and filter rare (<30) words
	# 1. Create concordances in parallel (only minimum 4 long words with lowercase alphabetic characters
	#	 recognised by emMorph i.e. not in the non-words set)
	# 2. sort entries
	# 3. Uniq based on the 2nd and 3rd fields
	# 4. Count lines (as uniq -c) based on the first field (TAB separated) and print only groups larger than
	#	 the specified limit (default: 30)
	export LC_ALL="C.UTF-8" && pigz -cd filter_final.txt.gz | parallel --pipe 'python3 create_conc.py'| \
	sort --parallel=$$(nproc) -T ~/tmp -S10% --compress-program=pigz | ./uniq_2nd_field.sh | ./uniq_3rd_field.sh | \
	 ./uniq_c_1st_field.sh | pigz -n > conc_filtered.txt.gz
	 echo "b906f2894787bd9fcb95a866457e4625206796ea18238eb80884a0948a67908f conc_filtered.txt.gz" | sha256sum -c - || \
	  exit 1
	# about 118 minutes
	# Words (to be guessed): 653 813
	# Concordances: 923 223 804

ballance: conc_filtered.txt.gz
	# Select 30 random concordances for each word to ballance frequent and rare words
	export LC_ALL="C.UTF-8" && pigz -cd conc_filtered.txt.gz | python3 random_select.py | pigz -n > sampled_concs.txt.gz
	echo "dd1bf2abbd0678123755caf51dc9d4f91b4623f4a9fb74eb3adf02eea128eecf sampled_concs.txt.gz" | sha256sum -c - || exit 1
	# about 18 minutes
	# Words (to be guessed): 653 813
	# Concordances: 19 614 390

venv:
	virtualenv -p python3 venv
	./venv/bin/pip install sqlalchemy

sample: ./venv/bin/pip sampled_concs.txt.gz
	# Sample from the ballanced dataset for portability
	export LC_ALL="C.UTF-8" && rm -rf webcorpus_conc.db  && pigz -cd sampled_concs.txt.gz | \
	 python3 random_sampling_filter.py | ./venv/bin/python3 create_sqldb.py -f webcorpus_conc.db
	# Words (to be guessed): 8 000
	# Concordances: 240 000
	# about a few minutes
	# DB size: about 30 MB

PrevCons.sqlite3:
	wget https://github.com/kagnes/prevcons/raw/master/PrevCons.sqlite3

prevcons: PrevCons.sqlite3 venv
	# Requires the database file (PrevCons.sqlite3) and the virtualenv (venv) to be created
	export LC_ALL="C.UTF-8" && ./venv/bin/python3 filter_prevcons.py | \
	 sort --parallel=$$(nproc) -T ~/tmp -S10% --compress-program=pigz | \
	 ./uniq_2nd_field.sh | ./uniq_3rd_field.sh | ./venv/bin/python3 create_sqldb.py -f prevcons_conc.db
	echo 'Database succesfully created! (The errors above were not fatal.)'
	# Words (to be guessed): 122
	# Concordances: 15 816
	# less than a minute
	# DB size: 1,4 MB

clean:
	rm -rf orig *.txt.gz *.db PrevCons.sqlite3
