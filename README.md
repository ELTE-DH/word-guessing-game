# Word Guessing Game

A [Cloze test-like](https://en.wikipedia.org/wiki/Cloze_test) game based on
 the idea of the "Nyelvi Játék" by [MorphoLogic Kft.](https://www.morphologic.hu/) on a new, different code base.

A sample instance is running at: https://word-concordance-game.onrender.com/

# Installation

The required minimum Python version is 3.6.

1. Clone the repository
2. `pip install -r requirements.txt`
3. Setup the database in [`config.yaml`](config.yaml) (`database_name` key in `db_config`)
4. `python main.py`

# Recreating the database

1. `cd create_database`
2. `make webcorpus1` XOR `make webcorpus2`
3. Setup the database in [`config.yaml`](config.yaml) (`database_name` key in `db_config`)

# License

This project is licensed under the terms of the GNU LGPL 3.0 license.

# Acknowledgement

The authors gratefully acknowledge the groundbreaking work of all pioneers who inspired this program. <br>
We wish to thank to the employees of _MorphoLogic Kft.__ who created this program. <br>
We also thank to the publishers of both Webcorpus versions for making their corpus publicly available.

# References

If you use this program, please cite the following paper:

[Indig, B. and Lévai, D. (2022). __Okosabb vagy, mint egy XXXXXXXX? – egy nyelvi játéktól a nyelvmodellek összehasonlı́tásáig__. In Gábor Berend, et al., editors, _XVIII. Magyar Számı́tógépes Nyelvészeti Konferencia_, pages 31--44 Szeged, Hungary](https://rgai.inf.u-szeged.hu/sites/rgai.inf.u-szeged.hu/files/mszny2022.pdf)

```
@inproceedings{word-guessing-mszny2022,
    author = {Indig, Balázs and Lévai, Dániel},
    booktitle = {{XVIII}. {M}agyar {S}zámítógépes {N}yelvészeti {K}onferencia},
    title = {Okosabb vagy, mint egy {XXXXXXXX}? -- Egy nyelvi játéktól a nyelvmodellek összehasonlításáig},
    year = {2022},
    editor = {Gábor Berend and Gábor Gosztolya and Veronika Vincze},
    pages = {31--44},
    orcid-numbers = {Indig, Balázs/0000-0001-8090-3661}
}
```
